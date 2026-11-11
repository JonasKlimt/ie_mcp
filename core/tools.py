"""
MCP tools registration.

All tools are registered onto the FastMCP instance via register_tools().
Tools use the PackageRegistry for package metadata, the target environment for
installed versions and source files, and the local cache for fetched docs and
releases. Every tool runs in a worker thread so a slow download never blocks the
server, and real failures are raised as ToolError (reported with isError=true).
"""

from __future__ import annotations

import difflib
import functools
import inspect
import sys
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from typing import Any

import anyio.to_thread
import httpx
from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.exceptions import ToolError
from mcp.types import ToolAnnotations

from . import changelog, docs_discovery, pypi, source_lookup
from .cache import get_or_fetch_page, refresh_page
from .config import setting
from .docs_provenance import docs_provenance, with_docs_header
from .docs_search import chunk_markdown, rank_chunks
from .environment import (
    SERVER_ORIGIN,
    TargetEnvironmentError,
    environment_fields,
    inspect_environment,
    normalize_version,
    python_override,
    register_names,
    select_environment_hint,
    select_target_python,
)
from .github import list_tags
from .readthedocs import list_versions
from .registry import PackageRegistry

MAX_LISTED_VERSIONS = int(setting("limits", "max_listed_versions"))
RATE_LIMIT_STATUSES = (403, 429)


def _version_not_supported_warning(package: str) -> str:
    """Build the message for packages whose docs exist only as 'latest'.

    Args:
        package: Package name as returned by list_packages().

    Returns:
        The warning text.
    """
    return (
        f"⚠️ Versioned documentation is not available for '{package}'. "
        f"Its documentation URLs do not follow the standard ReadTheDocs versioning "
        f"pattern (/en/{{version}}/), so older versions cannot be accessed. "
        f"Only the current (latest) documentation is available."
    )


def _annotations(title: str, open_world: bool, read_only: bool = True) -> ToolAnnotations:
    """Describe a tool to the client, so safe tools can run without a prompt.

    Args:
        title: Human-readable tool name.
        open_world: True if the tool may contact the internet.
        read_only: False only for the tool that changes the server's own state.

    Returns:
        The annotations of the tool.
    """
    return ToolAnnotations(
        title=title,
        readOnlyHint=read_only,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=open_world,
    )


def _network_message(exc: httpx.HTTPError) -> str:
    """Write a short message for a failed download.

    Args:
        exc: The error raised by httpx.

    Returns:
        The message, with a token hint for GitHub rate limits and rejected tokens.
    """
    message = f"Network error: {exc}"
    response = getattr(exc, "response", None)
    status = getattr(response, "status_code", None)
    if status in RATE_LIMIT_STATUSES:
        message += (
            " (a rate limit may be the cause; a GITHUB_TOKEN raises GitHub's limit from 60 to "
            "5000 requests per hour, see the README section 'GitHub token')"
        )
    elif status == 401 and response.request.url.host == "api.github.com":
        message += " (GitHub rejected the GITHUB_TOKEN: it is invalid, expired or revoked)"
    return message


def _threaded(fn: Callable[..., Any], per_call_python: bool) -> Callable[..., Any]:
    """Make a tool run in a worker thread and report failures as ToolError.

    The wrapper keeps the signature and docstring of the tool. If the tool has a
    python_executable argument, that interpreter is inspected for this call only.

    Args:
        fn: The synchronous tool function.
        per_call_python: True if the python_executable argument selects an interpreter.

    Returns:
        An async function that FastMCP registers in place of the tool.
    """
    signature = inspect.signature(fn)

    def call(*args: Any, **kwargs: Any) -> Any:
        python = signature.bind(*args, **kwargs).arguments.get("python_executable")
        try:
            with python_override(python if per_call_python else None):
                return fn(*args, **kwargs)
        except TargetEnvironmentError as exc:
            raise ToolError(str(exc)) from exc
        except httpx.HTTPError as exc:
            raise ToolError(_network_message(exc)) from exc

    @functools.wraps(fn)
    async def wrapper(*args: Any, **kwargs: Any) -> Any:
        return await anyio.to_thread.run_sync(functools.partial(call, *args, **kwargs))

    return wrapper


