"""
Finds more pages of a documentation site than the hand-written sections of a package.

Sphinx sites list their whole table of contents in the sidebar of every page. The
links of one entry page that stay inside the same docs folder are the extra pages;
the result is cached next to the docs pages.
"""

from __future__ import annotations

import logging
import re
from pathlib import Path
from urllib.parse import urljoin, urlsplit, urlunsplit

import httpx
from bs4 import BeautifulSoup

from .cache import cache_root, fetch_html, read_json_cache, write_json_cache
from .config import setting

LOGGER = logging.getLogger("ie_mcp")
_UNSAFE_ID = re.compile(r"[^A-Za-z0-9._-]+")


def docs_root(url: str) -> str:
    """Return the folder URL that a docs page lives in.

    Args:
        url: URL of a docs page, e.g. https://premise.readthedocs.io/en/latest/faq.html.

    Returns:
        The URL of its folder, ending with "/".
    """
    parts = urlsplit(url)
    path = parts.path if parts.path.endswith("/") else parts.path.rsplit("/", 1)[0] + "/"
    return urlunsplit((parts.scheme, parts.netloc, path, "", ""))


def _page_url(href: str, base: str) -> str | None:
    """Turn a link into the URL of a docs page without query and fragment.

    Args:
        href: The href attribute of a link.
        base: URL of the page that holds the link.

    Returns:
        The absolute page URL, or None for links that are not HTML pages.
    """
    parts = urlsplit(urljoin(base, href))
    if parts.scheme not in ("http", "https"):
        return None
    if not (parts.path.endswith(".html") or parts.path.endswith("/")):
        return None
    return urlunsplit((parts.scheme, parts.netloc, parts.path, "", ""))


def links_from_html(html: str, page_url: str, root: str) -> list[tuple[str, str]]:
    """List the docs pages that an HTML page links to inside one docs folder.

    Args:
        html: HTML of the entry page.
        page_url: URL of the entry page, to resolve relative links.
        root: Folder URL that all returned pages must be inside.

    Returns:
        (url, title) pairs in order of appearance, without duplicates and without
        pages such as indexes and source listings.
    """
    skipped = setting("docs", "skipped_path_parts")
    titles: dict[str, str] = {}
    for link in BeautifulSoup(html, "html.parser").select("a[href]"):
        url = _page_url(link["href"], page_url)
        if url is None or not url.startswith(root) or any(part in url for part in skipped):
            continue
        title = link.get_text(" ", strip=True)
        if titles.get(url) in (None, "", "¶"):
            titles[url] = title if title != "¶" else ""
    return list(titles.items())


def page_id(url: str, root: str) -> str:
    """Build a short id for a page from its path inside the docs folder.

    Args:
        url: URL of the page.
        root: Folder URL of the docs.

    Returns:
        The path without ".html" and folder separators replaced, e.g. "api_lca".
    """
    relative = url[len(root) :].removesuffix(".html").removesuffix("/index").strip("/")
    return _UNSAFE_ID.sub("_", relative).strip("_") or "index"


def _unique_id(wanted: str, taken: set[str]) -> str:
    """Make an id unique among the ids already used.

    Args:
        wanted: Preferred id.
        taken: Ids in use; the returned id is added to it.

    Returns:
        The wanted id, or the wanted id with a number appended.
    """
    candidate, number = wanted, 2
    while candidate in taken:
        candidate, number = f"{wanted}_{number}", number + 1
    taken.add(candidate)
    return candidate


def _pages_cache_file(package: str, version: str) -> Path:
    """Return the cache file that holds the discovered pages of a package.

    Args:
        package: Package name.
        version: Docs version slug.

    Returns:
        Path of docs/{package}/{version}/_pages.json under the cache root.
    """
    return cache_root() / "docs" / package / version / "_pages.json"


def _crawl(curated: list[dict[str, str]]) -> list[dict[str, str]]:
    """Read the entry pages of the curated sections and collect the linked pages.

    Args:
        curated: Curated sections with id, title and url.

    Returns:
        New pages (id, title, url), at most docs.max_discovered_pages.
    """
    taken = {page["id"] for page in curated}
    known_urls = {page["url"] for page in curated}
    found: list[dict[str, str]] = []
    entries: dict[str, str] = {}
    for page in curated:
        entries.setdefault(docs_root(page["url"]), page["url"])  # first page of each folder
    for root, entry in entries.items():
        for url, title in links_from_html(fetch_html(entry), entry, root):
            if url in known_urls:
                continue
            known_urls.add(url)
            found.append({"id": _unique_id(page_id(url, root), taken), "title": title, "url": url})
    return found[: int(setting("docs", "max_discovered_pages"))]


def discover_pages(
    package: str, curated: list[dict[str, str]], version: str = "latest"
) -> list[dict[str, str]]:
    """Find the extra documentation pages of a package, using the cache when fresh.

    Discovery is best effort: if the site cannot be read, no extra pages are returned.

    Args:
        package: Package name.
        curated: Curated sections of the package, each with id, title and url.
        version: Docs version slug the URLs belong to.

    Returns:
        Extra pages as dicts with id, title and url; empty if there are none.
    """
    cache_file = _pages_cache_file(package, version)
    cached = read_json_cache(cache_file, version)
    if cached is not None:
        return cached
    try:
        pages = _crawl(curated)
    except (httpx.HTTPError, OSError) as exc:
        LOGGER.warning("Could not discover docs pages of %s: %s", package, exc)
        return []
    write_json_cache(cache_file, pages)
    return pages
