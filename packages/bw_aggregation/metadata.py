"""
Tiny manifest for the `bw_aggregation` package.
"""

METADATA: dict = {
    "name": "bw_aggregation",
    "display_name": "bw_aggregation",
    "description": (
        "Use aggregated (unit) processes for quicker LCA calculations in Brightway. "
        "Allows pre-aggregated processes to be inserted into the supply chain, reducing "
        "matrix size and speeding up calculations, while maintaining compatibility with "
        "the Brightway LCA framework."
    ),
    "github_url": "https://github.com/brightway-lca/bw_aggregation",
    "github_repo": "brightway-lca/bw_aggregation",
    "readthedocs_slug": None,
    "docs_url": "https://github.com/brightway-lca/bw_aggregation",
    "pypi_url": "https://pypi.org/project/bw_aggregation/",
    "install": {
        "pip": "pip install bw_aggregation",
        "conda": "conda install -c conda-forge bw_aggregation",
    },
    "python_requires": ">=3.9",
    "license": "BSD-3-Clause",
    "key_dependencies": ["brightway25"],
    "sections": [
        {
            "id": "readme",
            "title": "README / Overview",
            "url": "https://github.com/brightway-lca/bw_aggregation",
            "description": "Overview, installation, and usage.",
        },
    ],
}
