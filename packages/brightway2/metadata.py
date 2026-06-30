"""
Tiny manifest for the `brightway2` package.

This file intentionally stays small: just enough metadata to locate the GitHub
repo, docs root, and section URLs. Documentation itself is fetched on demand
and cached outside the package tree.
"""

METADATA: dict = {
    "name": "brightway2",
    "display_name": "Brightway 2",
    "description": (
        "Metapackage for Brightway 2, the stable legacy version of the Brightway "
        "life cycle assessment framework. Installs bw2analyzer, bw2calc 1.x, "
        "bw2data 3.x, bw2io, bw2parameters, and other core components for LCA "
        "in Python."
    ),
    "github_url": "https://github.com/brightway-lca/brightway2",
    "github_repo": "brightway-lca/brightway2",
    "readthedocs_slug": None,
    "docs_url": "https://docs.brightway.dev/en/latest/",
    "pypi_url": "https://pypi.org/project/brightway2/",
    "install": {
        "pip": "pip install brightway2",
        "conda": "conda install -c conda-forge brightway2",
    },
    "python_requires": ">=3.7",
    "license": "BSD-3-Clause",
    "key_dependencies": [
        "bw2analyzer",
        "bw2calc",
        "bw2data",
        "bw2io",
        "bw2parameters",
        "stats_arrays",
    ],
    "sections": [
        {
            "id": "overview",
            "title": "Overview",
            "url": "https://docs.brightway.dev/en/latest/",
            "description": (
                "Introduction to the Brightway LCA framework and brightway2 packages."
            ),
        },
    ],
}
