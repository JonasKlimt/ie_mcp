"""
Reads package source code from GitHub at a tag, branch or HEAD (versions not on PyPI).

Takes a repository and a version; the Python files at that ref are downloaded into
.cache/source/{package}/{ref}/. GITHUB_TOKEN is optional and only raises the rate limit.
"""

from __future__ import annotations

import json
import os
import re
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import httpx

from .cache import cache_root
from .config import setting

_GITHUB_API = "https://api.github.com"
_GITHUB_RAW = "https://raw.githubusercontent.com"
MAX_REPOSITORY_FILES = int(setting("limits", "max_repository_files"))
DOWNLOAD_WORKERS = int(setting("workers", "download"))

_synced_refs: set[tuple[str, str]] = set()  # moving refs downloaded in this run


@dataclass
class RefFiles:
    """The Python files of a repository at one git ref.

    Attributes:
        ref: Git ref that was used (tag, branch, commit or "HEAD").
        root: Cache folder that holds the files.
        paths: Absolute paths of the .py files inside the folder.
        truncated: True if the repository has more files than were read.
    """

    ref: str
    root: Path
    paths: list[Path]
    truncated: bool


# ---------------------------------------------------------------------------
# HTTP helpers
# ---------------------------------------------------------------------------


def _headers() -> dict[str, str]:
    """Build the GitHub API request headers.

    Returns:
        Headers, with an Authorization entry if GITHUB_TOKEN is set.
    """
    token = os.environ.get("GITHUB_TOKEN")
    base = {"Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28"}
    if token:
        base["Authorization"] = f"Bearer {token}"
    return base


def _get(url: str, params: dict[str, Any] | None = None, timeout: float = 20.0) -> Any:
    """Fetch a JSON document from the GitHub API.

    Args:
        url: Full URL of the API endpoint.
        params: Query parameters.
        timeout: Request timeout in seconds.

    Returns:
        The decoded JSON document (a dict or a list).

    Raises:
        httpx.HTTPError: If the request fails.
    """
    response = httpx.get(url, headers=_headers(), params=params, timeout=timeout)
    response.raise_for_status()
    return response.json()


# ---------------------------------------------------------------------------
# Tags and refs
# ---------------------------------------------------------------------------


def list_tags(github_repo: str) -> list[str]:
    """List the tag names of a GitHub repository, most recent first.

    Args:
        github_repo: Repository in "owner/repo" format.

    Returns:
        Up to 100 tag names.

    Raises:
        httpx.HTTPError: If the request fails.
    """
    owner, repo = github_repo.split("/", 1)
    data = _get(f"{_GITHUB_API}/repos/{owner}/{repo}/tags", params={"per_page": 100})
    return [item["name"] for item in data]


def list_releases(github_repo: str) -> list[dict[str, Any]]:
    """List the published (non-draft) releases of a GitHub repository, newest first.

    Args:
        github_repo: Repository in "owner/repo" format.

    Returns:
        Release dicts with tag_name, name, published_at, prerelease and body.

    Raises:
        httpx.HTTPError: If the request fails or the rate limit is exceeded.
    """
    owner, repo = github_repo.split("/", 1)
    data = _get(f"{_GITHUB_API}/repos/{owner}/{repo}/releases", params={"per_page": 100})
    return [release for release in data if not release.get("draft")]


def fetch_raw_text(github_repo: str, ref: str, path: str) -> str | None:
    """Download one text file of a repository at a git ref.

    Args:
        github_repo: Repository in "owner/repo" format.
        ref: Tag, branch, commit or "HEAD".
        path: Repository-relative path of the file.

    Returns:
        The file text, or None if the file does not exist at that ref.

    Raises:
        httpx.HTTPError: For any failure other than "not found".
    """
    response = httpx.get(
        f"{_GITHUB_RAW}/{github_repo}/{ref}/{path}", follow_redirects=True, timeout=20.0
    )
    if response.status_code == 404:
        return None
    response.raise_for_status()
    return response.text


def resolve_version_to_tag(github_repo: str, version: str) -> str | None:
    """Find the GitHub tag that matches a version string.

    Tries an exact match first, then with a "v" prefix (2.1.0 → v2.1.0).

    Args:
        github_repo: Repository in "owner/repo" format.
        version: Version string to look for.

    Returns:
        The matching tag name, or None if there is none.

    Raises:
        httpx.HTTPError: If the tag list cannot be fetched.
    """
    tags = list_tags(github_repo)
    if version in tags:
        return version
    prefixed = f"v{version}" if not version.startswith("v") else version
    if prefixed in tags:
        return prefixed
    return None


def resolve_ref(github_repo: str, version: str) -> tuple[str, bool]:
    """Turn a requested version into a git ref.

    Args:
        github_repo: Repository in "owner/repo" format.
        version: Version, tag, branch or commit, or "HEAD" for the default branch.

    Returns:
        The git ref and whether it is a tag. A version without a matching tag is
        returned unchanged, because it may be a branch or a commit.

    Raises:
        httpx.HTTPError: If the tag list cannot be fetched.
    """
    if version.upper() == "HEAD":
        return "HEAD", False
    tag = resolve_version_to_tag(github_repo, version)
    return (tag, True) if tag else (version, False)


# ---------------------------------------------------------------------------
# Files at a ref
# ---------------------------------------------------------------------------


