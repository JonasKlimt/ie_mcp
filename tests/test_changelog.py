"""Changelog: version ranges, release selection, changelog files."""

from __future__ import annotations

import pytest

from core import changelog, github

MARKDOWN = """# Changelog

## [2.0.1] - 2024-02-01
- Fixed a bug

## 2.0.0 (2024-01-05)
- Breaking: removed `lci_calculation`

### v1.9.0
- Old stuff
"""

RST = """Changelog
=========

2.1.0 (2024-03-01)
------------------
* New solver

2.0.0
-----
* Big rewrite
"""


def release(tag: str, body: str = "notes", **extra: object) -> dict:
    return {"tag_name": tag, "published_at": "2024-01-02T10:00:00Z", "body": body, **extra}


@pytest.mark.parametrize(
    "version, lower, upper, expected",
    [
        ("2.0.1", "2.0.0", None, True),
        ("2.0.0", "2.0.0", None, False),  # lower bound is exclusive
        ("v2.0.0", None, "2.0.0", True),  # upper bound is inclusive
        ("2.0.1", None, "2.0.0", False),
        ("1.10.0", "1.9.0", "2.0", True),  # numeric, not alphabetical, comparison
        ("nightly", None, None, True),
        ("nightly", "1.0", None, False),
    ],
)
def test_version_ranges(version: str, lower: str | None, upper: str | None, expected: bool) -> None:
    assert changelog.in_range(version, lower, upper) is expected


@pytest.mark.parametrize(
    "tag, expected",
    [("v2.0.1", "2.0.1"), ("v.2.6.0", "2.6.0"), ("bw2calc-2.0.1", "2.0.1"), ("2.0", "2.0")],
)
def test_odd_release_tags_are_read(tag: str, expected: str) -> None:
    assert str(changelog.parse_version(tag)) == expected
    assert changelog.parse_version("nightly") is None


def test_releases_are_selected_and_sorted() -> None:
    releases = [release("v1.9.0"), release("v2.0.1"), release("v2.0.0"), release("junk")]

    chosen = changelog.select_releases(releases, "1.9.0", None, limit=10)
    limited = changelog.select_releases(releases, None, None, limit=1)

    assert [r["tag_name"] for r in chosen] == ["v2.0.1", "v2.0.0"]
    assert [r["tag_name"] for r in limited] == ["v2.0.1"]


def test_markdown_changelog_is_split_by_version() -> None:
    blocks = changelog.split_changelog(MARKDOWN)

    assert [version for version, _ in blocks] == ["2.0.1", "2.0.0", "1.9.0"]
    assert "Fixed a bug" in blocks[0][1] and "Breaking" not in blocks[0][1]


def test_rst_changelog_is_split_by_version() -> None:
    blocks = changelog.split_changelog(RST)

    assert [version for version, _ in blocks] == ["2.1.0", "2.0.0"]
    assert "New solver" in blocks[0][1]


def test_releases_come_first(monkeypatch: pytest.MonkeyPatch) -> None:
    releases = [release("v2.0.1", "x" * 3000), release("v2.0.0"), release("v1.0", draft=False)]
    monkeypatch.setattr(github, "list_releases", lambda repo: releases)
    monkeypatch.setattr(github, "fetch_raw_text", lambda *a: pytest.fail("no file needed"))

    result = changelog.build_changelog("o/r", "2.0.0", None, "2.0.0")

    assert result["source"] == "github_releases"
    assert [r["version"] for r in result["releases"]] == ["v2.0.1"]
    assert result["releases"][0]["date"] == "2024-01-02"
    assert "cut after" in result["releases"][0]["notes"]  # long notes are shortened


def test_changelog_file_is_the_fallback(monkeypatch: pytest.MonkeyPatch) -> None:
    files = {"CHANGES.md": MARKDOWN}
    monkeypatch.setattr(github, "list_releases", lambda repo: [])
    monkeypatch.setattr(github, "fetch_raw_text", lambda repo, ref, name: files.get(name))

    result = changelog.build_changelog("o/r", "1.9.0", None, "1.9.0")

    assert (result["source"], result["file"]) == ("changelog_file", "CHANGES.md")
    assert [r["version"] for r in result["releases"]] == ["2.0.1", "2.0.0"]


def test_unstructured_file_is_shown_from_the_start(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(github, "list_releases", lambda repo: [])
    monkeypatch.setattr(github, "fetch_raw_text", lambda *a: "just some text")

    result = changelog.build_changelog("o/r", None, None, None)

    assert result["releases"] == [] and result["text"] == "just some text"


def test_nothing_found(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(github, "list_releases", lambda repo: [])
    monkeypatch.setattr(github, "fetch_raw_text", lambda *a: None)

    result = changelog.build_changelog("o/r", None, None, None)

    assert result["source"] is None and "No releases" in result["message"]
