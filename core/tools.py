"""
MCP tools registration.

All tools are registered onto the FastMCP instance via register_tools().
Tools use the PackageRegistry for package metadata, the target environment for
installed versions and source files, and the local cache for fetched docs and
releases.
"""

from __future__ import annotations

import sys

from mcp.server.fastmcp import FastMCP

from typing import Any

from . import pypi, source_lookup
from .cache import get_or_fetch_page, refresh_page
from .docs_provenance import docs_provenance, with_docs_header
from .environment import (
    SERVER_ORIGIN,
    TargetEnvironmentError,
    environment_fields,
    inspect_environment,
    register_names,
    select_environment_hint,
    select_target_python,
    target_fields,
)
from .github import list_tags
from .readthedocs import list_versions
from .registry import PackageRegistry

MAX_LISTED_VERSIONS = 100


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


def register_tools(mcp: FastMCP, registry: PackageRegistry) -> None:
    """Register all tools on the MCP server.

    Args:
        mcp: The server to register the tools on.
        registry: Registry with the metadata of all known packages.
    """
    pypi_names = {key: registry.pypi_name(key) for key in registry.list_packages()}
    register_names(list(pypi_names.values()))

    def _docs_provenance(package: str, docs_version: str) -> dict[str, Any]:
        """Describe the docs version used for a package next to the installed one.

        Args:
            package: Package name as returned by list_packages().
            docs_version: Docs version slug that was read.

        Returns:
            Dict with docs_version, installed_version and an optional warning.
        """
        return docs_provenance(pypi_names[package], docs_version)

    # ------------------------------------------------------------------
    # Environment inspection tools
    # ------------------------------------------------------------------

    @mcp.tool()
    def get_installed_package_version(package: str) -> dict[str, Any]:
        """
        Check what version of a package is installed in the target Python
        environment (the user's research environment).

        The target is the interpreter chosen with set_python_environment, else a
        configured or detected one. The result names the interpreter and where it
        came from, so you and the user can verify it.

        Call this first when the user has not mentioned a version.

        Args:
            package: Package name as returned by list_packages().

        Returns:
            Dict with package, pypi_name, installed_version (null if not installed),
            python_executable, python_executable_origin and status
            ("installed", "not_installed" or "error", the last two with a message).
        """
        meta = registry.get_metadata(package)
        if meta is None:
            return {"error": f"Unknown package '{package}'. Available: {registry.list_packages()}"}

        pypi_name = pypi_names[package]
        environment = environment_fields(pypi_name)
        result = {"package": package, "pypi_name": pypi_name, **environment}
        if "environment_error" in environment:
            return {**result, "status": "error", "message": environment["environment_error"]}
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
        """
        try:
            environment = inspect_environment(sorted(set(pypi_names.values())), refresh=refresh)
        except TargetEnvironmentError as exc:
            return {"error": str(exc), **target_fields()}
        versions = environment.pop("versions")
        report = {
            **environment,
            "server_python_executable": sys.executable,
            "packages": {
                key: versions[name] or "not installed" for key, name in pypi_names.items()
            },
        }
        if environment["python_executable_origin"] == SERVER_ORIGIN:
            report["hint"] = (
                "This is the server's own Python, not a detected user environment. "
                + select_environment_hint()
            )
        return report

    @mcp.tool()
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
        imported; the environment is only read.

        Args:
            python_executable: Full path of the python executable, or the root
                               folder of a venv or conda environment.

        Returns:
            Same as get_server_environment for the chosen environment, or a dict
            with an error if no Python was found at the path.
        """
        try:
            select_target_python(python_executable)
        except TargetEnvironmentError as exc:
            return {"error": str(exc), **target_fields()}
        return _environment_report(refresh=True)

    @mcp.tool()
    def get_server_environment(refresh: bool = False) -> dict[str, Any]:
        """
        Inspect the target Python environment (the user's research environment).

        Returns the inspected interpreter, where it came from
        (python_executable_origin: set_python_environment, IE_MCP_TARGET_PYTHON,
        an active or project environment, or the server's own sys.executable),
        its Python version, and the installed version of every registered package.

        If this is not the environment of the user's file or project, call
        set_python_environment with the right interpreter.

        Installed versions are cached while the server runs. Pass refresh=True
        after the user installed or upgraded packages.

        Args:
            refresh: Read the environment again instead of using cached results.

        Returns:
            Dict with python_executable, python_executable_origin, python_version,
            server_python_executable and packages (package mapped to its installed
            version or "not installed"), plus a hint if no user environment was
            found; or an error with the interpreter path.
        """
        return _environment_report(refresh)

    # ------------------------------------------------------------------
    # Discovery tools
    # ------------------------------------------------------------------

    @mcp.tool()
    def list_packages() -> list[str]:
        """
        List all Python packages that this MCP server has documentation for.

        Returns:
            The registry keys of all packages, usable in every other tool.
        """
        return registry.list_packages()

    @mcp.tool()
    def get_package_info(package: str) -> dict[str, Any]:
        """
        Get metadata for a package: description, GitHub URL, docs URL, install
        commands, and the list of available documentation sections.

        Args:
            package: Package name as returned by list_packages().

        Returns:
            The package metadata plus available_sections, or a dict with an error.
        """
        meta = registry.get_metadata(package)
        if meta is None:
            available = registry.list_packages()
            return {"error": (f"Unknown package '{package}'. " f"Available packages: {available}")}
        sections = registry.get_sections(package)
        return {**meta, "available_sections": sections}

    @mcp.tool()
    def list_doc_versions(package: str) -> list[str] | dict[str, Any]:
        """
        List all available documentation versions for a package.

        Queries the ReadTheDocs API to discover published versions.
        Always call this before get_doc_section or search_docs when the user
        asks about a specific version other than the latest.

        Args:
            package: Package name as returned by list_packages().

        Returns:
            List of docs version slugs ('latest' and 'stable' first), or a dict with an error.
        """
        meta = registry.get_metadata(package)
        if meta is None:
            return {"error": f"Unknown package '{package}'."}
        slug = meta.get("readthedocs_slug")
        if not slug:
            return {"error": f"No ReadTheDocs slug registered for '{package}'."}
        try:
            return list_versions(slug)
        except Exception as exc:  # noqa: BLE001
            return {"error": f"ReadTheDocs API error: {exc}"}

    # ------------------------------------------------------------------
    # Cached/live docs tools
    # ------------------------------------------------------------------

    @mcp.tool()
    def get_doc_section(package: str, section: str, version: str = "latest") -> str:
        """
        Return the full Markdown content of a specific documentation section.

        The first call fetches the live docs page and caches it locally.
        Later calls are served from the cache.

        The text starts with a short header that states the docs version used
        (docs_version) and the installed version of the package. If they differ,
        the header has a warning: check signatures with get_function_source and
        tell the user about the mismatch.

        Defaults to the latest docs. Call list_doc_versions(package) first
        if the user asks about a specific older version.

        Call get_package_info(package) first to discover the available sections.

        Args:
            package: Package name as returned by list_packages().
            section: Section id (e.g. 'introduction', 'faq').
            version: Docs version slug (default: 'latest'). Use list_doc_versions()
                     to discover available versions.

        Returns:
            Markdown text: a header with docs_version, installed_version and an optional
            warning, then the page. A plain message if the section is unknown.
        """
        section_info = registry.get_section_info(package, section)
        if section_info is None:
            sections = registry.get_sections(package)
            if not sections:
                return (
                    f"Unknown package '{package}'. Available packages: {registry.list_packages()}"
                )
            return (
                f"Section '{section}' not found for package '{package}'. "
                f"Available sections: {', '.join(sections)}"
            )
        if version != "latest" and not registry.supports_versioning(package):
            return _version_not_supported_warning(package)
        url = registry.get_section_url(package, section, version)
        content, _ = get_or_fetch_page(package, section, url, version)
        return with_docs_header(content, _docs_provenance(package, version))

    @mcp.tool()
    def search_docs(package: str, query: str, version: str = "latest") -> list[dict[str, Any]]:
        """
        Search the package documentation for a query string.

        Missing pages are fetched live and cached before searching.
        Returns up to 10 matching paragraph-level snippets (case-insensitive).
        Each result includes the section name and a text snippet (≤500 chars),
        the docs version used (docs_version), the installed version of the
        package (installed_version) and a warning if the two differ.

        Defaults to the latest docs. Call list_doc_versions(package) first
        if the user asks about a specific older version.

        Args:
            package: Package name as returned by list_packages().
            query:   Free-text search query.
            version: Docs version slug (default: 'latest'). Use list_doc_versions()
                     to discover available versions.

        Returns:
            List of dicts with package, section, version, snippet, docs_version,
            installed_version and an optional warning; or one dict with a message.
        """
        if package not in registry.list_packages():
            return [{"error": f"Unknown package '{package}'."}]

        if version != "latest" and not registry.supports_versioning(package):
            return [{"warning": _version_not_supported_warning(package)}]

        section_urls = registry.get_all_section_urls(package, version)
        if not section_urls:
            return [{"message": f"No documentation manifest found for '{package}'."}]

        results: list[dict[str, Any]] = []
        query_lower = query.lower()
        provenance = _docs_provenance(package, version)

        for section, url in section_urls:
            content, _ = get_or_fetch_page(package, section, url, version)
            if not content:
                continue

            paragraphs = [p.strip() for p in content.split("\n\n") if p.strip()]
            for para in paragraphs:
                if query_lower in para.lower():
                    results.append(
                        {
                            "package": package,
                            "section": section,
                            "version": version,
                            "snippet": para[:500] + ("…" if len(para) > 500 else ""),
                            **provenance,
                        }
                    )
                    if len(results) >= 10:
                        return results

        if not results:
            message = f"No results found for '{query}' in '{package}' ({version})."
            return [{"message": message, **provenance}]
        return results

    # ------------------------------------------------------------------
    # Source tools: installed files first, then PyPI, then GitHub
    # ------------------------------------------------------------------

    @mcp.tool()
    def search_source(package: str, query: str, version: str | None = None) -> list[dict[str, Any]]:
        """
        Search the source code of a package for a text string (like grep).

        Without a version, or with the installed version, the installed files in
        the target environment are searched. Another version is downloaded from
        PyPI and searched; versions that are not on PyPI (e.g. 'HEAD') are read
        from GitHub at that exact tag or branch.

        Returns up to 20 matching lines with file, line and text. Every result
        states its source ("local", "pypi" or "github"), version,
        installed_version and python_executable.

        If the package is not installed and no version is given, the result has
        status "not_installed": ask the user before using version="latest".

        Args:
            package: Package name as returned by list_packages().
            query:   Search string (e.g. function name, class name, keyword).
            version: Optional version (e.g. '2.1.0', 'v2.1.0', 'latest', 'HEAD').
                     Omit to search the installed version.

        Returns:
            List of dicts with file, line, text, source, version, installed_version and
            python_executable; or one dict with a message, status or error.
        """
        meta = registry.get_metadata(package)
        if meta is None:
            return [{"error": f"Unknown package '{package}'."}]
        return source_lookup.search_source(package, meta, query, version)

    @mcp.tool()
    def list_source_versions(package: str) -> dict[str, Any]:
        """
        List the available versions of a package: releases on PyPI and tags on
        GitHub, newest first, plus the version installed in the target environment.

        Use this when the user asks about a specific version, to confirm it exists
        before calling get_function_source. Versions on PyPI are preferred; GitHub
        tags matter for versions that were never released on PyPI.

        Args:
            package: Package name as returned by list_packages().

        Returns:
            Dict with pypi_versions, github_tags, installed_version and python_executable.
            If one source fails, pypi_error or github_error replaces its list.
        """
        meta = registry.get_metadata(package)
        if meta is None:
            return {"error": f"Unknown package '{package}'."}
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

    @mcp.tool()
    def get_function_source(
        package: str,
        function_name: str,
        version: str | None = None,
        detail: str = "full",
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
        status "not_installed": ask the user before using version="latest".

        Args:
            package:       Package name as returned by list_packages().
            function_name: Name of a function ('lci'), method ('LCA.lci') or
                           class ('LCA'). Module prefixes are allowed
                           ('lca.LCA.lci').
            version:       Optional version (e.g. '2.1.0', 'v2.1.0', 'latest',
                           'HEAD'). Omit to use the installed version.
            detail:        'full' (default) returns signature, docstring and code;
                           'signature' leaves the code out to save tokens.

        Returns:
            Dict with function, qualified_name, kind, file, line, signature, docstring,
            code (detail 'full'), methods (classes), source, version,
            installed_version and python_executable. With several matches: matches
            and match_count instead. Otherwise a dict with status or error.
        """
        meta = registry.get_metadata(package)
        if meta is None:
            return {"error": f"Unknown package '{package}'."}
        return source_lookup.get_function_source(package, meta, function_name, version, detail)

    @mcp.tool()
    def fetch_latest_docs(package: str, section: str | None = None, version: str = "latest") -> str:
        """
        Force-fetch documentation for a package directly from the web, bypassing
        the local cache. Use this when the user wants the most up-to-date content
        or when cached content may be stale.

        The fetched page is written to the local cache so later calls are fast.
        Fetches a specific section page if given, otherwise the docs homepage.

        The text starts with a short header that states the docs version used
        and the installed version of the package, with a warning if they differ.

        Args:
            package: Package name as returned by list_packages().
            section: Optional section id (e.g. 'introduction', 'faq').
                     Leave empty to fetch the docs homepage.
            version: Docs version slug (default: 'latest'). Use list_doc_versions()
                     to discover available versions.

        Returns:
            Markdown text: a header with docs_version, installed_version and an optional
            warning, then the page. A plain message on failure.
        """
        meta = registry.get_metadata(package)
        if meta is None:
            return f"Unknown package '{package}'."

        if version != "latest" and not registry.supports_versioning(package):
            return _version_not_supported_warning(package)

        if section:
            url = registry.get_section_url(package, section, version)
            if url is None:
                available = registry.get_sections(package)
                return f"No URL registered for section '{section}'. Known sections: {available}"
        else:
            url = registry.get_section_url(package, "index", version) or meta["docs_url"]

        try:
            content = refresh_page(package, section or "index", url, version)
        except Exception as exc:  # noqa: BLE001
            return f"HTTP error while fetching '{url}': {exc}"
        return with_docs_header(content, _docs_provenance(package, version))
