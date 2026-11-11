"""
Ranks documentation paragraphs for a free-text query (BM25 style, no extra dependencies).

Pages are cut into paragraph chunks that remember their heading; the best-scoring
chunks over all pages of a package are returned.
"""

from __future__ import annotations

import math
import re
from collections import Counter
from dataclasses import dataclass

from .config import setting

_WORD = re.compile(r"[a-z0-9_]+")
_BLOCK_SEPARATOR = re.compile(r"\n\s*\n")
_ICON_CHARS = re.compile("[-¶]")  # permalink icons that Sphinx themes add to headings


@dataclass
class Chunk:
    """One paragraph of a documentation page.

    Attributes:
        section: Id of the page the paragraph belongs to.
        heading: Nearest heading above the paragraph ("" if none).
        text: The paragraph text.
    """

    section: str
    heading: str
    text: str


def tokenize(text: str) -> list[str]:
    """Split text into lower-case words; identifiers like get_node also give get and node.

    Args:
        text: Any text.

    Returns:
        The words, in order of appearance.
    """
    tokens: list[str] = []
    for word in _WORD.findall(text.lower()):
        tokens.append(word)
        if "_" in word:
            tokens.extend(part for part in word.split("_") if part)
    return tokens


def chunk_markdown(section: str, markdown: str) -> list[Chunk]:
    """Cut a Markdown page into paragraph chunks that keep their heading.

    Args:
        section: Id of the page.
        markdown: Markdown text of the page.

    Returns:
        One chunk per non-empty paragraph; headings themselves are not chunks.
    """
    chunks: list[Chunk] = []
    heading = ""
    for block in _BLOCK_SEPARATOR.split(markdown):
        lines = block.strip().splitlines()
        if lines and lines[0].startswith("#"):
            heading = _ICON_CHARS.sub("", lines[0].lstrip("#")).strip(" #")
            lines = lines[1:]  # the rest of the block is a paragraph under the heading
        text = "\n".join(lines).strip()
        if text:
            chunks.append(Chunk(section, heading, text))
    return chunks


def _idf(total: int, containing: int) -> float:
    """Compute the inverse document frequency of a term.

    Args:
        total: Number of chunks.
        containing: Number of chunks that hold the term.

    Returns:
        A positive weight that is higher for rarer terms.
    """
    return math.log(1 + (total - containing + 0.5) / (containing + 0.5))


def _score(
    chunk: Chunk,
    counts: Counter[str],
    length: int,
    average_length: float,
    query: str,
    weights: dict[str, float],
) -> float:
    """Score one chunk against the query.

    Args:
        chunk: The paragraph.
        counts: Word counts of the heading plus paragraph.
        length: Number of words of the heading plus paragraph.
        average_length: Average number of words over all chunks.
        query: The query text as typed.
        weights: idf weight of every query word.

    Returns:
        The score; 0 if no query word occurs.
    """
    k1, b = float(setting("search", "bm25_k1")), float(setting("search", "bm25_b"))
    score = 0.0
    for term, weight in weights.items():
        frequency = counts.get(term, 0)
        if frequency:
            norm = frequency + k1 * (1 - b + b * length / average_length)
            score += weight * frequency * (k1 + 1) / norm
    if score == 0:
        return 0.0
    if query.lower() in chunk.text.lower():
        score += float(setting("search", "phrase_bonus"))
    heading_words = set(tokenize(chunk.heading))
    score += float(setting("search", "heading_bonus")) * len(heading_words & set(weights))
    return score


def rank_chunks(chunks: list[Chunk], query: str, limit: int) -> list[tuple[float, Chunk]]:
    """Return the chunks that match a query best.

    Args:
        chunks: Chunks of all pages to search.
        query: Free-text query.
        limit: Maximum number of chunks to return.

    Returns:
        (score, chunk) pairs, best first; empty if nothing matches.
    """
    terms = set(tokenize(query))
    if not terms or not chunks:
        return []
    counted = [Counter(tokenize(f"{chunk.heading} {chunk.text}")) for chunk in chunks]
    lengths = [max(sum(counts.values()), 1) for counts in counted]
    average_length = sum(lengths) / len(lengths)
    weights = {
        term: _idf(len(chunks), sum(1 for counts in counted if term in counts)) for term in terms
    }
    scored = [
        (_score(chunk, counts, length, average_length, query, weights), chunk)
        for chunk, counts, length in zip(chunks, counted, lengths)
    ]
    ranked = sorted((pair for pair in scored if pair[0] > 0), key=lambda pair: -pair[0])
    return ranked[:limit]
