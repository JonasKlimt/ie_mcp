"""
ReadTheDocs API helpers for version discovery.

Uses the public ReadTheDocs API v3 to list available versions for a project.
No authentication required for public projects.
"""

from __future__ import annotations

import httpx

_READTHEDOCS_API = "https://readthedocs.org/api/v3"


def list_versions(readthedocs_slug: str, timeout: float = 15.0) -> list[str]:
    """
    Return the active version slugs for a ReadTheDocs project.

    Args:
        readthedocs_slug: The ReadTheDocs project slug (e.g. 'premise').

    Returns:
        List of version slug strings, e.g. ['latest', 'stable', 'v2.3.0', ...].
        'latest' is always first if present.
    """
    url = f"{_READTHEDOCS_API}/projects/{readthedocs_slug}/versions/"
    params = {"active": "true", "limit": 50}

    response = httpx.get(url, params=params, timeout=timeout)
    response.raise_for_status()

    data = response.json()
    slugs = [item["slug"] for item in data.get("results", [])]

    # Sort so 'latest' and 'stable' appear first
    priority = {"latest": 0, "stable": 1}
    slugs.sort(key=lambda s: (priority.get(s, 2), s))
    return slugs
