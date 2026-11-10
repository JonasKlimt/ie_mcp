"""
Reads installed package versions and file paths from the target Python environment.

The target interpreter is chosen by the assistant (set_python_environment), configured
(IE_MCP_TARGET_PYTHON) or detected. It is run as a subprocess with standard-library-only
scripts, so user packages are never imported.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

TARGET_VARIABLE = "IE_MCP_TARGET_PYTHON"
SELECTED_ORIGIN = "set_python_environment"
SERVER_ORIGIN = "sys.executable"
ACTIVE_ENVIRONMENT_VARIABLES = ("VIRTUAL_ENV", "CONDA_PREFIX")
PROJECT_VARIABLE = "CLAUDE_PROJECT_DIR"  # set by Claude Code for MCP servers
PROJECT_ENVIRONMENT_FOLDERS = (".venv", "venv")
# Where python sits inside an environment folder: conda on Windows, venv on Windows, POSIX.
_PYTHON_LOCATIONS = ("python.exe", "Scripts/python.exe", "bin/python")
SUBPROCESS_TIMEOUT_SECONDS = 30.0

# Runs inside the target interpreter. Standard library only.
_VERSIONS_SCRIPT = """
import importlib.metadata as md, json, sys
names = json.loads(sys.argv[1])["names"]
versions = {}
for name in names:
    try:
        versions[name] = md.version(name)
    except md.PackageNotFoundError:
        versions[name] = None
print(json.dumps({"python_version": sys.version, "versions": versions}))
"""

# Runs inside the target interpreter. Standard library only.
_DISTRIBUTION_SCRIPT = """
import importlib.metadata as md, json, sys
name = json.loads(sys.argv[1])["name"]
try:
    dist = md.distribution(name)
except md.PackageNotFoundError:
    print(json.dumps({"installed": False}))
    sys.exit(0)
files = dist.files or []
located = [str(dist.locate_file(f)) for f in files]
pth_lines = []
for path in located:
    if path.endswith(".pth"):
        try:
            with open(path, encoding="utf-8") as handle:
                pth_lines.extend(handle.read().splitlines())
        except OSError:
            pass
