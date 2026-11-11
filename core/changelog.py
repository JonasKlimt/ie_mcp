"""
Builds "what changed between two versions" from GitHub releases or a changelog file.

GitHub releases are used when a repository has them; otherwise the first changelog
file found in the repository (CHANGELOG.md, HISTORY.rst, ...) is split by version.
"""

from __future__ import annotations

import re
from typing import Any

from packaging.version import InvalidVersion, Version

from . import github
from .config import setting

_TAG_PREFIX = re.compile(r"^[vV]\.?")
_DOTTED_VERSION = re.compile(r"\d+(?:\.\d+)+(?:(?:a|b|rc|dev|post)\d+)?")
# "## 2.0.1 (2024-01-05)", "## [2.0.1] - 2024", "### v2.0.1"
_MARKDOWN_HEADING = re.compile(r"^#{1,4}\s*\[?v?(\d+(?:\.\d+)+[\w.+-]*)\]?")
# an RST title such as "2.0.1 (2024-01-05)" is followed by an underline of = - ~ ^
_RST_TITLE = re.compile(r"^v?(\d+(?:\.\d+)+[\w.+-]*)(?:\s.*)?$")
_RST_UNDERLINE = re.compile(r"^([=\-~^#*])\1{2,}\s*$")


def parse_version(text: str) -> Version | None:
    """Read a version from a release tag such as "v2.0.1", "v.2.0.1" or "bw2calc-2.0.1".

    Args:
        text: Tag or version string.

    Returns:
        The parsed version, or None if the text holds no version.
    """
    text = _TAG_PREFIX.sub("", text.strip())
    try:
        return Version(text)
    except InvalidVersion:
        pass
    found = _DOTTED_VERSION.search(text)  # e.g. a package name in front of the number
    try:
        return Version(found.group(0)) if found else None
    except InvalidVersion:
        return None


def in_range(version: str, lower: str | None, upper: str | None) -> bool:
    """Tell whether a version is newer than `lower` and not newer than `upper`.

    Args:
        version: Version to test.
        lower: Exclusive lower bound, or None.
        upper: Inclusive upper bound, or None.

    Returns:
        True if it is inside the range; versions that cannot be parsed are only
        inside when both bounds are None.
    """
    parsed = parse_version(version)
    if parsed is None:
        return lower is None and upper is None
    low, high = parse_version(lower or ""), parse_version(upper or "")
    return (low is None or parsed > low) and (high is None or parsed <= high)


def _release_entry(release: dict[str, Any], notes_chars: int) -> dict[str, Any]:
    """Shorten a GitHub release to the fields shown to the user.

    Args:
        release: One item of the GitHub releases API.
        notes_chars: Maximum number of characters of the notes.

    Returns:
        Dict with version, date, prerelease and notes (cut with a marker if long).
    """
    notes = (release.get("body") or "").strip()
    if len(notes) > notes_chars:
        notes = notes[:notes_chars] + f"\n[... cut after {notes_chars} characters]"
    return {
        "version": release["tag_name"],
        "date": (release.get("published_at") or "")[:10],
        "prerelease": bool(release.get("prerelease")),
        "notes": notes,
    }


def select_releases(
    releases: list[dict[str, Any]], lower: str | None, upper: str | None, limit: int
) -> list[dict[str, Any]]:
    """Pick the releases inside a version range, newest first.

    Args:
        releases: Items of the GitHub releases API.
        lower: Exclusive lower bound, or None.
        upper: Inclusive upper bound, or None.
        limit: Maximum number of releases to return.

    Returns:
        The matching releases as returned by the API, at most `limit`.
    """
    chosen = [r for r in releases if in_range(r["tag_name"], lower, upper)]
    chosen.sort(key=lambda r: parse_version(r["tag_name"]) or Version("0"), reverse=True)
    return chosen[:limit]


