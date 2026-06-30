"""
Tiny manifest for the `bw2parameters` package.

This file intentionally stays small: just enough metadata to locate the GitHub
repo, docs root, and section URLs. Documentation itself is fetched on demand
and cached outside the package tree.
"""

METADATA: dict = {
    "name": "bw2parameters",
    "display_name": "bw2parameters",
    "description": (
        "Library for storing, validating, and calculating with parameters in the "
        "Brightway LCA framework. Supports project-level, database-level, and "
        "activity-level parameters, formula evaluation, group management, and "
        "recalculation of dependent parameters."
    ),
    "github_url": "https://github.com/brightway-lca/brightway2-parameters",
    "github_repo": "brightway-lca/brightway2-parameters",
    "readthedocs_slug": None,
    "docs_url": "https://github.com/brightway-lca/brightway2-parameters",
    "pypi_url": "https://pypi.org/project/bw2parameters/",
    "install": {
        "pip": "pip install bw2parameters",
        "conda": "conda install -c conda-forge bw2parameters",
    },
    "python_requires": ">=3.9",
    "license": "BSD-3-Clause",
    "key_dependencies": [
        "bw2data",
        "asteval",
        "numpy",
        "peewee",
    ],
    "sections": [
        {
            "id": "readme",
            "title": "README / Overview",
            "url": "https://github.com/brightway-lca/brightway2-parameters",
            "description": (
                "Overview of bw2parameters: parameter types, formula syntax, "
                "and usage examples."
            ),
        },
    ],
}
