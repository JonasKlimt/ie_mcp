"""
MCP tools registration.

All tools are registered onto the FastMCP instance via register_tools().
Tools use the PackageRegistry for package metadata and the local cache for
live-fetched documentation pages.
"""

from __future__ import annotations

import sys
from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as pkg_version

from mcp.server.fastmcp import FastMCP

from .cache import get_or_fetch_page, refresh_page
from .github import find_and_extract_function, list_tags, search_code
from .readthedocs import list_versions
from .registry import PackageRegistry


def _version_not_supported_warning(package: str) -> str:
    return (
        f"⚠️ Versioned documentation is not available for '{package}'. "
        f"Its documentation URLs do not follow the standard ReadTheDocs versioning "
        f"pattern (/en/{{version}}/), so older versions cannot be accessed. "
        f"Only the current (latest) documentation is available."
    )


def register_tools(mcp: FastMCP, registry: PackageRegistry) -> None:

    # ------------------------------------------------------------------
    # Environment inspection tools
    # ------------------------------------------------------------------

    @mcp.tool()
    def get_installed_package_version(package: str) -> dict:
        """
        Check what version of a package is installed in the MCP server's Python
        environment.

        Returns the installed version and the Python executable path so users can
        verify which environment is being checked. Always call this before
        get_function_source or get_doc_section when the user has not specified a
        version, to ensure the documentation and source code match their actual
        installation.

        If the package is not installed, the response includes guidance on pointing
        mcp.json to the right Python environment.

        Args:
            package: Package name as returned by list_packages().
        """
        meta = registry.get_metadata(package)
        if meta is None:
            return {"error": f"Unknown package '{package}'. Available: {registry.list_packages()}"}

        pypi_name = meta.get("name", package)
        try:
            installed = pkg_version(pypi_name)
            return {
                "package": package,
                "pypi_name": pypi_name,
                "installed_version": installed,
                "python_executable": sys.executable,
                "status": "installed",
            }
        except PackageNotFoundError:
            return {
                "package": package,
                "pypi_name": pypi_name,
                "installed_version": None,
                "python_executable": sys.executable,
                "status": "not_installed",
                "message": (
                    f"'{pypi_name}' is not installed in the MCP server's Python "
                    f"environment ({sys.executable}). "
                    f"Update the 'command' in .vscode/mcp.json to point to the Python "
                    f"where you installed it, then restart the MCP server."
                ),
            }

    @mcp.tool()
    def get_server_environment() -> dict:
        """
        Inspect the MCP server's Python environment.

        Returns the Python executable path, Python version, and the installed version
        of every package registered in this server. Use this to verify that the MCP
        server is running in the correct environment before asking about specific
        packages. If a package shows 'not installed', update the 'command' field in
        .vscode/mcp.json to point to the Python where you have your packages installed.
        """
        packages: dict[str, str] = {}
        for pkg_key in registry.list_packages():
            meta = registry.get_metadata(pkg_key)
            pypi_name = meta.get("name", pkg_key) if meta else pkg_key
            try:
                packages[pkg_key] = pkg_version(pypi_name)
            except PackageNotFoundError:
                packages[pkg_key] = "not installed"

        return {
            "python_executable": sys.executable,
            "python_version": sys.version,
            "packages": packages,
        }

    # ------------------------------------------------------------------
    # Discovery tools
    # ------------------------------------------------------------------

    @mcp.tool()
    def list_packages() -> list[str]:
        """List all Python packages that this MCP server has documentation for."""
        return registry.list_packages()

    @mcp.tool()
    def get_package_info(package: str) -> dict:
        """
        Get metadata for a package: description, GitHub URL, docs URL, install
        commands, and the list of available documentation sections.

        Args:
            package: Package name as returned by list_packages().
        """
        meta = registry.get_metadata(package)
        if meta is None:
            available = registry.list_packages()
            return {
                "error": (
                    f"Unknown package '{package}'. "
                    f"Available packages: {available}"
                )
            }
        sections = registry.get_sections(package)
        return {**meta, "available_sections": sections}

    @mcp.tool()
    def list_doc_versions(package: str) -> list[str] | dict:
        """
        List all available documentation versions for a package.

        Queries the ReadTheDocs API to discover published versions.
        Always call this before get_doc_section or search_docs when the user
        asks about a specific version other than the latest.

        Args:
            package: Package name as returned by list_packages().
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

        Defaults to the latest version. Call list_doc_versions(package) first
        if the user asks about a specific older version.

        Call get_package_info(package) first to discover the available sections.

        Args:
            package: Package name as returned by list_packages().
            section: Section id (e.g. 'introduction', 'faq').
            version: Docs version slug (default: 'latest'). Use list_doc_versions()
                     to discover available versions.
        """
        section_info = registry.get_section_info(package, section)
        if section_info is None:
            sections = registry.get_sections(package)
            if not sections:
                return f"Unknown package '{package}'. Available packages: {registry.list_packages()}"
            return (
                f"Section '{section}' not found for package '{package}'. "
                f"Available sections: {', '.join(sections)}"
            )
        if version != "latest" and not registry.supports_versioning(package):
            return _version_not_supported_warning(package)
        url = registry.get_section_url(package, section, version)
        content, _ = get_or_fetch_page(package, section, url, version)
        return content

    @mcp.tool()
    def search_docs(package: str, query: str, version: str = "latest") -> list[dict]:
        """
        Search the package documentation for a query string.

        Missing pages are fetched live and cached before searching.
        Returns up to 10 matching paragraph-level snippets (case-insensitive).
        Each result includes the section name and a text snippet (≤500 chars).

        Defaults to the latest version. Call list_doc_versions(package) first
        if the user asks about a specific older version.

        Args:
            package: Package name as returned by list_packages().
            query:   Free-text search query.
            version: Docs version slug (default: 'latest'). Use list_doc_versions()
                     to discover available versions.
        """
        if package not in registry.list_packages():
            return [{"error": f"Unknown package '{package}'."}]

        if version != "latest" and not registry.supports_versioning(package):
            return [{"warning": _version_not_supported_warning(package)}]

        section_urls = registry.get_all_section_urls(package, version)
        if not section_urls:
            return [{"message": f"No documentation manifest found for '{package}'."}]

        results: list[dict] = []
        query_lower = query.lower()

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
                        }
                    )
                    if len(results) >= 10:
                        return results

        if not results:
            return [{"message": f"No results found for '{query}' in '{package}' ({version})."}]
        return results

    # ------------------------------------------------------------------
    # GitHub source tools
    # ------------------------------------------------------------------

    @mcp.tool()
    def search_source(package: str, query: str) -> list[dict]:
        """
        Search the GitHub source code of a package for a query string.

        Uses the GitHub code search API to find files containing the query.
        Returns up to 10 results with the file name, path, and GitHub URL.

        Requires the GITHUB_TOKEN environment variable for best results
        (5000 req/hr authenticated vs 60/hr unauthenticated).

        Args:
            package: Package name as returned by list_packages().
            query:   Search string (e.g. function name, class name, keyword).
        """
        meta = registry.get_metadata(package)
        if meta is None:
            return [{"error": f"Unknown package '{package}'."}]
        github_repo = meta.get("github_repo")
        if not github_repo:
            return [{"error": f"No GitHub repository registered for '{package}'."}]
        try:
            return search_code(github_repo, query)
        except Exception as exc:  # noqa: BLE001
            return [{"error": f"GitHub API error: {exc}"}]

    @mcp.tool()
    def list_source_versions(package: str) -> list[str] | dict:
        """
        List all available source code versions (GitHub tags) for a package.

        Use this when the user asks about a specific version of a function,
        to confirm the version exists before calling get_function_source.

        Args:
            package: Package name as returned by list_packages().
        """
        meta = registry.get_metadata(package)
        if meta is None:
            return {"error": f"Unknown package '{package}'."}
        github_repo = meta.get("github_repo")
        if not github_repo:
            return {"error": f"No GitHub repository registered for '{package}'."}
        try:
            return list_tags(github_repo)
        except Exception as exc:  # noqa: BLE001
            return {"error": f"GitHub API error: {exc}"}

    @mcp.tool()
    def get_function_source(package: str, function_name: str, version: str | None = None) -> dict:
        """
        Find a function in the package's GitHub source code and return its
        full source, including docstring and signature.

        Searches the repository for files containing the function name, then
        uses Python's ast module to extract the exact function definition.
        The raw source file is cached locally after the first fetch.

        If a version is given, the file is fetched at that GitHub tag. Call
        list_source_versions(package) first to confirm the version tag exists.

        Only returns an error if the version tag does not exist, or if the
        function was not present in the codebase at that version.

        Args:
            package:       Package name as returned by list_packages().
            function_name: Exact name of the function or method to retrieve.
            version:       Optional version tag (e.g. 'v2.1.0' or '2.1.0').
                           Omit to get the current (latest) implementation.
        """
        meta = registry.get_metadata(package)
        if meta is None:
            return {"error": f"Unknown package '{package}'."}
        github_repo = meta.get("github_repo")
        if not github_repo:
            return {"error": f"No GitHub repository registered for '{package}'."}
        return find_and_extract_function(package, github_repo, function_name, version)

    @mcp.tool()
    def fetch_latest_docs(package: str, section: str | None = None, version: str = "latest") -> str:
        """
        Force-fetch documentation for a package directly from the web, bypassing
        the local cache. Use this when the user wants the most up-to-date content
        or when cached content may be stale.

        The fetched page is written to the local cache so later calls are fast.
        Fetches a specific section page if given, otherwise the docs homepage.

        Args:
            package: Package name as returned by list_packages().
            section: Optional section id (e.g. 'introduction', 'faq').
                     Leave empty to fetch the docs homepage.
            version: Docs version slug (default: 'latest'). Use list_doc_versions()
                     to discover available versions.
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
                return (
                    f"No URL registered for section '{section}'. "
                    f"Known sections: {available}"
                )
        else:
            url = registry.get_section_url(package, "index", version) or meta["docs_url"]

        try:
            return refresh_page(package, section or "index", url, version)
        except Exception as exc:  # noqa: BLE001
            return f"HTTP error while fetching '{url}': {exc}"
