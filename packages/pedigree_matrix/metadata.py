"""
Tiny manifest for the `pedigree_matrix` package.
"""

METADATA: dict = {
    "name": "pedigree_matrix",
    "display_name": "Pedigree Matrix",
    "description": "Implementation of pedigree matrix approaches to adapting uncertainty probability distributions to new circumstances in LCA. Provides tools to calculate additional uncertainty based on data quality indicators (DQI) using the pedigree matrix approach as defined by Weidema et al.",
    "github_url": "https://github.com/brightway-lca/pedigree_matrix",
    "github_repo": "brightway-lca/pedigree_matrix",
    "readthedocs_slug": None,
    "docs_url": "https://github.com/brightway-lca/pedigree_matrix",
    "pypi_url": "https://pypi.org/project/pedigree_matrix/",
    "install": {
        "pip": "pip install pedigree_matrix",
        "conda": "conda install -c conda-forge pedigree_matrix",
    },
    "python_requires": ">=3.9",
    "license": "BSD-3-Clause",
    "key_dependencies": ["stats_arrays", "numpy"],
    "sections": [
        {
            "id": "readme",
            "title": "README / Overview",
            "url": "https://github.com/brightway-lca/pedigree_matrix",
            "description": "Overview, installation, and usage.",
        },
    ],
}
