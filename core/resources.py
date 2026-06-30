"""
MCP resources registration.

Resources expose documentation pages at docs://{package}/{section} URIs.
They are backed by the same live-fetch cache used by the tools.
"""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from .cache import get_or_fetch_page
from .registry import PackageRegistry


def register_resources(mcp: FastMCP, registry: PackageRegistry) -> None:

    @mcp.resource("docs://{package}/{section}")
    def doc_resource(package: str, section: str) -> str:
        """
        Documentation resource for a specific package section.

        URI pattern: docs://{package}/{section}
        Examples:
            docs://premise/introduction
            docs://premise/faq
            docs://premise/extract

        Returns the Markdown content of the requested section.
        """
        section_info = registry.get_section_info(package, section)
        if section_info is None:
            sections = registry.get_sections(package)
            if not sections:
                return f"Unknown package '{package}'. Available packages: {registry.list_packages()}"
            return (
                f"Section '{section}' not found for '{package}'. "
                f"Available: {', '.join(sections)}"
            )
        content, _ = get_or_fetch_page(package, section, section_info["url"])
        return content
