"""
Tiny manifest for the `bw2analyzer` package.

This file intentionally stays small: just enough metadata to locate the GitHub
repo, docs root, and section URLs. Documentation itself is fetched on demand
and cached outside the package tree.
"""

METADATA: dict = {
    "name": "bw2analyzer",
    "display_name": "bw2analyzer",
    "description": (
        "Tools to analyze results of life cycle assessment (LCA) calculations "
        "in the Brightway LCA framework. Provides utilities to explore and traverse "
        "the supply chains that contribute to an LCA score, including contribution "
        "analysis, supply chain traversal, and utilities for working with "
        "characterization factors."
    ),
    "github_url": "https://github.com/brightway-lca/brightway2-analyzer",
    "github_repo": "brightway-lca/brightway2-analyzer",
    "readthedocs_slug": None,
    "docs_url": "https://docs.brightway.dev/en/latest/content/api/bw2analyzer/index.html",
    "pypi_url": "https://pypi.org/project/bw2analyzer/",
    "install": {
        "pip": "pip install bw2analyzer",
        "conda": "conda install -c conda-forge bw2analyzer",
    },
    "python_requires": ">=3.9",
    "license": "BSD-3-Clause",
    "key_dependencies": [
        "bw2calc",
        "bw2data",
        "matrix_utils",
        "numpy",
        "scipy",
    ],
    "sections": [
        {
            "id": "readme",
            "title": "README / Overview",
            "url": "https://docs.brightway.dev/en/latest/content/api/bw2analyzer/index.html",
            "description": (
                "Overview of bw2analyzer features, installation, and "
                "basic usage examples."
            ),
        },
    ],
}
