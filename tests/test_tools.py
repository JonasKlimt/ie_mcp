"""Registered tools: failures, annotations, result shapes, long pages and per-call interpreter."""

from __future__ import annotations

import sys
from collections.abc import Callable

import httpx
import pytest
from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.exceptions import ToolError

from core import changelog, docs_discovery, environment, tools
from core.registry import PackageRegistry


def test_unknown_package_is_a_tool_error_with_suggestions(tool: Callable) -> None:
    with pytest.raises(ToolError, match="Did you mean: premise"):
        tool("get_package_info")("premis")
    with pytest.raises(ToolError, match="list_packages"):
        tool("get_function_source")("no_such_package_at_all", "f")


def test_every_tool_is_annotated() -> None:
    server = FastMCP("test")
    tools.register_tools(server, PackageRegistry())

    registered = server._tool_manager.list_tools()

    assert len(registered) >= 14
    for item in registered:
        assert item.title and item.annotations is not None
        assert item.annotations.readOnlyHint is (item.name != "set_python_environment")


def test_list_packages_has_descriptions_and_versions(
    monkeypatch: pytest.MonkeyPatch, tool: Callable
) -> None:
    def fake_environment(names: list[str], refresh: bool = False) -> dict:
        return {"versions": {name: "1.0" if name == "premise" else None for name in names}}

    monkeypatch.setattr(tools, "inspect_environment", fake_environment)

    everything = tool("list_packages")()
    installed = tool("list_packages")(installed_only=True)

    by_name = {item["package"]: item for item in everything}
    assert len(everything) == len(PackageRegistry().list_packages())
    assert by_name["premise"]["installed_version"] == "1.0"
    assert by_name["bw2calc"]["installed_version"] is None
    assert all(0 < len(item["description"]) <= 110 for item in everything)
    assert [item["package"] for item in installed] == ["premise"]


def test_list_packages_works_when_the_environment_is_unreadable(
    monkeypatch: pytest.MonkeyPatch, tool: Callable
) -> None:
    def broken(names: list[str], refresh: bool = False) -> dict:
        raise environment.TargetEnvironmentError("not found")

    monkeypatch.setattr(tools, "inspect_environment", broken)

    assert "installed_version" not in tool("list_packages")()[0]
    with pytest.raises(ToolError, match="not found"):
        tool("list_packages")(installed_only=True)


def test_long_pages_are_cut_and_can_be_continued(
    monkeypatch: pytest.MonkeyPatch, set_installed: Callable, tool: Callable
) -> None:
    set_installed(None)
    monkeypatch.setattr(tools, "get_or_fetch_page", lambda *args: ("abcdefghij" * 10, True))

    first = tool("get_doc_section")("premise", "faq", max_chars=40)
    second = tool("get_doc_section")("premise", "faq", max_chars=40, offset=40)
    last = tool("get_doc_section")("premise", "faq", max_chars=40, offset=80)

    assert first.endswith("[Cut at character 40 of 100. Call again with offset=40.]")
    assert "[Continuing at character 40 of 100.]" in second and "offset=80" in second
    assert "Cut at" not in last and last.endswith("abcdefghijabcdefghij")


def test_unknown_section_names_the_alternatives(tool: Callable) -> None:
    with pytest.raises(ToolError, match="list_doc_sections"):
        tool("get_doc_section")("premise", "no_such_section")


def test_discovered_pages_can_be_listed_and_read(
    monkeypatch: pytest.MonkeyPatch, set_installed: Callable, tool: Callable
) -> None:
    set_installed(None)
    extra = [{"id": "api_lca", "title": "LCA", "url": "https://x.org/en/latest/api_lca.html"}]
    monkeypatch.setattr(docs_discovery, "discover_pages", lambda *args, **kwargs: extra)
    fetched = []
    monkeypatch.setattr(
        tools, "get_or_fetch_page", lambda *args: (fetched.append(args[2]) or "text", True)
    )

    sections = tool("list_doc_sections")("premise")["sections"]
    tool("get_doc_section")("premise", "api_lca")

    assert {"id": "api_lca", "title": "LCA", "curated": False} in sections
    assert sections[0]["curated"] is True
    assert fetched == ["https://x.org/en/latest/api_lca.html"]


