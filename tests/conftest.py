"""Shared fixtures: an isolated cache folder and a clean environment cache per test."""

from __future__ import annotations

from pathlib import Path

import pytest

from core import environment


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
