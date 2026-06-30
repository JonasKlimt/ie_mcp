"""
Tiny manifest for the `bw_migrations` package.

This file intentionally stays small: just enough metadata to locate the GitHub
repo, docs root, and section URLs. Documentation itself is fetched on demand
and cached outside the package tree.
"""

METADATA: dict = {
    "name": "bw_migrations",
    "display_name": "bw_migrations",
    "description": (
        "Migration data and utilities for the Brightway IO and LCA ecosystem. "
        "Provides tools and datasets for migrating between different versions of "
        "ecoinvent and other LCA databases, mapping old flow identifiers to new "
        "ones, and applying transformations to existing datasets."
    ),
    "github_url": "https://github.com/brightway-lca/bw_migrations",
    "github_repo": "brightway-lca/bw_migrations",
    "readthedocs_slug": None,
    "docs_url": "https://github.com/brightway-lca/bw_migrations",
    "pypi_url": "https://pypi.org/project/bw_migrations/",
    "install": {
        "pip": "pip install bw_migrations",
        "conda": "conda install -c conda-forge bw_migrations",
    },
    "python_requires": ">=3.9",
    "license": "BSD-3-Clause",
    "key_dependencies": [
        "randonneur",
    ],
    "sections": [
        {
            "id": "readme",
            "title": "README / Overview",
            "url": "https://github.com/brightway-lca/bw_migrations",
            "description": (
                "Overview of bw_migrations: migration files, transformation "
                "utilities, and how to apply migrations."
            ),
        },
    ],
}