def list_python_paths(github_repo: str, ref: str) -> tuple[list[str], bool]:
    """List the paths of the Python files in a repository at a git ref.

    Args:
        github_repo: Repository in "owner/repo" format.
        ref: Tag, branch, commit or "HEAD".

    Returns:
        Repository-relative paths of at most MAX_REPOSITORY_FILES .py files, and
        whether the repository has more than that.

    Raises:
        httpx.HTTPError: If the ref does not exist or the API call fails.
    """
    tree = _get(f"{_GITHUB_API}/repos/{github_repo}/git/trees/{ref}", params={"recursive": "1"})
    paths = [
        item["path"]
        for item in tree["tree"]
        if item["type"] == "blob" and item["path"].endswith(".py")
    ]
    return paths[:MAX_REPOSITORY_FILES], len(paths) > MAX_REPOSITORY_FILES


def _safe_folder_name(ref: str) -> str:
    """Turn a version or git ref into a name that is safe as one folder.

    Args:
        ref: Version, tag, branch or commit.

    Returns:
        The ref with every character outside letters, digits and "._+-" replaced.

    Raises:
        ValueError: If the ref is empty or contains "..".
    """
    if not ref or ".." in ref:
        raise ValueError(f"'{ref}' is not a valid version or git ref.")
    return re.sub(r"[^A-Za-z0-9._+-]", "_", ref)


def ref_cache_path(package: str, ref: str) -> Path:
    """Return the cache folder for the files of a package at one git ref.

    Args:
        package: Package name (used for the cache directory).
        ref: Tag, branch, commit or "HEAD".

    Returns:
        Path of .cache/source/{package}/{ref}/ (it may not exist yet).

    Raises:
        ValueError: If the ref is not usable as a folder name.
    """
    return cache_root() / "source" / package / _safe_folder_name(ref)


def _tag_index_path(package: str, version: str) -> Path:
    """Return the file that remembers which files a tagged version consists of.

    Args:
        package: Package name (used for the cache directory).
        version: Version as requested by the caller.

    Returns:
        Path of .cache/source/{package}/_index/{version}.json.

    Raises:
        ValueError: If the version is not usable as a file name.
    """
    return cache_root() / "source" / package / "_index" / f"{_safe_folder_name(version)}.json"


def _read_tag_index(package: str, version: str) -> RefFiles | None:
    """Load a fully cached tagged version without calling GitHub.

    Args:
        package: Package name (used for the cache directory).
        version: Version as requested by the caller.

    Returns:
        The cached files, or None if this version was not cached as a tag.

    Raises:
        ValueError: If the version is not usable as a file name.
    """
    index_path = _tag_index_path(package, version)
    if not index_path.is_file():
        return None
    index = json.loads(index_path.read_text(encoding="utf-8"))
    root = ref_cache_path(package, index["ref"])
    return RefFiles(index["ref"], root, [root / p for p in index["paths"]], index["truncated"])


def _download_file(client: httpx.Client, github_repo: str, ref: str, path: str, root: Path) -> None:
    """Download one raw file from GitHub into the cache folder.

    Args:
        client: Open HTTP client.
        github_repo: Repository in "owner/repo" format.
        ref: Tag, branch, commit or "HEAD".
        path: Repository-relative path of the file.
        root: Cache folder of this ref.

    Raises:
        httpx.HTTPError: If the download fails.
    """
    response = client.get(f"{_GITHUB_RAW}/{github_repo}/{ref}/{path}")
    response.raise_for_status()
    target = root / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(response.content)


def fetch_ref_files(package: str, github_repo: str, version: str) -> RefFiles:
    """Download the Python files of a repository at a version into the cache.

    A tag is downloaded once and later served without any GitHub request. A
    branch or HEAD is downloaded again in every server run, because it moves.

    Args:
        package: Package name (used for the cache directory).
        github_repo: Repository in "owner/repo" format.
        version: Version, tag, branch or commit, or "HEAD" for the default branch.

    Returns:
        The git ref that was used and its cached .py files.

    Raises:
        ValueError: If the version is not usable as a folder name.
        httpx.HTTPError: If the ref does not exist or a request fails.
    """
    cached = _read_tag_index(package, version)
    if cached is not None:
        return cached

    ref, is_tag = resolve_ref(github_repo, version)
    root = ref_cache_path(package, ref)
    paths, truncated = list_python_paths(github_repo, ref)
    reuse_cache = is_tag or (github_repo, ref) in _synced_refs
    missing = [path for path in paths if not (reuse_cache and (root / path).is_file())]

    with httpx.Client(follow_redirects=True, timeout=30.0) as client:
        with ThreadPoolExecutor(max_workers=DOWNLOAD_WORKERS) as pool:
            downloads = [
                pool.submit(_download_file, client, github_repo, ref, path, root)
                for path in missing
            ]
            for download in downloads:
                download.result()
    _synced_refs.add((github_repo, ref))
    if is_tag:
        index_path = _tag_index_path(package, version)
        index_path.parent.mkdir(parents=True, exist_ok=True)
        index = {"ref": ref, "paths": paths, "truncated": truncated}
        index_path.write_text(json.dumps(index), encoding="utf-8")
    return RefFiles(ref, root, [root / path for path in paths], truncated)