def _raise_on_error(result: dict[str, Any]) -> dict[str, Any]:
    """Turn the "error" entry of a lookup result into a ToolError.

    Args:
        result: Result of a source lookup.

    Returns:
        The result itself if it holds no error.

    Raises:
        ToolError: If the result has an "error" entry.
    """
    if "error" in result:
        raise ToolError(str(result["error"]))
    return result


def _page_window(text: str, max_chars: int | None, offset: int) -> str:
    """Cut a long page into a window and say how to read on.

    Args:
        text: The full page.
        max_chars: Window size; default limits.doc_page_chars.
        offset: Character position the window starts at.

    Returns:
        The page if it fits, else the window with a note that names the next offset.
    """
    size = max_chars if max_chars and max_chars > 0 else int(setting("limits", "doc_page_chars"))
    start = min(max(offset, 0), len(text))
    end = min(start + size, len(text))
    if start == 0 and end == len(text):
        return text
    parts = [text[start:end]]
    if start:
        parts.insert(0, f"[Continuing at character {start} of {len(text)}.]\n")
    if end < len(text):
        parts.append(f"\n[Cut at character {end} of {len(text)}. Call again with offset={end}.]")
    return "\n".join(parts)


def _short_description(text: str, limit: int) -> str:
    """Shorten a package description to its first sentence.

    Args:
        text: Full description.
        limit: Maximum length of the result.

    Returns:
        The first sentence, cut with an ellipsis if it is longer than the limit.
    """
    sentence = text.split(". ")[0].strip().rstrip(".")
    return sentence if len(sentence) <= limit else sentence[: limit - 1].rstrip() + "…"


