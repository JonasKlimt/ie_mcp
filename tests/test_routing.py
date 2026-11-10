"""Version routing: same version → local, other version → PyPI, else GitHub (all mocked)."""

from __future__ import annotations

from pathlib import Path

import pytest

from core import environment, github, pypi, source_lookup
from core.environment import TargetEnvironmentError
from core.local_source import InstalledSource

META = {"name": "fakepkg", "github_repo": "owner/fakepkg"}
INSTALLED = "1.0.0"


@pytest.fixture
def sources(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> dict:
    """Fake one package that exists locally, on PyPI and on GitHub.

    Each origin defines where() with a different body, and remote calls are
    recorded, so a test can tell which origin served a lookup.

    Returns:
        Dict with "calls" (list of remote calls) and "installed" (settable version).
    """
    state = {"calls": [], "installed": INSTALLED, "truncated": False}

    def write(origin: str) -> Path:
        root = tmp_path / origin
        (root / "fakepkg").mkdir(parents=True)
        file = root / "fakepkg" / "mod.py"
        file.write_text(f"def where():\n    return '{origin}'\n", encoding="utf-8")
        return root

    roots = {origin: write(origin) for origin in ("local", "pypi", "github")}

    def fake_environment(names: list[str], refresh: bool = False) -> dict:
        return {
            "python_version": "3.12",
            "versions": {name: state["installed"] for name in names},
        }

    def fake_installed(name: str) -> InstalledSource:
        return InstalledSource(INSTALLED, [roots["local"] / "fakepkg" / "mod.py"])

    def fake_release(name: str, version: str) -> Path:
        state["calls"].append(("pypi", version))
        if version == "9.9.9":
            raise pypi.VersionNotOnPyPI("not on PyPI")
        return roots["pypi"]

    def fake_ref(package: str, repo: str, version: str) -> github.RefFiles:
        state["calls"].append(("github", version))
        paths = [roots["github"] / "fakepkg" / "mod.py"]
        return github.RefFiles(f"ref-{version}", roots["github"], paths, state["truncated"])

    monkeypatch.setenv(environment.TARGET_VARIABLE, "/target/python")
    monkeypatch.setattr(environment, "inspect_environment", fake_environment)
    monkeypatch.setattr(source_lookup, "list_installed_source", fake_installed)
    monkeypatch.setattr(pypi, "fetch_release", fake_release)
    monkeypatch.setattr(pypi, "latest_version", lambda name: "2.0.0")
    monkeypatch.setattr(github, "fetch_ref_files", fake_ref)
    return state


def lookup(version: str | None) -> dict:
    return source_lookup.get_function_source("fakepkg", META, "where", version, "full")


@pytest.mark.parametrize("version", [None, "", INSTALLED, f"v{INSTALLED}", f" {INSTALLED} "])
def test_no_version_or_installed_version_is_read_locally(sources: dict, version: str) -> None:
    result = lookup(version)

    assert result["source"] == "local"
    assert result["version"] == result["installed_version"] == INSTALLED
    assert "'local'" in result["code"]
    assert result["python_executable"] == "/target/python"
    assert sources["calls"] == []


def test_other_version_is_read_from_pypi(sources: dict) -> None:
    result = lookup("v0.9.0")

    assert result["source"] == "pypi"
    assert result["version"] == "0.9.0"
    assert result["installed_version"] == INSTALLED
    assert result["file"] == "fakepkg/mod.py"
    assert "'pypi'" in result["code"]
    assert sources["calls"] == [("pypi", "0.9.0")]


def test_latest_is_resolved_to_a_version_number(sources: dict) -> None:
    result = lookup("latest")

    assert (result["source"], result["version"]) == ("pypi", "2.0.0")


def test_version_missing_on_pypi_falls_back_to_github(sources: dict) -> None:
    result = lookup("9.9.9")

    assert result["source"] == "github"
    assert result["version"] == "ref-9.9.9"
    assert result["pypi_error"] == "not on PyPI"
    assert result["html_url"] == "https://github.com/owner/fakepkg/blob/ref-9.9.9/fakepkg/mod.py#L1"
    assert sources["calls"] == [("pypi", "9.9.9"), ("github", "9.9.9")]


def test_failed_pypi_download_falls_back_to_github(
    sources: dict, monkeypatch: pytest.MonkeyPatch
) -> None:
    def broken_release(name: str, version: str) -> Path:
        raise ValueError("Checksum mismatch")

    monkeypatch.setattr(pypi, "fetch_release", broken_release)

    result = lookup("0.9.0")

    assert result["source"] == "github"
    assert "Checksum mismatch" in result["pypi_error"]


def test_truncated_repository_is_reported(sources: dict) -> None:
    sources["truncated"] = True

    assert "only the first" in lookup("HEAD")["warning"]
    assert "warning" not in lookup(None)


def test_path_like_version_never_reaches_the_cache() -> None:
    with pytest.raises(pypi.VersionNotOnPyPI):
        pypi.fetch_release("fakepkg", "../../outside")
    with pytest.raises(ValueError):
        github.ref_cache_path("fakepkg", "../outside")


def test_head_goes_straight_to_github(sources: dict) -> None:
    result = lookup("HEAD")

    assert result["source"] == "github"
    assert sources["calls"] == [("github", "HEAD")]


def test_not_installed_without_version_asks_instead_of_guessing(sources: dict) -> None:
    sources["installed"] = None

    result = lookup(None)

    assert result["status"] == "not_installed"
    assert result["installed_version"] is None
    assert "/target/python" in result["message"] and "ask" in result["message"]
    assert "code" not in result
    assert sources["calls"] == []


def test_not_installed_with_version_uses_pypi(sources: dict) -> None:
    sources["installed"] = None

    result = lookup("0.9.0")

    assert result["source"] == "pypi"
    assert result["installed_version"] is None


def test_broken_target_environment(sources: dict, monkeypatch: pytest.MonkeyPatch) -> None:
    def broken_environment(names: list[str], refresh: bool = False) -> dict:
        raise TargetEnvironmentError("Target Python interpreter not found")

    monkeypatch.setattr(environment, "inspect_environment", broken_environment)

    assert "not found" in lookup(None)["error"]

    remote = lookup("0.9.0")
    assert remote["source"] == "pypi"
    assert remote["installed_version"] is None
    assert "not found" in remote["environment_error"]


def test_search_follows_the_same_routing(sources: dict) -> None:
    local = source_lookup.search_source("fakepkg", META, "RETURN", None)
    remote = source_lookup.search_source("fakepkg", META, "return", "0.9.0")
    nothing = source_lookup.search_source("fakepkg", META, "no such text", None)

    assert (local[0]["source"], local[0]["line"], local[0]["text"]) == (
        "local",
        2,
        "return 'local'",
    )
    assert (remote[0]["source"], remote[0]["version"]) == ("pypi", "0.9.0")
    assert remote[0]["file"] == "fakepkg/mod.py"
    assert nothing[0]["message"] and nothing[0]["source"] == "local"
