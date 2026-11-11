"""
Fetches documentation pages, converts them to Markdown and caches them on disk.

Pages come from the URLs in the package registry and are stored under
{cache root}/docs/{package}/{version}/{section}.md; the cache root is also used for source files.
"""

from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Any

import httpx
from bs4 import BeautifulSoup
from markdownify import markdownify as _to_md

from .config import setting

ROOT = Path(__file__).resolve().parent.parent
CACHE_DIR_VARIABLE = "IE_MCP_CACHE_DIR"
TTL_VARIABLE = "IE_MCP_DOCS_TTL_DAYS"
SECONDS_PER_DAY = 86400


def cache_root() -> Path:
    """Return the folder that holds all cached docs and source files.

    Uses IE_MCP_CACHE_DIR if set, the repository's .cache folder when the server
    runs from a git clone, and ~/.cache/ie_mcp for installed copies (uvx, pip).

    Returns:
        Path of the cache root folder (it may not exist yet).
    """
    override = os.environ.get(CACHE_DIR_VARIABLE)
    if override:
        return Path(override).expanduser()
    if (ROOT / ".git").exists():
        return ROOT / ".cache"
    return Path.home() / ".cache" / "ie_mcp"


def docs_ttl_days() -> float:
    """Return how many days moving docs ("latest", "stable") stay cached.

    Uses IE_MCP_DOCS_TTL_DAYS if it holds a number, else docs.ttl_days of config.yaml.

    Returns:
        The time to live in days; 0 means always download again.
    """
    try:
        return float(os.environ[TTL_VARIABLE])
    except (KeyError, ValueError):
        return float(setting("docs", "ttl_days"))


def is_stale(path: Path, version: str) -> bool:
    """Tell whether a cached docs file is too old to be served without a check.

    Pinned versions (e.g. "2.0.1") never go stale; moving ones ("latest") do.

    Args:
        path: The cached file.
        version: Docs version slug the file belongs to.

    Returns:
        True if the version is a moving one and the file is older than the TTL.
    """
    if version not in setting("docs", "moving_versions"):
        return False
    age_days = (time.time() - path.stat().st_mtime) / SECONDS_PER_DAY
    return age_days >= docs_ttl_days()


def read_json_cache(path: Path, version: str = "latest") -> Any | None:
    """Read a small JSON helper file (e.g. discovered pages) if it is still fresh.

    Args:
        path: Cache file.
        version: Docs version slug that decides how fresh the file must be.

    Returns:
        The decoded JSON, or None if the file is missing, stale or unreadable.
    """
    if not path.is_file() or is_stale(path, version):
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def write_json_cache(path: Path, data: Any) -> None:
    """Write a small JSON helper file, creating folders as needed.

    Args:
        path: Cache file.
        data: JSON-serialisable content.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data), encoding="utf-8")


_NOISE_SELECTORS = (
    "nav",
    "header",
    "footer",
    ".wy-nav-side",
    ".wy-nav-top",
    ".rst-versions",
    ".ethical-rtd",
    ".admonition-todo",
    "[role='navigation']",
    "script",
    "style",
)

_MAIN_SELECTORS = (
    ".rst-content",
    "div[role='main']",
    "article",
    "main",
    ".document",
)


def html_to_markdown(html: str) -> str:
    """Convert a documentation HTML page to Markdown, without navigation and scripts.

    Args:
        html: Full HTML of the page.

    Returns:
        Markdown of the main content, with links and images stripped.
    """
    soup = BeautifulSoup(html, "html.parser")

    for selector in _NOISE_SELECTORS:
        for tag in soup.select(selector):
            tag.decompose()

    main = None
    for selector in _MAIN_SELECTORS:
        main = soup.select_one(selector)
        if main:
            break

    fragment = str(main) if main else str(soup.body or soup)
    return _to_md(fragment, heading_style="ATX", strip=["a", "img"]).strip()


def cache_path(package: str, section: str, version: str = "latest") -> Path:
    """Return the cache file of one documentation page.

    Args:
        package: Package name.
        section: Section id of the page.
        version: Docs version slug.

    Returns:
        Path of {cache root}/docs/{package}/{version}/{section}.md.
    """
    return cache_root() / "docs" / package / version / f"{section}.md"


def read_cached_page(package: str, section: str, version: str = "latest") -> str | None:
    """Read a documentation page from the cache.

    Args:
        package: Package name.
        section: Section id of the page.
        version: Docs version slug.

    Returns:
        The cached Markdown, or None if the page is not cached.
    """
    path = cache_path(package, section, version)
    return path.read_text(encoding="utf-8") if path.exists() else None


def write_cached_page(package: str, section: str, content: str, version: str = "latest") -> Path:
    """Write a documentation page to the cache.

    Args:
        package: Package name.
        section: Section id of the page.
        content: Markdown text of the page.
        version: Docs version slug.

    Returns:
        Path of the written cache file.
    """
    path = cache_path(package, section, version)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


def fetch_html(url: str, timeout: float | None = None) -> str:
    """Download a page as HTML.

    Args:
        url: URL of the page.
        timeout: Request timeout in seconds; default timeouts.http_seconds.

    Returns:
        The HTML text.

    Raises:
        httpx.HTTPError: If the download fails.
    """
    timeout = timeout or float(setting("timeouts", "http_seconds"))
    response = httpx.get(url, follow_redirects=True, timeout=timeout)
    response.raise_for_status()
    return response.text


def fetch_live_markdown(url: str, timeout: float | None = None) -> str:
    """Download a documentation page and convert it to Markdown.

    Args:
        url: URL of the page.
        timeout: Request timeout in seconds; default timeouts.http_seconds.

    Returns:
        Markdown of the page's main content.

    Raises:
        httpx.HTTPError: If the download fails.
    """
    return html_to_markdown(fetch_html(url, timeout))


def get_or_fetch_page(
    package: str, section: str, url: str, version: str = "latest"
) -> tuple[str, bool]:
    """Return a documentation page from the cache, downloading it when needed.

    A page of a moving version ("latest") is downloaded again once it is older than
    the TTL; if that download fails, the old copy is served instead.

    Args:
        package: Package name.
        section: Section id of the page.
        url: URL of the page.
        version: Docs version slug.

    Returns:
        The Markdown text and whether it came from the cache.

    Raises:
        httpx.HTTPError: If there is no usable cached copy and the download fails.
    """
    cached = read_cached_page(package, section, version)
    if cached is not None and not is_stale(cache_path(package, section, version), version):
        return cached, True

    try:
        content = fetch_live_markdown(url)
    except httpx.HTTPError:
        if cached is not None:
            return cached, True  # offline or site down: an old copy beats nothing
        raise
    write_cached_page(package, section, content, version)
    return content, False


def refresh_page(package: str, section: str, url: str, version: str = "latest") -> str:
    """Download a documentation page again and replace its cache entry.

    Args:
        package: Package name.
        section: Section id of the page.
        url: URL of the page.
        version: Docs version slug.

    Returns:
        The fresh Markdown text.

    Raises:
        httpx.HTTPError: If the download fails.
    """
    content = fetch_live_markdown(url)
    write_cached_page(package, section, content, version)
    return content
