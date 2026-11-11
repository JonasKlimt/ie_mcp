"""Shared fixtures: an isolated cache folder and a clean environment cache per test."""

from __future__ import annotations

import asyncio
from collections.abc import Callable
from pathlib import Path

import pytest
from mcp.server.fastmcp import FastMCP

from core import docs_discovery, docs_provenance, environment, tools
from core.registry import PackageRegistry

PAGE = "# Title\n\nFirst paragraph about lci.\n\nSecond paragraph."


@pytest.fixture(autouse=True)
def isolated_state(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Point the cache at a temp folder and inspect the test interpreter itself.

    Args:
        tmp_path: Temp folder of the test.
        monkeypatch: Pytest helper to change environment variables.
    """
    monkeypatch.setenv("IE_MCP_CACHE_DIR", str(tmp_path / "cache"))
    detection_variables = (
        environment.TARGET_VARIABLE,
        environment.PROJECT_VARIABLE,
        *environment.ACTIVE_ENVIRONMENT_VARIABLES,
    )
    for variable in detection_variables:
        monkeypatch.delenv(variable, raising=False)
    monkeypatch.chdir(tmp_path)  # no project .venv to detect
    monkeypatch.setattr(environment, "_selected_python", None)
    environment._environment_cache.clear()
    environment._distribution_cache.clear()
    environment._registered_names.clear()


@pytest.fixture
def set_installed(monkeypatch: pytest.MonkeyPatch) -> Callable[[str | None], None]:
    """Provide a function that pretends a version is installed in the target environment.

    Args:
        monkeypatch: Pytest helper.

    Returns:
        Function taking the installed version, or None for "not installed".
    """

    def apply(version: str | None) -> None:
        fields = {
            "installed_version": version,
            "python_executable": "/target/python",
            "python_executable_origin": "IE_MCP_TARGET_PYTHON",
        }
        monkeypatch.setattr(docs_provenance, "environment_fields", lambda name: fields)
        monkeypatch.setattr(tools, "environment_fields", lambda name: fields)

    return apply


@pytest.fixture
def tool(monkeypatch: pytest.MonkeyPatch) -> Callable[[str], Callable]:
    """Register the tools on a fresh server, with docs fetching and discovery mocked.

    Returns:
        Function that returns a registered tool by name, as a normal synchronous function.
    """
    monkeypatch.setattr(tools, "get_or_fetch_page", lambda *args: (PAGE, True))
    monkeypatch.setattr(tools, "refresh_page", lambda *args: PAGE)
    monkeypatch.setattr(docs_discovery, "discover_pages", lambda *args, **kwargs: [])
    server = FastMCP("test")
    tools.register_tools(server, PackageRegistry())

    def get(name: str) -> Callable:
        function = server._tool_manager.get_tool(name).fn
        return lambda *args, **kwargs: asyncio.run(function(*args, **kwargs))

    return get
