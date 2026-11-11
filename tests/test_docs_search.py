"""Docs search: chunking, tokenising and ranking."""

from __future__ import annotations

from core.docs_search import Chunk, chunk_markdown, rank_chunks, tokenize

PAGE = """# Title

Intro text.

## Contribution analysis

Use the analyzer to find the top activities that contribute to a score.

## Installation

Install the package with pip. Contribution is not covered here.
"""


def test_tokenize_splits_identifiers() -> None:
    assert tokenize("get_node(Name)") == ["get_node", "get", "node", "name"]


def test_chunks_keep_their_heading() -> None:
    chunks = chunk_markdown("intro", PAGE)

    assert [(c.heading, c.text[:12]) for c in chunks] == [
        ("Title", "Intro text."),
        ("Contribution analysis", "Use the anal"),
        ("Installation", "Install the "),
    ]
    assert all(c.section == "intro" for c in chunks)


def test_permalink_icons_are_removed_from_headings() -> None:
    chunks = chunk_markdown("page", "## IAM data access\n\nText.")

    assert chunks[0].heading == "IAM data access"


def test_heading_and_phrase_matches_rank_first() -> None:
    chunks = chunk_markdown("intro", PAGE)

    ranked = rank_chunks(chunks, "contribution analysis", limit=5)

    assert ranked[0][1].heading == "Contribution analysis"
    assert [score for score, _ in ranked] == sorted((s for s, _ in ranked), reverse=True)


def test_rare_words_weigh_more_than_common_ones() -> None:
    chunks = [
        Chunk("a", "", "the the the matrix"),
        Chunk("a", "", "the the the the the"),
        Chunk("a", "", "the sparse solver"),
    ]

    ranked = rank_chunks(chunks, "the solver", limit=3)

    assert ranked[0][1].text == "the sparse solver"


def test_limit_and_no_match() -> None:
    chunks = [Chunk("a", "", f"lci number {n}") for n in range(5)]

    assert len(rank_chunks(chunks, "lci", limit=2)) == 2
    assert rank_chunks(chunks, "zzz", limit=2) == []
    assert rank_chunks(chunks, "   ", limit=2) == []
    assert rank_chunks([], "lci", limit=2) == []
