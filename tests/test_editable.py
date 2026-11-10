"""Editable-install fallback, on a tiny fake package built in a temp folder."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from core import local_source


def build_project(root: Path) -> Path:
    """Create a fake src-layout project with one module and some noise folders.

    Args:
        root: Empty folder to build the project in.

    Returns:
        The project folder.
    """
    project = root / "project"
    package = project / "src" / "fakepkg"
    package.mkdir(parents=True)
    (package / "__init__.py").write_text("", encoding="utf-8")
    (package / "core.py").write_text("def answer():\n    return 42\n", encoding="utf-8")
    for noise in (".venv", "build"):
        (project / noise).mkdir()
        (project / noise / "junk.py").write_text("x = 1\n", encoding="utf-8")
    return project


def fake_distribution(project: Path, py_files: list[str], pth_lines: list[str]) -> dict:
    """Build the distribution info of an editable install, as the target reports it.

    Args:
        project: Project folder the install points at.
        py_files: Python files recorded in the distribution itself.
        pth_lines: Lines of the distribution's .pth file.

    Returns:
        Dict in the shape of environment.get_distribution_info().
    """
    direct_url = {"url": project.as_uri(), "dir_info": {"editable": True}}
    return {
        "installed": True,
        "version": "1.0",
        "py_files": py_files,
        "direct_url": json.dumps(direct_url),
        "pth_lines": pth_lines,
    }


def relative_names(installed: local_source.InstalledSource, project: Path) -> list[str]:
    return [file.relative_to(project).as_posix() for file in installed.files]


def test_pth_path_points_at_the_source_folder(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    project = build_project(tmp_path)
    info = fake_distribution(project, [], [str(project / "src")])
    monkeypatch.setattr(local_source, "get_distribution_info", lambda name: info)

    installed = local_source.list_installed_source("fakepkg")

    assert installed.version == "1.0"
    assert relative_names(installed, project) == [
        "src/fakepkg/__init__.py",
        "src/fakepkg/core.py",
    ]
    (match,) = local_source.find_in_files(installed.files, "answer")
    assert match[0].name == "core.py"


def test_direct_url_is_used_when_the_pth_only_installs_an_import_hook(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    project = build_project(tmp_path)
    finder = tmp_path / "site" / "__editable___fakepkg_finder.py"
    finder.parent.mkdir()
    finder.write_text("MAPPING = {}\n", encoding="utf-8")
    pth_lines = ["import __editable___fakepkg_finder; __editable___fakepkg_finder.install()"]
    info = fake_distribution(project, [str(finder)], pth_lines)
    monkeypatch.setattr(local_source, "get_distribution_info", lambda name: info)

    installed = local_source.list_installed_source("fakepkg")

    # the project is walked; .venv and build are skipped; the finder file is not source
    assert relative_names(installed, project) == [
        "src/fakepkg/__init__.py",
        "src/fakepkg/core.py",
    ]


def test_malformed_direct_url_is_ignored(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    module = tmp_path / "mod.py"
    module.write_text("x = 1\n", encoding="utf-8")
    info = fake_distribution(tmp_path, [str(module)], [])
    info["direct_url"] = "{not json"
    monkeypatch.setattr(local_source, "get_distribution_info", lambda name: info)

    assert local_source.list_installed_source("fakepkg").files == [module]


def test_regular_install_uses_the_recorded_files(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    module = tmp_path / "mod.py"
    module.write_text("x = 1\n", encoding="utf-8")
    info = {
        "installed": True,
        "version": "2.0",
        "py_files": [str(module)],
        "direct_url": None,
        "pth_lines": [],
    }
    monkeypatch.setattr(local_source, "get_distribution_info", lambda name: info)

    installed = local_source.list_installed_source("fakepkg")

    assert installed.files == [module]