def test_search_reports_pages_that_could_not_be_read(
    monkeypatch: pytest.MonkeyPatch, set_installed: Callable, tool: Callable
) -> None:
    def flaky(package: str, section: str, url: str, version: str) -> tuple[str, bool]:
        if section == "faq":
            raise httpx.ConnectError("boom")
        return "# Title\n\nParagraph about lci.", True

    set_installed(None)
    monkeypatch.setattr(tools, "get_or_fetch_page", flaky)

    result = tool("search_docs")("premise", "lci")

    assert result["matches"]  # the other pages still answer
    assert result["skipped_pages"] == [{"section": "faq", "error": "boom"}]


def test_search_without_hits_says_so(set_installed: Callable, tool: Callable) -> None:
    set_installed(None)

    result = tool("search_docs")("premise", "zzzzzz")

    assert result["matches"] == [] and "No results" in result["message"]


def test_download_failures_are_tool_errors(
    monkeypatch: pytest.MonkeyPatch, set_installed: Callable, tool: Callable
) -> None:
    def down(*args: object) -> str:
        raise httpx.ConnectError("no internet")

    set_installed(None)
    monkeypatch.setattr(tools, "refresh_page", down)

    with pytest.raises(ToolError, match="Network error: no internet"):
        tool("fetch_latest_docs")("premise", "faq")


def test_rate_limit_gets_a_token_hint() -> None:
    response = httpx.Response(403, request=httpx.Request("GET", "https://api.github.com/x"))
    error = httpx.HTTPStatusError("forbidden", request=response.request, response=response)

    assert "rate limit" in tools._network_message(error)
    assert "GITHUB_TOKEN" in tools._network_message(error)
    assert "GITHUB_TOKEN" not in tools._network_message(httpx.ConnectError("x"))


@pytest.mark.parametrize(
    "url, hinted", [("https://api.github.com/x", True), ("https://pypi.org/x", False)]
)
def test_rejected_github_token_is_named(url: str, hinted: bool) -> None:
    response = httpx.Response(401, request=httpx.Request("GET", url))
    error = httpx.HTTPStatusError("unauthorized", request=response.request, response=response)

    assert ("invalid, expired or revoked" in tools._network_message(error)) is hinted


def test_per_call_interpreter_does_not_change_the_server_choice(tool: Callable) -> None:
    once = tool("get_server_environment")(python_executable=sys.executable)
    after = tool("get_server_environment")()

    assert once["python_executable_origin"] == environment.OVERRIDE_ORIGIN
    assert after["python_executable_origin"] == environment.SERVER_ORIGIN
    with pytest.raises(ToolError, match="No Python executable"):
        tool("get_server_environment")(python_executable="/no/such/python")


def test_changelog_starts_after_the_installed_version(
    monkeypatch: pytest.MonkeyPatch, set_installed: Callable, tool: Callable
) -> None:
    seen = {}

    def fake_build(repo: str, lower: str | None, upper: str | None, installed: str | None) -> dict:
        seen.update(repo=repo, lower=lower, upper=upper)
        return {"source": "github_releases", "releases": []}

    set_installed("1.8.0")
    monkeypatch.setattr(changelog, "build_changelog", fake_build)

    default = tool("get_changelog")("bw2calc")
    explicit = tool("get_changelog")("bw2calc", from_version="v1.0", to_version="2.0")

    assert default["from_version"] == "1.8.0" and default["source"] == "github_releases"
    assert seen == {"repo": "brightway-lca/brightway2-calc", "lower": "1.0", "upper": "2.0"}
    assert explicit["to_version"] == "2.0"
