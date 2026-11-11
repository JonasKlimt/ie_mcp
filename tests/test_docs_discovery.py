"""Discovery of extra documentation pages from the links of an entry page."""

from __future__ import annotations

import httpx
import pytest

from core import docs_discovery
from core.config import setting

ROOT = "https://premise.readthedocs.io/en/latest/"
ENTRY = ROOT + "introduction.html"
CURATED = [{"id": "introduction", "title": "In a nutshell", "url": ENTRY}]
HTML = """
<nav>
  <a href="introduction.html">In a nutshell</a>
  <a href="transform.html#electricity">TRANSFORM</a>
  <a href="transform.html">¶</a>
  <a href="api/index.html">API</a>
  <a href="faq.html">FAQ</a>
  <a href="https://other.org/en/latest/elsewhere.html">external</a>
  <a href="../../other/page.html">outside the folder</a>
  <a href="_modules/premise.html">source</a>
  <a href="genindex.html">Index</a>
  <a href="mailto:someone@example.org">mail</a>
  <a href="_static/style.css">css</a>
</nav>
"""


def test_docs_root_is_the_folder_of_the_page() -> None:
    assert docs_discovery.docs_root(ENTRY) == ROOT
    assert docs_discovery.docs_root(ROOT) == ROOT
    bw2calc = "https://docs.brightway.dev/en/latest/content/api/bw2calc/index.html"
    assert docs_discovery.docs_root(bw2calc) == (
        "https://docs.brightway.dev/en/latest/content/api/bw2calc/"
    )


def test_links_stay_inside_the_folder_and_skip_noise() -> None:
    links = docs_discovery.links_from_html(HTML, ENTRY, ROOT)

    assert links == [
        (ROOT + "introduction.html", "In a nutshell"),
        (ROOT + "transform.html", "TRANSFORM"),  # the anchor link's title wins over "¶"
        (ROOT + "api/index.html", "API"),
        (ROOT + "faq.html", "FAQ"),
    ]


@pytest.mark.parametrize(
    "path, expected",
    [
        ("faq.html", "faq"),
        ("api/index.html", "api"),
        ("content/api/bw2calc.lca.html", "content_api_bw2calc.lca"),
        ("", "index"),
    ],
)
def test_page_ids(path: str, expected: str) -> None:
    assert docs_discovery.page_id(ROOT + path, ROOT) == expected


def test_new_pages_are_found_and_cached(monkeypatch: pytest.MonkeyPatch) -> None:
    calls = []
    monkeypatch.setattr(docs_discovery, "fetch_html", lambda url: calls.append(url) or HTML)

    first = docs_discovery.discover_pages("premise", CURATED)
    second = docs_discovery.discover_pages("premise", CURATED)

    assert [page["id"] for page in first] == ["transform", "api", "faq"]  # curated one excluded
    assert first[0] == {"id": "transform", "title": "TRANSFORM", "url": ROOT + "transform.html"}
    assert second == first
    assert calls == [ENTRY]  # the second call came from the cache


def test_ids_do_not_clash_with_curated_sections(monkeypatch: pytest.MonkeyPatch) -> None:
    curated = [{"id": "faq", "title": "FAQ", "url": ROOT + "other.html"}]
    monkeypatch.setattr(docs_discovery, "fetch_html", lambda url: HTML)

    ids = [page["id"] for page in docs_discovery.discover_pages("premise", curated)]

    assert "faq_2" in ids and "faq" not in ids


def test_unreachable_site_gives_no_extra_pages(monkeypatch: pytest.MonkeyPatch) -> None:
    def down(url: str) -> str:
        raise httpx.ConnectError("offline")

    monkeypatch.setattr(docs_discovery, "fetch_html", down)

    assert docs_discovery.discover_pages("premise", CURATED) == []


def test_number_of_pages_is_limited(monkeypatch: pytest.MonkeyPatch) -> None:
    many = "".join(f'<a href="page{n}.html">Page {n}</a>' for n in range(100))
    monkeypatch.setattr(docs_discovery, "fetch_html", lambda url: many)

    pages = docs_discovery.discover_pages("premise", CURATED)

    assert len(pages) == setting("docs", "max_discovered_pages")
