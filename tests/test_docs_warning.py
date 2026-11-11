"""Docs version mismatch warning, and the registered tools that carry it."""

from __future__ import annotations

import sys
from collections.abc import Callable

import pytest
from mcp.server.fastmcp.exceptions import ToolError

from core import docs_provenance, github, pypi, tools
from core.registry import PackageRegistry
from tests.conftest import PAGE


def test_mismatch_gives_a_warning(set_installed: Callable) -> None:
    set_installed("2.1.0")

    assert docs_provenance.docs_provenance("premise", "latest") == {
        "docs_version": "latest",
        "installed_version": "2.1.0",
        "warning": (
            "Docs are for 'latest', installed version is 2.1.0. "
            "Check function signatures with get_function_source."
        ),
    }


@pytest.mark.parametrize("docs_version", ["2.1.0", "v2.1.0"])
def test_matching_versions_give_no_warning(set_installed: Callable, docs_version: str) -> None:
    set_installed("2.1.0")
    assert "warning" not in docs_provenance.docs_provenance("premise", docs_version)


def test_not_installed_gives_no_warning(set_installed: Callable) -> None:
    set_installed(None)

    provenance = docs_provenance.docs_provenance("premise", "latest")

    assert provenance == {"docs_version": "latest", "installed_version": None}
    header = docs_provenance.with_docs_header(PAGE, provenance)
    assert header.startswith("> docs_version: latest | installed_version: not installed\n\n# Title")


def test_get_doc_section_starts_with_the_header(set_installed: Callable, tool: Callable) -> None:
    set_installed("2.1.0")

    text = tool("get_doc_section")("premise", "introduction")

    lines = text.splitlines()
    assert lines[0] == "> docs_version: latest | installed_version: 2.1.0"
    assert lines[1].startswith("> warning: Docs are for 'latest', installed version is 2.1.0.")
    assert text.endswith(PAGE)


def test_fetch_latest_docs_starts_with_the_header(set_installed: Callable, tool: Callable) -> None:
    set_installed("2.1.0")
    assert tool("fetch_latest_docs")("premise", "introduction").startswith("> docs_version: latest")


def test_search_docs_result_carries_the_fields(set_installed: Callable, tool: Callable) -> None:
    set_installed("2.1.0")

    result = tool("search_docs")("premise", "LCI")

    assert result["matches"][0]["snippet"] == "First paragraph about lci."
    assert result["matches"][0]["heading"] == "Title"
    assert result["docs_version"] == "latest"
    assert result["installed_version"] == "2.1.0"
    assert "warning" in result  # stated once, not per match


def test_list_source_versions_returns_both_lists(
    monkeypatch: pytest.MonkeyPatch, set_installed: Callable, tool: Callable
) -> None:
    set_installed("2.1.0")
    monkeypatch.setattr(pypi, "list_versions", lambda name: ["2.2.0", "2.1.0"])
    monkeypatch.setattr(tools, "list_tags", lambda repo: ["v2.2.0", "v2.1.0"])

    result = tool("list_source_versions")("premise")

    assert result["pypi_versions"] == ["2.2.0", "2.1.0"]
    assert result["github_tags"] == ["v2.2.0", "v2.1.0"]
    assert result["installed_version"] == "2.1.0"


def test_one_failing_source_does_not_hide_the_other(
    monkeypatch: pytest.MonkeyPatch, set_installed: Callable, tool: Callable
) -> None:
    def no_github(repo: str) -> list[str]:
        raise RuntimeError("rate limited")

    set_installed(None)
    monkeypatch.setattr(pypi, "list_versions", lambda name: ["2.2.0"])
    monkeypatch.setattr(tools, "list_tags", no_github)

    result = tool("list_source_versions")("premise")

    assert result["pypi_versions"] == ["2.2.0"]
    assert "rate limited" in result["github_error"]


def test_environment_tools_report_the_interpreter(tool: Callable) -> None:
    environment = tool("get_server_environment")()
    assert environment["python_executable"] == sys.executable
    assert environment["python_executable_origin"] == "sys.executable"
    registered = set(PackageRegistry().list_packages())
    assert set(environment["packages"]) <= registered  # only installed packages are listed
    assert environment["not_installed_count"] + len(environment["packages"]) == len(registered)

    assert "set_python_environment" in environment["hint"]

    chosen = tool("set_python_environment")(sys.executable)
    assert chosen["python_executable_origin"] == "set_python_environment"
    assert "hint" not in chosen
    with pytest.raises(ToolError, match="No Python executable"):
        tool("set_python_environment")("/no/such/python")

    missing = tool("get_installed_package_version")("premise")
    assert missing["python_executable"] == sys.executable
    assert missing["status"] in ("installed", "not_installed")


def test_github_module_is_not_called_for_tags_only(monkeypatch: pytest.MonkeyPatch) -> None:
    # resolve_ref must not need the network for HEAD
    monkeypatch.setattr(github, "list_tags", lambda repo: pytest.fail("no tag lookup for HEAD"))
    assert github.resolve_ref("owner/repo", "HEAD") == ("HEAD", False)
