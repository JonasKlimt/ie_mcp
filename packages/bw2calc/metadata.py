"""
Tiny manifest for the `bw2calc` package.

This file intentionally stays small: just enough metadata to locate the GitHub
repo, docs root, and section URLs. Documentation itself is fetched on demand
and cached outside the package tree.
"""

METADATA: dict = {
    "name": "bw2calc",
    "display_name": "bw2calc",
    "description": (
        "The calculation engine for the Brightway LCA framework. Performs life "
        "cycle assessment (LCA) calculations including technosphere and biosphere "
        "matrix construction, inventory analysis, impact assessment, Monte Carlo "
        "simulations for uncertainty analysis, and graph traversal for contribution "
        "analysis."
    ),
    "github_url": "https://github.com/brightway-lca/brightway2-calc",
    "github_repo": "brightway-lca/brightway2-calc",
    "readthedocs_slug": "bw2calc",
    "docs_url": "https://docs.brightway.dev/en/latest/content/api/bw2calc/index.html",
    "pypi_url": "https://pypi.org/project/bw2calc/",
    "install": {
        "pip": "pip install bw2calc",
        "conda": "conda install -c conda-forge bw2calc",
    },
    "python_requires": ">=3.9",
    "license": "BSD-3-Clause",
    "key_dependencies": [
        "bw_processing",
        "matrix_utils",
        "numpy",
        "scipy",
        "stats_arrays",
    ],
    "sections": [
        {
            "id": "overview",
            "title": "Overview",
            "url": "https://docs.brightway.dev/en/latest/content/api/bw2calc/index.html",
            "description": (
                "Overview of the bw2calc calculation engine, LCA matrix setup, "
                "and basic usage."
            ),
        },
    ],
}
