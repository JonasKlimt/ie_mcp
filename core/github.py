"""
GitHub API helpers for fetching and searching package source code.

Uses the GitHub REST API to:
  - List repository tags (for version validation)
  - Search code within a repository (find which file a function lives in)
  - Fetch raw file contents at any tag/ref (base64-decoded via the contents API)
  - Extract a specific function's source using Python's ast module

Authentication:
  Set the GITHUB_TOKEN environment variable for 5000 req/hr.
  Without it the server falls back to unauthenticated (60 req/hr).

Cache:
  Raw source files are cached under .cache/source/{package}/{ref}/{path}.py
  so default-branch and versioned files are stored separately.
"""

from __future__ import annotations

import ast
import base64
import os
import textwrap
from pathlib import Path

import httpx


_GITHUB_API = "https://api.github.com"
ROOT = Path(__file__).resolve().parent.parent
SOURCE_CACHE_ROOT = ROOT / ".cache" / "source"

# ---------------------------------------------------------------------------
# HTTP helpers
# ---------------------------------------------------------------------------


def _headers() -> dict[str, str]:
    token = os.environ.get("GITHUB_TOKEN")
    base = {"Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28"}
    if token:
        base["Authorization"] = f"Bearer {token}"
    return base


def _get(url: str, params: dict | None = None, timeout: float = 20.0) -> dict | list:
    response = httpx.get(url, headers=_headers(), params=params, timeout=timeout)
    response.raise_for_status()
    return response.json()


# ---------------------------------------------------------------------------
# Cache helpers  (keyed by ref so default-branch and versioned files coexist)
# ---------------------------------------------------------------------------


def _source_cache_path(package: str, file_path: str, ref: str = "HEAD") -> Path:
    # Sanitise ref so it is safe as a directory name (e.g. "v2.1.0" → "v2.1.0")
    safe_ref = ref.replace("/", "_")
    return SOURCE_CACHE_ROOT / package / safe_ref / file_path


def _read_source_cache(package: str, file_path: str, ref: str = "HEAD") -> str | None:
    path = _source_cache_path(package, file_path, ref)
    if path.exists():
        return path.read_text(encoding="utf-8")
    # Backward-compat: old cache had no ref subdirectory
    if ref == "HEAD":
        old_path = SOURCE_CACHE_ROOT / package / file_path
        if old_path.exists():
            return old_path.read_text(encoding="utf-8")
    return None


def _write_source_cache(package: str, file_path: str, content: str, ref: str = "HEAD") -> None:
    path = _source_cache_path(package, file_path, ref)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


# ---------------------------------------------------------------------------
# GitHub API calls
# ---------------------------------------------------------------------------


def list_tags(github_repo: str) -> list[str]:
    """
    Return all tag names for a GitHub repository, most recent first.

    Args:
        github_repo: Repository in "owner/repo" format.
    """
    owner, repo = github_repo.split("/", 1)
    data = _get(f"{_GITHUB_API}/repos/{owner}/{repo}/tags", params={"per_page": 100})
    return [item["name"] for item in data]


def resolve_version_to_tag(github_repo: str, version: str) -> str | None:
    """
    Find a GitHub tag that matches the requested version string.

    Tries exact match first, then with a 'v' prefix (e.g. '2.1.0' → 'v2.1.0').
    Returns the matching tag name, or None if not found.
    """
    tags = list_tags(github_repo)
    if version in tags:
        return version
    prefixed = f"v{version}" if not version.startswith("v") else version
    if prefixed in tags:
        return prefixed
    return None


def search_code(github_repo: str, query: str) -> list[dict]:
    """
    Search for code in a GitHub repository (always searches the default branch).

    Returns a list of results with keys: name, path, url, html_url.
    At most 10 results.

    Args:
        github_repo: Repository in "owner/repo" format.
        query:       Search string (e.g. a function name or keyword).
    """
    data = _get(
        f"{_GITHUB_API}/search/code",
        params={"q": f"{query} repo:{github_repo}", "per_page": 10},
    )
    items = data.get("items", [])
    return [
        {
            "name": item["name"],
            "path": item["path"],
            "url": item["url"],
            "html_url": item["html_url"],
        }
        for item in items
    ]