def _version_heading(line: str, next_line: str) -> str | None:
    """Read the version from a changelog heading, in Markdown or RST style.

    Args:
        line: A line of the changelog.
        next_line: The line below it (RST underlines are detected there).

    Returns:
        The version text, or None if the line is not a version heading.
    """
    markdown = _MARKDOWN_HEADING.match(line)
    if markdown:
        return markdown.group(1)
    rst = _RST_TITLE.match(line.strip())
    if rst and _RST_UNDERLINE.match(next_line):
        return rst.group(1)
    return None


def split_changelog(text: str) -> list[tuple[str, str]]:
    """Cut a changelog file into one block per version.

    Args:
        text: Content of a Markdown or RST changelog.

    Returns:
        (version, block text) pairs in file order; empty if no version heading is found.
    """
    lines = text.splitlines()
    starts = [
        (index, version)
        for index, line in enumerate(lines)
        if (version := _version_heading(line, lines[index + 1] if index + 1 < len(lines) else ""))
    ]
    blocks = []
    for position, (index, version) in enumerate(starts):
        end = starts[position + 1][0] if position + 1 < len(starts) else len(lines)
        blocks.append((version, "\n".join(lines[index:end]).strip()))
    return blocks


def _file_entries(
    text: str, lower: str | None, upper: str | None, limit: int, notes_chars: int
) -> list[dict[str, Any]]:
    """Turn a changelog file into release-like entries inside a version range.

    Args:
        text: Content of the changelog file.
        lower: Exclusive lower bound, or None.
        upper: Inclusive upper bound, or None.
        limit: Maximum number of entries.
        notes_chars: Maximum number of characters per entry.

    Returns:
        Dicts with version and notes; empty if the file has no version headings.
    """
    blocks = [(v, b) for v, b in split_changelog(text) if in_range(v, lower, upper)]
    return [{"version": v, "notes": b[:notes_chars]} for v, b in blocks[:limit]]


def read_changelog_file(github_repo: str, ref: str) -> tuple[str, str] | None:
    """Download the first changelog file that exists in a repository at a ref.

    Args:
        github_repo: Repository in "owner/repo" format.
        ref: Tag, branch or "HEAD".

    Returns:
        (file name, text), or None if none of the configured names exists.

    Raises:
        httpx.HTTPError: If a request fails for another reason than "not found".
    """
    for name in setting("changelog", "file_names"):
        text = github.fetch_raw_text(github_repo, ref, name)
        if text is not None:
            return name, text
    return None


def build_changelog(
    github_repo: str, lower: str | None, upper: str | None, installed: str | None
) -> dict[str, Any]:
    """Collect the changes between two versions of a package.

    Args:
        github_repo: Repository in "owner/repo" format.
        lower: Exclusive lower bound, or None.
        upper: Inclusive upper bound, or None.
        installed: Installed version, used to say whether `lower` was its default.

    Returns:
        Dict with source ("github_releases", "changelog_file" or None), releases
        and, if nothing was found, a message.

    Raises:
        httpx.HTTPError: If GitHub cannot be reached or the rate limit is exceeded.
    """
    limit = int(setting("limits", "changelog_releases"))
    notes_chars = int(setting("limits", "changelog_notes_chars"))
    if lower is None and upper is None and installed is None:
        limit = int(setting("limits", "changelog_default_releases"))

    releases = github.list_releases(github_repo)
    if releases:
        chosen = select_releases(releases, lower, upper, limit)
        entries = [_release_entry(release, notes_chars) for release in chosen]
        return {"source": "github_releases", "releases": entries}

    found = read_changelog_file(github_repo, upper or "HEAD") or read_changelog_file(
        github_repo, "HEAD"
    )
    if found is None:
        return {"source": None, "releases": [], "message": "No releases or changelog file found."}
    name, text = found
    entries = _file_entries(text, lower, upper, limit, notes_chars)
    if entries:
        return {"source": "changelog_file", "file": name, "releases": entries}
    head = text[: int(setting("limits", "changelog_file_chars"))]
    return {
        "source": "changelog_file",
        "file": name,
        "releases": [],
        "text": head,
        "message": f"{name} has no version headings in range; its start is shown.",
    }