print(json.dumps({
    "installed": True,
    "version": dist.version,
    "py_files": [p for p in located if p.endswith(".py")],
    "direct_url": dist.read_text("direct_url.json"),
    "pth_lines": pth_lines,
}))
"""

_environment_cache: dict[str, dict[str, Any]] = {}
_distribution_cache: dict[tuple[str, str], dict[str, Any]] = {}
_registered_names: set[str] = set()  # read together in one subprocess
_selected_python: str | None = None  # chosen with set_python_environment


class TargetEnvironmentError(RuntimeError):
    """The target Python interpreter could not be inspected."""


def python_in_folder(folder: Path) -> str | None:
    """Find the Python executable of an environment folder (venv or conda).

    Args:
        folder: Root folder of the environment.

    Returns:
        Path of the executable, or None if the folder holds no Python.
    """
    for relative in _PYTHON_LOCATIONS:
        candidate = folder / relative
        if candidate.is_file():
            return str(candidate)
    return None


def select_target_python(path: str) -> str:
    """Choose the environment to inspect for the rest of the server run.

    Args:
        path: Python executable, or root folder of a venv or conda environment.

    Returns:
        Path of the selected Python executable.

    Raises:
        TargetEnvironmentError: If the path holds no Python executable.
    """
    global _selected_python
    cleaned = Path(path.strip().strip("\"'")).expanduser()
    python = python_in_folder(cleaned) if cleaned.is_dir() else str(cleaned)
    if python is None or not Path(python).is_file():
        raise TargetEnvironmentError(
            f"No Python executable found at '{path}'. Pass the full path of the python "
            f"executable, or the root folder of a venv or conda environment."
        )
    _selected_python = python
    return python


def _active_environment() -> tuple[str, str] | None:
    """Find an environment that was active when the server was started.

    The server's own environment is skipped: it holds the server, not the user's packages.

    Returns:
        The interpreter path and the variable it came from, or None.
    """
    for variable in ACTIVE_ENVIRONMENT_VARIABLES:
        folder = os.environ.get(variable, "").strip()
        if not folder or Path(folder).resolve() == Path(sys.prefix).resolve():
            continue
        python = python_in_folder(Path(folder))
        if python:
            return python, variable
    return None


def _project_environment() -> tuple[str, str] | None:
    """Find a virtual environment inside the folder the user's AI client works in.

    Returns:
        The interpreter path and the folder it was found in, or None.
    """
    project = os.environ.get(PROJECT_VARIABLE, "").strip()
    for folder in dict.fromkeys(Path(p) for p in (project, os.getcwd()) if p):
        for name in PROJECT_ENVIRONMENT_FOLDERS:
            python = python_in_folder(folder / name)
            if python and Path(folder / name).resolve() != Path(sys.prefix).resolve():
                return python, f"{name} folder in {folder}"
    return None


def resolve_target_python() -> tuple[str, str]:
    """Find the interpreter whose environment should be inspected.

    Order: set_python_environment, IE_MCP_TARGET_PYTHON, an active venv or conda
    environment, a .venv folder in the project, then the server's own Python.

    Returns:
        The interpreter path and where it came from, e.g. "set_python_environment",
        "IE_MCP_TARGET_PYTHON", "VIRTUAL_ENV" or "sys.executable" (SERVER_ORIGIN).
    """
    if _selected_python:
        return _selected_python, SELECTED_ORIGIN
    configured = os.environ.get(TARGET_VARIABLE, "").strip()
    if configured:
        return configured, TARGET_VARIABLE
    detected = _active_environment() or _project_environment()
    return detected or (sys.executable, SERVER_ORIGIN)


def select_environment_hint() -> str:
    """Explain how the assistant chooses the user's environment.

    Returns:
        Text for results where the right environment is unknown or was not found.
    """
    return (
        "Find the Python interpreter of the file, notebook or project the user works on "
        "(the selected interpreter or kernel; or run "
        '`python -c "import sys; print(sys.executable)"` in the project\'s environment) '
        "and call set_python_environment(path). If you cannot find it, ask the user "
        "which environment to use."
    )


def target_fields() -> dict[str, Any]:
    """Name the inspected interpreter in the shape used by all tool results.

    Returns:
        Dict with python_executable and python_executable_origin.
    """
    python, origin = resolve_target_python()
    return {"python_executable": python, "python_executable_origin": origin}


def register_names(pypi_names: list[str]) -> None:
    """Announce distributions whose versions should be read in one batch.

    Nothing is run here. The next version lookup reads all registered names in
    the same subprocess instead of one subprocess per package.

    Args:
        pypi_names: Distribution names as published on PyPI.
    """
    _registered_names.update(pypi_names)


def run_in_target(script: str, payload: dict[str, Any]) -> dict[str, Any]:
    """Run a small script in the target interpreter and parse its JSON output.

    Args:
        script: Python source that prints one JSON object to stdout.
        payload: JSON-serialisable input, passed to the script as sys.argv[1].

    Returns:
        The decoded JSON object printed by the script.

    Raises:
        TargetEnvironmentError: If the interpreter is missing, times out, fails,
            or prints something that is not JSON.
    """
    python, origin = resolve_target_python()
    if not Path(python).is_file():
        raise TargetEnvironmentError(
            f"Target Python interpreter not found: '{python}' (from {origin}). "
            f"{select_environment_hint()}"
        )
    command = [python, "-I", "-X", "utf8", "-c", script, json.dumps(payload)]
    try:
        completed = subprocess.run(
            command,
            capture_output=True,
            stdin=subprocess.DEVNULL,  # never read the MCP stdio stream
            timeout=SUBPROCESS_TIMEOUT_SECONDS,
            encoding="utf-8",
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        raise TargetEnvironmentError(
            f"Target Python '{python}' did not answer within "
            f"{SUBPROCESS_TIMEOUT_SECONDS:.0f} seconds."
        ) from exc
    except OSError as exc:
        raise TargetEnvironmentError(
            f"Target Python '{python}' could not be started: {exc}"
        ) from exc

    if completed.returncode != 0:
        raise TargetEnvironmentError(
            f"Target Python '{python}' exited with code {completed.returncode}: "
            f"{completed.stderr.strip()[-500:]}"
        )
    try:
        return json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        raise TargetEnvironmentError(
            f"Target Python '{python}' returned unreadable output: "
            f"{completed.stdout.strip()[:200]!r}"
        ) from exc


def inspect_environment(pypi_names: list[str], refresh: bool = False) -> dict[str, Any]:
    """Read the installed versions of several distributions in the target environment.

    Results are cached per interpreter for the lifetime of the server. A lookup
    that needs the subprocess also reads all registered names (see register_names).

    Args:
        pypi_names: Distribution names as published on PyPI.
        refresh: Drop all cached results for this interpreter and read again.

    Returns:
        Dict with python_executable, python_executable_origin, python_version and
        versions (distribution name mapped to a version string or None).

    Raises:
        TargetEnvironmentError: If the target interpreter cannot be inspected.
    """
    python, _ = resolve_target_python()
    if refresh:
        clear_cache(python)
    cached = _environment_cache.get(python)
    known = cached["versions"] if cached else {}
    if any(name not in known for name in pypi_names):
        missing = sorted((set(pypi_names) | _registered_names) - set(known))
        result = run_in_target(_VERSIONS_SCRIPT, {"names": missing})
        if cached is None:
            cached = {"python_version": result["python_version"], "versions": {}}
            _environment_cache[python] = cached
        cached["versions"].update(result["versions"])
    return {
        **target_fields(),
        "python_version": cached["python_version"],
        "versions": {name: cached["versions"][name] for name in pypi_names},
    }


def environment_fields(pypi_name: str) -> dict[str, Any]:
    """Describe the target environment for one package, without raising.

    Args:
        pypi_name: Distribution name as published on PyPI.

    Returns:
        Dict with installed_version (None if not installed or unknown),
        python_executable and python_executable_origin, plus environment_error
        if the target interpreter could not be inspected.
    """
    try:
        installed = inspect_environment([pypi_name])["versions"][pypi_name]
    except TargetEnvironmentError as exc:
        return {"installed_version": None, **target_fields(), "environment_error": str(exc)}
    return {"installed_version": installed, **target_fields()}


def normalize_version(version: str | None) -> str | None:
    """Clean a requested version: trim spaces and drop a leading "v" (v2.1.0 → 2.1.0).

    Args:
        version: Version as given by the caller, or None.

    Returns:
        The cleaned version, or None if no version was given.
    """
    if version is None or not version.strip():
        return None
    version = version.strip()
    if version[0] in "vV" and version[1:2].isdigit():
        return version[1:]
    return version


def get_distribution_info(pypi_name: str) -> dict[str, Any]:
    """Read version and file locations of one distribution in the target environment.

    Args:
        pypi_name: Distribution name as published on PyPI.

    Returns:
        Dict with installed (bool) and, if installed: version, py_files (absolute
        paths), direct_url (raw direct_url.json text or None) and pth_lines.

    Raises:
        TargetEnvironmentError: If the target interpreter cannot be inspected.
    """
    python, _ = resolve_target_python()
    key = (python, pypi_name)
    if key not in _distribution_cache:
        _distribution_cache[key] = run_in_target(_DISTRIBUTION_SCRIPT, {"name": pypi_name})
    return _distribution_cache[key]


def clear_cache(python: str) -> None:
    """Forget everything cached for one interpreter.

    Args:
        python: Interpreter path whose cached results should be dropped.
    """
    _environment_cache.pop(python, None)
    for key in [k for k in _distribution_cache if k[0] == python]:
        del _distribution_cache[key]
