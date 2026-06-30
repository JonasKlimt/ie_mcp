"""
Tiny manifest for the `matrix_utils` package.

This file intentionally stays small: just enough metadata to locate the GitHub
repo, docs root, and section URLs. Documentation itself is fetched on demand
and cached outside the package tree.
"""

METADATA: dict = {
    "name": "matrix_utils",
    "display_name": "matrix_utils",
    "description": (
        "Utilities to build and iterate over matrices using Brightway datapackages. "
        "Provides MappedMatrix and related classes for constructing sparse scipy "
        "matrices from structured array datapackages, supporting Monte Carlo "
        "sampling, scenario iteration, and matrix building from multiple datapackages."
    ),
    "github_url": "https://github.com/brightway-lca/matrix_utils",
    "github_repo": "brightway-lca/matrix_utils",
    "readthedocs_slug": None,
    "docs_url": "https://github.com/brightway-lca/matrix_utils",
    "pypi_url": "https://pypi.org/project/matrix_utils/",
    "install": {
        "pip": "pip install matrix_utils",
        "conda": "conda install -c conda-forge matrix_utils",
    },
    "python_requires": ">=3.9",
    "license": "BSD-3-Clause",
    "key_dependencies": [
        "bw_processing",
        "numpy",
        "scipy",
        "stats_arrays",
    ],
    "sections": [
        {
            "id": "readme",
            "title": "README / Overview",
            "url": "https://github.com/brightway-lca/matrix_utils",
            "description": (
                "Overview of matrix_utils: MappedMatrix, datapackage iteration, "
                "and matrix construction."
            ),
        },
    ],
}
