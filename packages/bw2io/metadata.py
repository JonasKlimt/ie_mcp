"""
Tiny manifest for the `bw2io` package.

This file intentionally stays small: just enough metadata to locate the GitHub
repo, docs root, and section URLs. Documentation itself is fetched on demand
and cached outside the package tree.
"""

METADATA: dict = {
    "name": "bw2io",
    "display_name": "bw2io",
    "description": (
        "Importing and exporting functionality for the Brightway LCA framework. "
        "Supports importing ecoinvent (ecospold1, ecospold2), SimaPro CSV, "
        "ExioBase, and other LCA data formats. Also handles exporting and provides "
        "migration utilities for converting between data formats."
    ),
    "github_url": "https://github.com/brightway-lca/brightway2-io",
    "github_repo": "brightway-lca/brightway2-io",
    "readthedocs_slug": "bw2io",
    "docs_url": "https://docs.brightway.dev/en/latest/content/api/bw2io/index.html",
    "pypi_url": "https://pypi.org/project/bw2io/",
    "install": {
        "pip": "pip install bw2io",
        "conda": "conda install -c conda-forge bw2io",
    },
    "python_requires": ">=3.9",
    "license": "BSD-3-Clause",
    "key_dependencies": [
        "bw2data",
        "bw_migrations",
        "bw_processing",
        "randonneur",
        "randonneur_data",
        "lxml",
        "numpy",
    ],
    "sections": [
        {
            "id": "overview",
            "title": "Overview",
            "url": "https://docs.brightway.dev/en/latest/content/api/bw2io/index.html",
            "description": (
                "Introduction to bw2io: supported import/export formats, "
                "importers, and strategies."
            ),
        },
    ],
}
