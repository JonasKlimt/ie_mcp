"""
Tiny manifest for the `multifunctional` package.

This file intentionally stays small: just enough metadata to locate the GitHub
repo, docs root, and section URLs. Documentation itself is fetched on demand
and cached outside the package tree.
"""

METADATA: dict = {
    "name": "multifunctional",
    "display_name": "multifunctional",
    "description": (
        "Code for handling multifunctional activities in Brightway LCA. Provides "
        "strategies and tools for allocation, substitution, and partitioning of "
        "processes that produce multiple products, extending bw2data to support "
        "multifunctional processes."
    ),
    "github_url": "https://github.com/brightway-lca/multifunctional",
    "github_repo": "brightway-lca/multifunctional",
    "readthedocs_slug": None,
    "docs_url": "https://github.com/brightway-lca/multifunctional",
    "pypi_url": "https://pypi.org/project/multifunctional/",
    "install": {
        "pip": "pip install multifunctional",
        "conda": "conda install -c conda-forge multifunctional",
    },
    "python_requires": ">=3.9",
    "license": "BSD-3-Clause",
    "key_dependencies": [
        "bw2data",
        "bw_processing",
        "numpy",
    ],
    "sections": [
        {
            "id": "readme",
            "title": "README / Overview",
            "url": "https://github.com/brightway-lca/multifunctional",
            "description": (
                "Overview of multifunctional: allocation strategies, substitution, "
                "and handling co-products in LCA."
            ),
        },
    ],
}
