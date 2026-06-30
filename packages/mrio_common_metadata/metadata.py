"""
Tiny manifest for the `mrio_common_metadata` package.

This file intentionally stays small: just enough metadata to locate the GitHub
repo, docs root, and section URLs. Documentation itself is fetched on demand
and cached outside the package tree.
"""

METADATA: dict = {
    "name": "mrio_common_metadata",
    "display_name": "mrio_common_metadata",
    "description": (
        "Common datapackage schema and utilities for multi-regional input-output "
        "(MRIO) tables in the Brightway LCA ecosystem. Provides metadata standards "
        "and helper functions for working with MRIO data as Brightway datapackages."
    ),
    "github_url": "https://github.com/brightway-lca/mrio_common_metadata",
    "github_repo": "brightway-lca/mrio_common_metadata",
    "readthedocs_slug": None,
    "docs_url": "https://github.com/brightway-lca/mrio_common_metadata",
    "pypi_url": "https://pypi.org/project/mrio_common_metadata/",
    "install": {
        "pip": "pip install mrio_common_metadata",
        "conda": "conda install -c conda-forge mrio_common_metadata",
    },
    "python_requires": ">=3.9",
    "license": "BSD-3-Clause",
    "key_dependencies": [
        "bw_processing",
        "numpy",
    ],
    "sections": [
        {
            "id": "readme",
            "title": "README / Overview",
            "url": "https://github.com/brightway-lca/mrio_common_metadata",
            "description": (
                "Overview of mrio_common_metadata: schema, utilities, and "
                "MRIO datapackage format."
            ),
        },
    ],
}