def get_file_source(package: str, github_repo: str, file_path: str, ref: str = "HEAD") -> str:
    """
    Fetch the raw source of a file from GitHub at a specific ref, with caching.

    Args:
        package:     Package name (used for cache directory).
        github_repo: Repository in "owner/repo" format.
        file_path:   Path to the file within the repository.
        ref:         Git ref (tag, branch, or commit SHA). Defaults to HEAD.
    """
    cached = _read_source_cache(package, file_path, ref)
    if cached is not None:
        return cached

    owner, repo = github_repo.split("/", 1)
    params = {"ref": ref} if ref != "HEAD" else None
    data = _get(f"{_GITHUB_API}/repos/{owner}/{repo}/contents/{file_path}", params=params)
    if isinstance(data, dict) and data.get("encoding") == "base64":
        content = base64.b64decode(data["content"]).decode("utf-8")
    else:
        raise ValueError(f"Unexpected response format for '{file_path}' at ref '{ref}'")

    _write_source_cache(package, file_path, content, ref)
    return content


# ---------------------------------------------------------------------------
# AST-based function extraction
# ---------------------------------------------------------------------------


def extract_function(source: str, function_name: str) -> str | None:
    """
    Extract the source code of a named function or method from Python source.

    Searches top-level functions first, then methods inside any class.
    Returns the dedented source string, or None if not found.
    """
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return None

    lines = source.splitlines(keepends=True)

    def _node_source(node: ast.AST) -> str:
        start = node.lineno - 1
        end = node.end_lineno
        return textwrap.dedent("".join(lines[start:end]))

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
            if node.name == function_name:
                return _node_source(node)

    return None


def find_and_extract_function(
    package: str,
    github_repo: str,
    function_name: str,
    version: str | None = None,
) -> dict:
    """
    Search a repository for a function by name, fetch the file (optionally at a
    specific version tag), and return its source code plus metadata.

    Workflow:
      1. Search the default branch to find which file contains the function.
      2. If a version is given, validate it against GitHub tags.
      3. Fetch that file at the resolved tag ref.
      4. Extract the function via AST.

    Returns a dict with keys: function, file, html_url, version, source.
    On failure, returns a dict with an "error" key.
    """
    # Step 1: find file via code search (always on default branch)
    try:
        results = search_code(github_repo, function_name)
    except httpx.HTTPStatusError as exc:
        return {"error": f"GitHub API error during search: {exc}"}

    if not results:
        return {"error": f"No files found containing '{function_name}' in {github_repo}."}

    # Step 2: resolve version to a tag ref
    ref = "HEAD"
    resolved_tag = None
    if version:
        try:
            resolved_tag = resolve_version_to_tag(github_repo, version)
        except httpx.HTTPStatusError as exc:
            return {"error": f"GitHub API error fetching tags: {exc}"}
        if resolved_tag is None:
            try:
                available = list_tags(github_repo)[:20]
            except Exception:  # noqa: BLE001
                available = []
            return {
                "error": (
                    f"Version '{version}' not found as a GitHub tag in {github_repo}. "
                    f"Available tags (up to 20): {available}"
                )
            }
        ref = resolved_tag

    # Step 3 & 4: fetch file at ref and extract function
    for item in results:
        file_path = item["path"]
        if not file_path.endswith(".py"):
            continue
        try:
            source = get_file_source(package, github_repo, file_path, ref)
        except httpx.HTTPStatusError as exc:
            if exc.response.status_code == 404:
                # File may not have existed at this version — try next candidate
                continue
            return {"error": f"GitHub API error fetching '{file_path}' at '{ref}': {exc}"}
        except Exception:  # noqa: BLE001
            continue

        fn_source = extract_function(source, function_name)
        if fn_source:
            return {
                "function": function_name,
                "file": file_path,
                "version": resolved_tag or "latest",
                "html_url": item["html_url"],
                "source": fn_source,
            }

    # Function not found in any candidate file at the requested ref
    searched = [r["path"] for r in results if r["path"].endswith(".py")][:5]
    if version and resolved_tag:
        return {
            "error": (
                f"Function '{function_name}' was not found at version '{resolved_tag}'. "
                f"It may not have existed yet or may have had a different name. "
                f"Files checked: {searched}"
            )
        }
    return {
        "error": (
            f"Found files mentioning '{function_name}' but could not extract "
            f"the function definition. It may be defined dynamically or in a "
            f"non-standard way. Files searched: {searched}"
        )
    }
