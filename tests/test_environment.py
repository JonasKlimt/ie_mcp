"""Target-interpreter subprocess, using the test interpreter as the target."""

from __future__ import annotations

import sys
from importlib.metadata import version as installed_version
from pathlib import Path

import pytest

from core import environment
from core.environment import TargetEnvironmentError

MISSING_PACKAGE = "ie-mcp-package-that-does-not-exist"


def test_default_target_is_the_server_interpreter() -> None:
    assert environment.resolve_target_python() == (sys.executable, "sys.executable")


def test_target_from_environment_variable(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(environment.TARGET_VARIABLE, "/some/python")
    assert environment.resolve_target_python() == ("/some/python", environment.TARGET_VARIABLE)


def fake_environment(folder: Path) -> Path:
    """Create a folder that looks like a venv, with the test interpreter's name inside.

    Args:
        folder: Folder to create.

    Returns:
        Path of the fake python executable.
    """
    python = folder / ("Scripts/python.exe" if sys.platform == "win32" else "bin/python")
    python.parent.mkdir(parents=True)
    python.write_bytes(b"")
    return python


def test_selected_environment_wins(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    python = fake_environment(tmp_path / "env")
    monkeypatch.setenv(environment.TARGET_VARIABLE, "/some/python")

    # a folder or the executable itself are both accepted
    assert environment.select_target_python(str(tmp_path / "env")) == str(python)
    assert environment.select_target_python(f'"{python}"') == str(python)
    assert environment.resolve_target_python() == (str(python), environment.SELECTED_ORIGIN)


def test_selecting_a_missing_environment_is_an_error(tmp_path: Path) -> None:
    with pytest.raises(TargetEnvironmentError, match="No Python executable"):
        environment.select_target_python(str(tmp_path / "nothing"))
    assert environment.resolve_target_python()[1] == environment.SERVER_ORIGIN


def test_active_environment_is_detected(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    python = fake_environment(tmp_path / "active")
    monkeypatch.setenv("VIRTUAL_ENV", str(tmp_path / "active"))

    assert environment.resolve_target_python() == (str(python), "VIRTUAL_ENV")


def test_server_environment_is_not_taken_for_the_users(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("VIRTUAL_ENV", sys.prefix)
    assert environment.resolve_target_python() == (sys.executable, environment.SERVER_ORIGIN)


def test_project_venv_is_detected(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    project = tmp_path / "project"
    python = fake_environment(project / ".venv")
    monkeypatch.setenv(environment.PROJECT_VARIABLE, str(project))

    path, origin = environment.resolve_target_python()

    assert path == str(python)
    assert origin == f".venv folder in {project}"


def test_inspect_environment_reads_versions() -> None:
    result = environment.inspect_environment(["pytest", MISSING_PACKAGE])

    assert result["python_executable"] == sys.executable
    assert result["python_executable_origin"] == "sys.executable"
    assert result["python_version"] == sys.version
    assert result["versions"] == {"pytest": installed_version("pytest"), MISSING_PACKAGE: None}


def test_results_are_cached_until_refresh(monkeypatch: pytest.MonkeyPatch) -> None:
    calls = []
    real_run = environment.run_in_target

    def counting_run(script: str, payload: dict) -> dict:
        calls.append(payload)
        return real_run(script, payload)

    monkeypatch.setattr(environment, "run_in_target", counting_run)

    environment.inspect_environment(["pytest"])
    environment.inspect_environment(["pytest"])
    assert len(calls) == 1

    environment.inspect_environment(["pytest"], refresh=True)
    assert len(calls) == 2


def test_registered_names_are_read_in_the_same_subprocess(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    environment.register_names(["pytest", "httpx"])
    environment.inspect_environment(["pytest"])
    monkeypatch.setattr(environment, "run_in_target", lambda *args: pytest.fail("not cached"))

    assert environment.inspect_environment(["httpx"])["versions"]["httpx"]


def test_environment_fields_never_raise(monkeypatch: pytest.MonkeyPatch) -> None:
    assert environment.environment_fields("pytest")["installed_version"] == installed_version(
        "pytest"
    )

    monkeypatch.setenv(environment.TARGET_VARIABLE, "/no/such/python")
    fields = environment.environment_fields("pytest")
    assert fields["installed_version"] is None
    assert fields["python_executable"] == "/no/such/python"
    assert "not found" in fields["environment_error"]


def test_distribution_info_lists_python_files() -> None:
    info = environment.get_distribution_info("pytest")

    assert info["installed"] is True
    assert info["version"] == installed_version("pytest")
    assert info["py_files"] and all(path.endswith(".py") for path in info["py_files"])
    assert environment.get_distribution_info(MISSING_PACKAGE) == {"installed": False}


def test_missing_interpreter_is_reported(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(environment.TARGET_VARIABLE, "/no/such/python")
    with pytest.raises(TargetEnvironmentError, match="not found"):
        environment.inspect_environment(["pytest"])


def test_bad_output_is_reported() -> None:
    with pytest.raises(TargetEnvironmentError, match="unreadable output"):
        environment.run_in_target("print('this is not json')", {})


def test_failing_script_is_reported() -> None:
    with pytest.raises(TargetEnvironmentError, match="exited with code 3"):
        environment.run_in_target("raise SystemExit(3)", {})


def test_timeout_is_reported(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(environment, "SUBPROCESS_TIMEOUT_SECONDS", 0.2)
    with pytest.raises(TargetEnvironmentError, match="did not answer"):
        environment.run_in_target("import time; time.sleep(5)", {})
