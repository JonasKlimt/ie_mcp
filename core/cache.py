"""
Local cache and live-fetch helpers for package documentation.

The cache keeps the repo small while making repeated questions fast.
Docs are fetched from the package's official documentation when needed and
stored under .cache/docs/{package}/{section}.md.
"""

from __future__ import annotations

from pathlib import Path

import httpx
from bs4 import BeautifulSoup
from markdownify import markdownify as _to_md


ROOT = Path(__file__).resolve().parent.parent
CACHE_ROOT = ROOT / ".cache" / "docs"

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
    return CACHE_ROOT / package / version / f"{section}.md"


def read_cached_page(package: str, section: str, version: str = "latest") -> str | None:
    path = cache_path(package, section, version)
    if path.exists():
        return path.read_text(encoding="utf-8")
    # Backward-compat: old cache had no version subdirectory for 'latest'
    if version == "latest":
        old_path = CACHE_ROOT / package / f"{section}.md"
        if old_path.exists():
            return old_path.read_text(encoding="utf-8")
    return None


def write_cached_page(package: str, section: str, content: str, version: str = "latest") -> Path:
    path = cache_path(package, section, version)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


def fetch_live_markdown(url: str, timeout: float = 30.0) -> str:
    response = httpx.get(url, follow_redirects=True, timeout=timeout)
    response.raise_for_status()
    return html_to_markdown(response.text)


def get_or_fetch_page(package: str, section: str, url: str, version: str = "latest") -> tuple[str, bool]:
    cached = read_cached_page(package, section, version)
    if cached is not None:
        return cached, True

    content = fetch_live_markdown(url)
    write_cached_page(package, section, content, version)
    return content, False


def refresh_page(package: str, section: str, url: str, version: str = "latest") -> str:
    content = fetch_live_markdown(url)
    write_cached_page(package, section, content, version)
    return content
