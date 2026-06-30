"""
Tiny manifest for the `bw2data` package.

This file intentionally stays small: just enough metadata to locate the GitHub
repo, docs root, and section URLs. Documentation itself is fetched on demand
and cached outside the package tree.
"""

METADATA: dict = {
    "name": "bw2data",
    "display_name": "bw2data",
    "description": (
        "Tools for the management of inventory databases and impact assessment "
        "methods in the Brightway LCA framework. Provides the core data management "
        "layer: project management, database storage using SQLite, activity and "
        "exchange manipulation, LCIA method storage, and searching."
    ),
    "github_url": "https://github.com/brightway-lca/brightway2-data",
    "github_repo": "brightway-lca/brightway2-data",
    "readthedocs_slug": "bw2data",
    "docs_url": "https://docs.brightway.dev/en/latest/content/api/bw2data/index.html",
    "pypi_url": "https://pypi.org/project/bw2data/",
    "install": {
        "pip": "pip install bw2data",
        "conda": "conda install -c conda-forge bw2data",
    },
    "python_requires": ">=3.9",
    "license": "BSD-3-Clause",
    "key_dependencies": [
        "bw_processing",
        "numpy",
        "peewee",
        "scipy",
        "stats_arrays",
    ],
    "sections": [
        {
            "id": "overview",
            "title": "Overview",
            "url": "https://docs.brightway.dev/en/latest/content/api/bw2data/index.html",
            "description": (
                "Introduction to bw2data: project management, databases, "
                "activities, exchanges, and LCIA methods."
            ),
        },
        {
            "id": "api",
            "title": "API Reference",
            "url": "https://docs.brightway.dev/en/latest/content/api/bw2data/index.html",
            "description": (
                "Full API reference for bw2data classes and functions."
            ),
        },
    ],
}
