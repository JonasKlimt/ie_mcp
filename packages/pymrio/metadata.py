"""
Tiny manifest for the `pymrio` package.

This file intentionally stays small: just enough metadata to locate the GitHub
repo, docs root, and section URLs. Documentation itself is fetched on demand
and cached outside the package tree.
"""

METADATA: dict = {
    "name": "pymrio",
    "display_name": "pymrio",
    "description": (
        "pymrio is an open-source Python tool for analysing global environmentally "
        "extended multi-regional input-output (EE MRIO) tables. It provides a "
        "high-level abstraction layer for MRIO databases, with automatic download "
        "and parsers for EXIOBASE, WIOD, EORA26, OECD, and GLORIA. Automatically "
        "calculates missing tables (footprint, territorial, trade-embodied impacts), "
        "supports region/sector reclassification, extension restructuring, "
        "visualization, and automated report generation."
    ),
    "github_url": "https://github.com/IndEcol/pymrio",
    "github_repo": "IndEcol/pymrio",
    "readthedocs_slug": "pymrio",
    "docs_url": "https://pymrio.readthedocs.io/en/latest/",
    "pypi_url": "https://pypi.org/project/pymrio/",
    "install": {
        "pip": "pip install pymrio",
        "conda": "conda install -c conda-forge pymrio",
    },
    "python_requires": ">=3.9",
    "license": "GPL-3.0",
    "key_dependencies": ["numpy", "pandas", "scipy", "matplotlib"],
    "sections": [
        {
            "id": "intro",
            "title": "Introduction",
            "url": "https://pymrio.readthedocs.io/en/latest/intro.html",
            "description": (
                "What pymrio is, installation, quickstart, tutorials, and citation."
            ),
        },
        {
            "id": "installation",
            "title": "Installation",
            "url": "https://pymrio.readthedocs.io/en/latest/installation.html",
            "description": (
                "Detailed installation instructions for pip and conda."
            ),
        },
        {
            "id": "tutorial",
            "title": "Basic Tutorial",
            "url": "https://pymrio.readthedocs.io/en/latest/notebooks/full_tutorial.html",
            "description": (
                "Full tutorial: loading test MRIO data, core calculations (calc_all), "
                "Ghosh model, search/extract, IO math, gross trade, extension methods, "
                "and parsing/saving MRIOs."
            ),
        },
        {
            "id": "autodownload",
            "title": "Automatic MRIO Download",
            "url": "https://pymrio.readthedocs.io/en/latest/notebooks/autodownload.html",
            "description": (
                "How to automatically download EXIOBASE 3, WIOD, OECD, Eora26, "
                "and GLORIA databases."
            ),
        },
        {
            "id": "math",
            "title": "Mathematical Background",
            "url": "https://pymrio.readthedocs.io/en/latest/math.html",
            "description": (
                "MRIO mathematics: basic MRIO calculations, upstream/downstream "
                "scope 3, and aggregation."
            ),
        },
    ],
}
