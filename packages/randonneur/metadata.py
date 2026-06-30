"""
Tiny manifest for the `randonneur` package.

This file intentionally stays small: just enough metadata to locate the GitHub
repo, docs root, and section URLs. Documentation itself is fetched on demand
and cached outside the package tree.
"""

METADATA: dict = {
    "name": "randonneur",
    "display_name": "randonneur",
    "description": (
        "Library to apply flexible, reproducible changes (transformations) to LCA "
        "datasets. Supports renaming, updating, deleting, and relinking flows and "
        "activities via JSON transformation files. Designed for migrating ecoinvent "
        "databases between versions and adapting datasets for different use cases."
    ),
    "github_url": "https://github.com/brightway-lca/randonneur",
    "github_repo": "brightway-lca/randonneur",
    "readthedocs_slug": None,
    "docs_url": "https://github.com/brightway-lca/randonneur",
    "pypi_url": "https://pypi.org/project/randonneur/",
    "install": {
        "pip": "pip install randonneur",
        "conda": "conda install -c conda-forge randonneur",
    },
    "python_requires": ">=3.9",
    "license": "BSD-3-Clause",
    "key_dependencies": [
        "randonneur_data",
        "pydantic",
        "numpy",
    ],
    "sections": [
        {
            "id": "readme",
            "title": "README / Overview",
            "url": "https://github.com/brightway-lca/randonneur",
            "description": (
                "Overview of randonneur: transformation files, operations "
                "(rename, update, delete, relink), and usage."
            ),
        },
    ],
}
