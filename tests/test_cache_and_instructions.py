"""Docs cache expiry, the config files and the server instructions."""

from __future__ import annotations

import asyncio
import os
import re
import time
from pathlib import Path

import httpx
import pytest
from mcp.server.fastmcp import FastMCP

from core import cache, tools
from core import registry as registry_module
from core.config import setting
from core.instructions import build_instructions, trigger_groups
from core.registry import PackageRegistry

DAY = 86400


def age(package: str, section: str, version: str, days: float) -> None:
    """Make a cached page look `days` old."""
    path = cache.cache_path(package, section, version)
    old = time.time() - days * DAY
    os.utime(path, (old, old))


@pytest.fixture
def downloads(monkeypatch: pytest.MonkeyPatch) -> list[str]:
    """Replace the page download by a counter that returns fresh text."""
    calls: list[str] = []
    monkeypatch.setattr(cache, "fetch_live_markdown", lambda url: calls.append(url) or "fresh")
    return calls


def test_fresh_page_comes_from_the_cache(downloads: list[str]) -> None:
    cache.write_cached_page("pkg", "faq", "old", "latest")

    assert cache.get_or_fetch_page("pkg", "faq", "http://x", "latest") == ("old", True)
    assert downloads == []


def test_old_latest_page_is_downloaded_again(downloads: list[str]) -> None:
    cache.write_cached_page("pkg", "faq", "old", "latest")
    age("pkg", "faq", "latest", days=10)

    assert cache.get_or_fetch_page("pkg", "faq", "http://x", "latest") == ("fresh", False)
    assert cache.read_cached_page("pkg", "faq", "latest") == "fresh"


def test_pinned_versions_never_expire(downloads: list[str]) -> None:
    cache.write_cached_page("pkg", "faq", "old", "2.0.1")
    age("pkg", "faq", "2.0.1", days=3650)

    assert cache.get_or_fetch_page("pkg", "faq", "http://x", "2.0.1") == ("old", True)
    assert downloads == []


def test_old_copy_is_served_when_the_download_fails(monkeypatch: pytest.MonkeyPatch) -> None:
    def down(url: str) -> str:
        raise httpx.ConnectError("offline")

    monkeypatch.setattr(cache, "fetch_live_markdown", down)
    cache.write_cached_page("pkg", "faq", "old", "latest")
    age("pkg", "faq", "latest", days=10)

    assert cache.get_or_fetch_page("pkg", "faq", "http://x", "latest") == ("old", True)
    with pytest.raises(httpx.ConnectError):
        cache.get_or_fetch_page("pkg", "never_cached", "http://x", "latest")


def test_ttl_comes_from_config_and_can_be_overridden(monkeypatch: pytest.MonkeyPatch) -> None:
    assert cache.docs_ttl_days() == setting("docs", "ttl_days") == 7

    monkeypatch.setenv(cache.TTL_VARIABLE, "0.5")
    assert cache.docs_ttl_days() == 0.5

    monkeypatch.setenv(cache.TTL_VARIABLE, "not a number")
    assert cache.docs_ttl_days() == 7


def test_json_cache_respects_the_ttl(tmp_path: Path) -> None:
    path = tmp_path / "pages.json"
    cache.write_json_cache(path, [{"id": "a"}])

    assert cache.read_json_cache(path, "latest") == [{"id": "a"}]
    old = time.time() - 10 * DAY
    os.utime(path, (old, old))
    assert cache.read_json_cache(path, "latest") is None
    assert cache.read_json_cache(path, "2.0.1") == [{"id": "a"}]
    path.write_text("{broken", encoding="utf-8")
    assert cache.read_json_cache(path, "2.0.1") is None


def test_trigger_groups_only_name_registered_packages() -> None:
    registered = set(PackageRegistry().list_packages())

    for group in trigger_groups():
        assert group["triggers"] and group["check_first"], group["name"]
        assert set(group["check_first"]) <= registered, group["name"]


def test_instructions_contain_the_trigger_map_and_rules() -> None:
    text = build_instructions()

    for group in trigger_groups():
        assert group["name"] in text
    assert "Trigger terms -> packages to check first:" in text
    assert "without waiting for the user to say" in text
    assert "set_python_environment" in text and "isError" in text


def test_instructions_only_mention_existing_tools() -> None:
    server = FastMCP("test")
    tools.register_tools(server, PackageRegistry())
    names = {item.name for item in asyncio.run(server.list_tools())}

    mentioned = set(re.findall(r"\b([a-z][a-z_]+)\(", build_instructions())) - {"print"}

    assert mentioned <= names, mentioned - names


def test_registry_never_prints_to_stdout(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    caplog: pytest.LogCaptureFixture,
) -> None:
    def broken_manifest(name: str) -> None:
        raise RuntimeError("bad manifest")

    monkeypatch.setattr(registry_module.importlib, "import_module", broken_manifest)

    with caplog.at_level("WARNING", logger="ie_mcp"):
        registry = registry_module.PackageRegistry()

    assert registry.list_packages() == []
    assert capsys.readouterr().out == ""  # stdout carries the MCP protocol
    assert "bad manifest" in caplog.text