def register_tools(mcp: FastMCP, registry: PackageRegistry) -> None:
    """Register all tools on the MCP server.

    Args:
        mcp: The server to register the tools on.
        registry: Registry with the metadata of all known packages.
    """
    pypi_names = {key: registry.pypi_name(key) for key in registry.list_packages()}
    register_names(list(pypi_names.values()))

    def tool(
        title: str, open_world: bool = False, selects_python: bool = False
    ) -> Callable[[Callable[..., Any]], Any]:
        """Register a function as an MCP tool with annotations and a worker thread.

        Args:
            title: Human-readable tool name.
            open_world: True if the tool may contact the internet.
            selects_python: True for the tool that sets the server-wide interpreter.

        Returns:
            A decorator for the tool function.
        """

        def decorate(fn: Callable[..., Any]) -> Any:
            annotations = _annotations(title, open_world, read_only=not selects_python)
            wrapped = _threaded(fn, per_call_python=not selects_python)
            return mcp.tool(title=title, annotations=annotations)(wrapped)

        return decorate

    def _meta(package: str) -> dict[str, Any]:
        """Return the metadata of a package.

        Args:
            package: Package name as returned by list_packages().

        Returns:
            The package metadata.

        Raises:
            ToolError: If the package is not registered; the message suggests close names.
        """
        meta = registry.get_metadata(package)
        if meta is None:
            close = difflib.get_close_matches(package, registry.list_packages(), n=5, cutoff=0.5)
            hint = f" Did you mean: {', '.join(close)}?" if close else ""
            raise ToolError(
                f"Unknown package '{package}'.{hint} Call list_packages() to see all packages."
            )
        return meta

    def _docs_provenance(package: str, docs_version: str) -> dict[str, Any]:
        """Describe the docs version used for a package next to the installed one.

        Args:
            package: Package name as returned by list_packages().
            docs_version: Docs version slug that was read.

        Returns:
            Dict with docs_version, installed_version and an optional warning.
        """
        return docs_provenance(pypi_names[package], docs_version)

    def _doc_pages(package: str, version: str) -> list[dict[str, Any]]:
        """List the documentation pages of a package: curated sections, then discovered pages.

        Args:
            package: Package name as returned by list_packages().
            version: Docs version slug.

        Returns:
            Dicts with id, title, url and curated (True for hand-written sections).
        """
        sections = _meta(package).get("sections", [])
        curated = [
            {
                "id": section["id"],
                "title": section["title"],
                "url": registry.get_section_url(package, section["id"], version),
            }
            for section in sections
        ]
        found = docs_discovery.discover_pages(package, curated, version)
        return [{**p, "curated": True} for p in curated] + [{**p, "curated": False} for p in found]

    def _find_page(package: str, section: str, version: str) -> dict[str, Any]:
        """Find one documentation page by section id.

        Curated sections are looked up without any network access; the other pages
        of the docs site are looked up only if the id is not a curated section.

        Args:
            package: Package name as returned by list_packages().
            section: Section or page id.
            version: Docs version slug.

        Returns:
            Dict with id, title and url.

        Raises:
            ToolError: If the package has no such page.
        """
        info = registry.get_section_info(package, section)
        if info is not None:
            url = registry.get_section_url(package, section, version)
            return {"id": section, "title": info["title"], "url": url}
        for page in _doc_pages(package, version):
            if page["id"] == section:
                return page
        curated = ", ".join(registry.get_sections(package))
        raise ToolError(
            f"Section '{section}' not found for package '{package}'. "
            f"Curated sections: {curated}. list_doc_sections('{package}') lists all pages."
        )

    def _load_pages(
        package: str, pages: list[dict[str, Any]], version: str
    ) -> tuple[dict[str, str], list[dict[str, str]]]:
        """Read several docs pages, downloading the missing ones in parallel.

        Args:
            package: Package name as returned by list_packages().
            pages: Pages with id and url.
            version: Docs version slug.

        Returns:
            The Markdown of every page that could be read (by id), and the pages that failed.
        """

        def load(page: dict[str, Any]) -> tuple[str, str, str | None]:
            try:
                content, _ = get_or_fetch_page(package, page["id"], page["url"], version)
                return page["id"], content, None
            except (httpx.HTTPError, OSError) as exc:
                return page["id"], "", str(exc)

        with ThreadPoolExecutor(max_workers=int(setting("workers", "docs"))) as pool:
            loaded = list(pool.map(load, pages))
        texts = {page_id: content for page_id, content, error in loaded if error is None}
        failed = [{"section": page_id, "error": error} for page_id, _, error in loaded if error]
        return texts, failed

    # ------------------------------------------------------------------
    # Environment inspection tools
    # ------------------------------------------------------------------

    @tool("Get installed package version")
    def get_installed_package_version(
        package: str, python_executable: str | None = None
    ) -> dict[str, Any]:
        """
        Check what version of a package is installed in the target Python
        environment (the user's research environment).

        The target is the interpreter chosen with set_python_environment, else a
        configured or detected one. The result names the interpreter and where it
        came from, so you and the user can verify it.

        Call this first when the user has not mentioned a version.

        Args:
            package: Package name as returned by list_packages().
            python_executable: Optional. Python of another project, for this call only.

        Returns:
            Dict with package, pypi_name, installed_version (null if not installed),
            python_executable, python_executable_origin and status ("installed" or
            "not_installed", the latter with a message). An unreadable environment
            is reported as a tool error.
        """
        _meta(package)
        pypi_name = pypi_names[package]
        environment = environment_fields(pypi_name)
        if "environment_error" in environment:
            raise ToolError(environment["environment_error"])
        result = {"package": package, "pypi_name": pypi_name, **environment}
        if environment["installed_version"] is None:
            message = source_lookup.not_installed_message(pypi_name, environment)
            return {**result, "status": "not_installed", "message": message}
        return {**result, "status": "installed"}

    def _environment_report(refresh: bool) -> dict[str, Any]:
        """Describe the inspected environment and its registered packages.

        Args:
            refresh: Read the environment again instead of using cached results.

        Returns:
            The result of get_server_environment.

        Raises:
            TargetEnvironmentError: If the interpreter cannot be inspected.
        """
        environment = inspect_environment(sorted(set(pypi_names.values())), refresh=refresh)
        versions = environment.pop("versions")
        installed = {key: versions[name] for key, name in pypi_names.items() if versions[name]}
        report = {
            **environment,
            "server_python_executable": sys.executable,
            "packages": installed,
            "not_installed_count": len(pypi_names) - len(installed),
        }
        if environment["python_executable_origin"] == SERVER_ORIGIN:
            report["hint"] = (
                "This is the server's own Python, not a detected user environment. "
                + select_environment_hint()
            )
        return report

    @tool("Set Python environment", selects_python=True)
    def set_python_environment(python_executable: str) -> dict[str, Any]:
        """
        Choose the Python environment of the user's project. All other tools then
        read installed versions and source code from it.

        Call this at the start of a task with the interpreter of the file, notebook
        or project the user works on: the selected interpreter or kernel, or the
        output of `python -c "import sys; print(sys.executable)"` run in the
        project's environment. If you cannot find it, ask the user which
        environment to use. Call it again when the user switches projects.

        The choice lasts until the server restarts. Nothing is installed or
        imported; the environment is only read. Only files named like a Python
        interpreter are accepted.

        Args:
            python_executable: Full path of the python executable, or the root
                               folder of a venv or conda environment.

        Returns:
            Same as get_server_environment for the chosen environment. A path
            without a Python is reported as a tool error.
        """
        select_target_python(python_executable)
        return _environment_report(refresh=True)

    @tool("Inspect Python environment")
    def get_server_environment(
        refresh: bool = False, python_executable: str | None = None
    ) -> dict[str, Any]:
        """
        Inspect the target Python environment (the user's research environment).

        Returns the inspected interpreter, where it came from
        (python_executable_origin: set_python_environment, IE_MCP_TARGET_PYTHON,
        an active or project environment, or the server's own sys.executable),
        its Python version, and the installed version of every registered package
        that is installed. Packages that are not listed are not installed
        (not_installed_count tells how many).

        If this is not the environment of the user's file or project, call
        set_python_environment with the right interpreter.

        Installed versions are cached while the server runs. Pass refresh=True
        after the user installed or upgraded packages.

        Args:
            refresh: Read the environment again instead of using cached results.
            python_executable: Optional. Python of another project, for this call only.

        Returns:
            Dict with python_executable, python_executable_origin, python_version,
            server_python_executable, packages (installed ones mapped to their
            version) and not_installed_count, plus a hint if no user environment
            was found.
        """
        return _environment_report(refresh)

    # ------------------------------------------------------------------
    # Discovery tools
    # ------------------------------------------------------------------

    def _installed_versions(required: bool) -> dict[str, str | None]:
        """Read the installed version of every registered package.

        Args:
            required: True to raise if the environment cannot be read.

        Returns:
            Distribution name mapped to its version or None; empty if unreadable.

        Raises:
            TargetEnvironmentError: If required and the environment cannot be read.
        """
        try:
            return inspect_environment(sorted(set(pypi_names.values())))["versions"]
        except TargetEnvironmentError:
            if required:
                raise
            return {}

    @tool("List packages")
    def list_packages(
        installed_only: bool = False, python_executable: str | None = None
    ) -> list[dict[str, Any]]:
        """
        List all Python packages that this MCP server has documentation for, each
        with a one-line description and the version installed in the target
        environment (null if not installed).

        Args:
            installed_only: Only list packages that are installed in the target
                            environment.
            python_executable: Optional. Python of another project, for this call only.

        Returns:
            One dict per package with package (the key usable in every other tool),
            description and installed_version (left out if the environment cannot
            be read).
        """
        versions = _installed_versions(required=installed_only)
        limit = int(setting("limits", "package_description_chars"))
        items = []
        for key, name in pypi_names.items():
            if installed_only and not versions.get(name):
                continue
            item: dict[str, Any] = {
                "package": key,
                "description": _short_description(registry.get_metadata(key)["description"], limit),
            }
            if versions:
                item["installed_version"] = versions[name]
            items.append(item)
        return items

    @tool("Get package info")
    def get_package_info(package: str) -> dict[str, Any]:
        """
        Get metadata for a package: description, GitHub URL, docs URL, install
        commands, and the list of curated documentation sections. Use
        list_doc_sections for every page of the docs site.

        Args:
            package: Package name as returned by list_packages().

        Returns:
            The package metadata plus available_sections.
        """
        meta = _meta(package)
        return {**meta, "available_sections": registry.get_sections(package)}

    @tool("List documentation versions", open_world=True)
    def list_doc_versions(package: str) -> list[str]:
        """
        List all available documentation versions for a package.

        Queries the ReadTheDocs API to discover published versions.
        Always call this before the docs tools when the user asks about a
        specific version other than the latest.

        Args:
            package: Package name as returned by list_packages().

        Returns:
            List of docs version slugs ('latest' and 'stable' first).
        """
        slug = _meta(package).get("readthedocs_slug")
        if not slug:
            raise ToolError(f"No ReadTheDocs slug registered for '{package}'.")
        return list_versions(slug)

    # ------------------------------------------------------------------
    # Cached/live docs tools
    # ------------------------------------------------------------------

    @tool("List documentation sections", open_world=True)
    def list_doc_sections(package: str, version: str = "latest") -> dict[str, Any]:
        """
        List the pages of a package's documentation: the curated sections and the
        other pages found on the docs site (for example one page per module).
        Use the id with get_doc_section.

        Args:
            package: Package name as returned by list_packages().
            version: Docs version slug (default: 'latest').

        Returns:
            Dict with package, docs_version and sections (id, title, curated).
        """
        _meta(package)
        if version != "latest" and not registry.supports_versioning(package):
            return {"package": package, "message": _version_not_supported_warning(package)}
        pages = _doc_pages(package, version)
        sections = [{k: page[k] for k in ("id", "title", "curated")} for page in pages]
        return {"package": package, "docs_version": version, "sections": sections}

    @tool("Read documentation section", open_world=True)
    def get_doc_section(
        package: str,
        section: str,
        version: str = "latest",
        max_chars: int | None = None,
        offset: int = 0,
        python_executable: str | None = None,
    ) -> str:
        """
        Return the Markdown content of a documentation page.

        The first call fetches the live docs page and caches it locally. Later
        calls are served from the cache until it is a few days old.

        The text starts with a short header that states the docs version used
        (docs_version) and the installed version of the package. If they differ,
        the header has a warning: check signatures with get_function_source and
        tell the user about the mismatch.

        Long pages are cut at max_chars; the note at the end names the offset to
        continue with. Defaults to the latest docs. Call list_doc_versions(package)
        first if the user asks about a specific older version.

        Args:
            package: Package name as returned by list_packages().
            section: Section id from get_package_info or list_doc_sections.
            version: Docs version slug (default: 'latest').
            max_chars: Size of the part to return (default: 20000 characters).
            offset: Character position to start at, to read on in a long page.
            python_executable: Optional. Python of another project, for this call only.

        Returns:
            Markdown text: a header with docs_version, installed_version and an optional
            warning, then the page (or the requested part of it).
        """
        _meta(package)
        if version != "latest" and not registry.supports_versioning(package):
            return _version_not_supported_warning(package)
        page = _find_page(package, section, version)
        content, _ = get_or_fetch_page(package, page["id"], page["url"], version)
        shown = _page_window(content, max_chars, offset)
        return with_docs_header(shown, _docs_provenance(package, version))

    @tool("Search documentation", open_world=True)
    def search_docs(
        package: str, query: str, version: str = "latest", python_executable: str | None = None
    ) -> dict[str, Any]:
        """
        Search the package documentation and return the best-matching paragraphs.

        All pages of the docs (curated sections and the other pages of the site)
        are searched; missing pages are fetched and cached first. Paragraphs are
        ranked by how well they match the words of the query, best first.

        Defaults to the latest docs. Call list_doc_versions(package) first
        if the user asks about a specific older version.

        Args:
            package: Package name as returned by list_packages().
            query: Free-text search query, e.g. 'contribution analysis'.
            version: Docs version slug (default: 'latest').
            python_executable: Optional. Python of another project, for this call only.

        Returns:
            Dict with package, docs_version, installed_version, an optional warning and
            matches (section, heading, snippet, score). Pages that could not be
            downloaded are listed in skipped_pages; message says if nothing matched.
        """
        _meta(package)
        if version != "latest" and not registry.supports_versioning(package):
            return {"package": package, "warning": _version_not_supported_warning(package)}
        pages = _doc_pages(package, version)
        if not pages:
            return {"message": f"No documentation manifest found for '{package}'."}

        texts, failed = _load_pages(package, pages, version)
        chunks = [
            c for page in pages for c in chunk_markdown(page["id"], texts.get(page["id"], ""))
        ]
        ranked = rank_chunks(chunks, query, int(setting("limits", "max_doc_matches")))
        snippet_chars = int(setting("limits", "doc_snippet_chars"))
        matches = [
            {
                "section": chunk.section,
                "heading": chunk.heading,
                "snippet": chunk.text[:snippet_chars]
                + ("…" if len(chunk.text) > snippet_chars else ""),
                "score": round(score, 2),
            }
            for score, chunk in ranked
        ]
        result: dict[str, Any] = {
            "package": package,
            **_docs_provenance(package, version),
            "matches": matches,
        }
        if not matches:
            result["message"] = f"No results found for '{query}' in '{package}' ({version})."
        if failed:
            result["skipped_pages"] = failed
        return result

    # ------------------------------------------------------------------
    # Source tools: installed files first, then PyPI, then GitHub
    # ------------------------------------------------------------------

    @tool("Search source code", open_world=True)
    def search_source(
        package: str, query: str, version: str | None = None, python_executable: str | None = None
    ) -> dict[str, Any]:
        """
        Search the source code of a package for a text string (like grep).

        Without a version, or with the installed version, the installed files in
        the target environment are searched. Another version is downloaded from
        PyPI and searched; versions that are not on PyPI (e.g. 'HEAD') are read
        from GitHub at that exact tag or branch.

        Returns up to 20 matching lines with file, line and text. The result states
        its source ("local", "pypi" or "github"), version, installed_version and
        python_executable once; files of the installed package are relative to root.

        If the package is not installed and no version is given, the result has
        status "not_installed": ask the user before using version="latest".

        Args:
            package: Package name as returned by list_packages().
            query: Search string (e.g. function name, class name, keyword).
            version: Optional version (e.g. '2.1.0', 'v2.1.0', 'latest', 'HEAD').
                     Omit to search the installed version.
            python_executable: Optional. Python of another project, for this call only.

        Returns:
            Dict with source, version, installed_version, python_executable, root
            (installed files only) and matches (file, line, text); or a dict with a
            message or status.
        """
        meta = _meta(package)
        return _raise_on_error(source_lookup.search_source(package, meta, query, version))

    @tool("List source versions", open_world=True)
    def list_source_versions(package: str, python_executable: str | None = None) -> dict[str, Any]:
        """
        List the available versions of a package: releases on PyPI and tags on
        GitHub, newest first, plus the version installed in the target environment.

        Use this when the user asks about a specific version, to confirm it exists
        before calling get_function_source. Versions on PyPI are preferred; GitHub
        tags matter for versions that were never released on PyPI.

        Args:
            package: Package name as returned by list_packages().
            python_executable: Optional. Python of another project, for this call only.

        Returns:
            Dict with pypi_versions, github_tags, installed_version and python_executable.
            If one source fails, pypi_error or github_error replaces its list.
        """
        meta = _meta(package)
        pypi_name = pypi_names[package]
        result: dict[str, Any] = {"package": package, **environment_fields(pypi_name)}
        try:
            result["pypi_versions"] = pypi.list_versions(pypi_name)[:MAX_LISTED_VERSIONS]
        except Exception as exc:  # noqa: BLE001
            result["pypi_error"] = f"PyPI error: {exc}"
        github_repo = meta.get("github_repo")
        if not github_repo:
            result["github_error"] = f"No GitHub repository registered for '{package}'."
            return result
        try:
            result["github_tags"] = list_tags(github_repo)[:MAX_LISTED_VERSIONS]
        except Exception as exc:  # noqa: BLE001
            result["github_error"] = f"GitHub API error: {exc}"
        return result

    @tool("Get function source", open_world=True)
    def get_function_source(
        package: str,
        function_name: str,
        version: str | None = None,
        detail: str = "full",
        python_executable: str | None = None,
    ) -> dict[str, Any]:
        """
        Return a function, method or class of a package: signature, docstring
        and code, read from the exact version in question.

        Without a version, or with the installed version, the code is read from
        the installed files in the target environment (source "local"). Another
        version is downloaded from PyPI (source "pypi"); GitHub (source "github")
        is only used for versions that are not on PyPI, such as 'HEAD'.

        Every result states source, version, installed_version, file and
        python_executable. Always tell the user which version and source an
        answer is based on.

        If several definitions match a plain name (e.g. methods with the same
        name in different classes), the result lists all of them with signature
        and docstring but without code; call again with 'Class.method'.

        If the package is not installed and no version is given, the result has
        status "not_installed": ask the user before using version="latest". If the
        name does not exist in that version, the status is "not_found".

        Args:
            package:       Package name as returned by list_packages().
            function_name: Name of a function ('lci'), method ('LCA.lci') or
                           class ('LCA'). Module prefixes are allowed
                           ('lca.LCA.lci').
            version:       Optional version (e.g. '2.1.0', 'v2.1.0', 'latest',
                           'HEAD'). Omit to use the installed version.
            detail:        'full' (default) returns signature, docstring and code;
                           'signature' leaves the code out to save tokens.
            python_executable: Optional. Python of another project, for this call only.

        Returns:
            Dict with function, qualified_name, kind, file, line, signature, docstring,
            code (detail 'full'), methods (classes), source, version,
            installed_version and python_executable. With several matches: matches
            and match_count instead. Otherwise a dict with status and message.
        """
        meta = _meta(package)
        result = source_lookup.get_function_source(package, meta, function_name, version, detail)
        return _raise_on_error(result)

    @tool("Fetch fresh documentation", open_world=True)
    def fetch_latest_docs(
        package: str,
        section: str | None = None,
        version: str = "latest",
        max_chars: int | None = None,
        offset: int = 0,
        python_executable: str | None = None,
    ) -> str:
        """
        Force-fetch documentation for a package directly from the web, bypassing
        the local cache. Use this when the user wants the most up-to-date content
        or when cached content may be stale.

        The fetched page is written to the local cache so later calls are fast.
        Fetches a specific page if given, otherwise the docs homepage. Long pages
        are cut like in get_doc_section (max_chars, offset).

        The text starts with a short header that states the docs version used
        and the installed version of the package, with a warning if they differ.

        Args:
            package: Package name as returned by list_packages().
            section: Optional section id (e.g. 'introduction', 'faq') or a page id
                     from list_doc_sections. Leave empty to fetch the docs homepage.
            version: Docs version slug (default: 'latest').
            max_chars: Size of the part to return (default: 20000 characters).
            offset: Character position to start at, to read on in a long page.
            python_executable: Optional. Python of another project, for this call only.

        Returns:
            Markdown text: a header with docs_version, installed_version and an optional
            warning, then the page.
        """
        meta = _meta(package)
        if version != "latest" and not registry.supports_versioning(package):
            return _version_not_supported_warning(package)
        if section:
            page = _find_page(package, section, version)
            page_id, url = page["id"], page["url"]
        else:
            page_id = "index"
            url = registry.get_section_url(package, "index", version) or meta["docs_url"]
        content = refresh_page(package, page_id, url, version)
        shown = _page_window(content, max_chars, offset)
        return with_docs_header(shown, _docs_provenance(package, version))

    @tool("Get changelog", open_world=True)
    def get_changelog(
        package: str,
        from_version: str | None = None,
        to_version: str | None = None,
        python_executable: str | None = None,
    ) -> dict[str, Any]:
        """
        Show what changed between versions of a package: release notes from GitHub
        releases, or from the changelog file of the repository if it has no releases.

        Without from_version the changes after the installed version are shown, up
        to the latest release; if the package is not installed, the latest releases.
        Use it for "what is new", "what broke in version X" and migration questions.

        Args:
            package: Package name as returned by list_packages().
            from_version: Show releases newer than this version (exclusive).
            to_version: Show releases up to and including this version.
            python_executable: Optional. Python of another project, for this call only.

        Returns:
            Dict with source ("github_releases" or "changelog_file"), releases
            (version, date, notes), from_version, to_version, installed_version and
            python_executable; a message if nothing was found.
        """
        meta = _meta(package)
        github_repo = meta.get("github_repo")
        if not github_repo:
            raise ToolError(f"No GitHub repository registered for '{package}'.")
        environment = environment_fields(pypi_names[package])
        lower = normalize_version(from_version) or environment["installed_version"]
        upper = normalize_version(to_version)
        found = changelog.build_changelog(
            github_repo, lower, upper, environment["installed_version"]
        )
        return {
            "package": package,
            "github_repo": github_repo,
            "from_version": lower,
            "to_version": upper,
            **environment,
            **found,
        }
