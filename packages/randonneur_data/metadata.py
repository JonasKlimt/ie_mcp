"""
Tiny manifest for the `randonneur_data` package.

This file intentionally stays small: just enough metadata to locate the GitHub
repo, docs root, and section URLs. Documentation itself is fetched on demand
and cached outside the package tree.
"""

METADATA: dict = {
    "name": "randonneur_data",
    "display_name": "randonneur_data",
    "description": (
        "Data files (migration/transformation datasets) for the randonneur ETL "
        "library. Contains JSON transformation files for migrating between ecoinvent "
        "versions, mapping flows between different nomenclature systems, and other "
        "LCA dataset transformations."
    ),
    "github_url": "https://github.com/brightway-lca/randonneur_data",
    "github_repo": "brightway-lca/randonneur_data",
    "readthedocs_slug": None,
    "docs_url": "https://github.com/brightway-lca/randonneur_data",
    "pypi_url": "https://pypi.org/project/randonneur_data/",
    "install": {
        "pip": "pip install randonneur_data",
        "conda": "conda install -c conda-forge randonneur_data",
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
            "url": "https://github.com/brightway-lca/randonneur_data",
            "description": (
                "Overview of available transformation datasets and how to use "
                "them with randonneur."
            ),
        },
    ],
}
