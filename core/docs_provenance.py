"""
Compares the docs version that was read with the version installed in the target environment.

Tools pass the package's PyPI name and the docs version slug; the result is a set of
fields (or a text header) that warns when docs and installed code differ.
"""

from __future__ import annotations

from typing import Any

from .environment import environment_fields, normalize_version


def docs_provenance(pypi_name: str, docs_version: str) -> dict[str, Any]:
    """Compare the docs version that was used with the installed version.

    Args:
        pypi_name: Distribution name as published on PyPI.
        docs_version: Docs version slug that was actually read (e.g. "latest").

    Returns:
        Dict with docs_version and installed_version, plus a warning if the
        package is installed in a different version.
    """
    installed = environment_fields(pypi_name)["installed_version"]
    fields = {"docs_version": docs_version, "installed_version": installed}
    if installed and normalize_version(docs_version) != normalize_version(installed):
        fields["warning"] = (
            f"Docs are for '{docs_version}', installed version is {installed}. "
            f"Check function signatures with get_function_source."
        )
    return fields


def with_docs_header(content: str, provenance: dict[str, Any]) -> str:
    """Put the docs provenance on top of a Markdown page.

    Args:
        content: Markdown text of the documentation page.
        provenance: Result of docs_provenance().

    Returns:
        The page with a short quoted header block in front.
    """
    installed = provenance["installed_version"] or "not installed"
    lines = [f"> docs_version: {provenance['docs_version']} | installed_version: {installed}"]
    if "warning" in provenance:
        lines.append(f"> warning: {provenance['warning']}")
    return "\n".join(lines) + "\n\n" + content
