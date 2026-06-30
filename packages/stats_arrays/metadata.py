"""
Tiny manifest for the `stats_arrays` package.

This file intentionally stays small: just enough metadata to locate the GitHub
repo, docs root, and section URLs. Documentation itself is fetched on demand
and cached outside the package tree.
"""

METADATA: dict = {
    "name": "stats_arrays",
    "display_name": "stats_arrays",
    "description": (
        "A standard NumPy structured array interface for defining uncertain "
        "parameters used in models, with classes for Monte Carlo sampling. Provides "
        "probability distribution definitions (lognormal, normal, triangular, "
        "uniform, etc.) stored in a compact NumPy array format, used throughout "
        "Brightway for uncertainty analysis."
    ),
    "github_url": "https://github.com/brightway-lca/stats_arrays",
    "github_repo": "brightway-lca/stats_arrays",
    "readthedocs_slug": "stats-arrays",
    "docs_url": "https://stats-arrays.readthedocs.io/en/latest/",
    "pypi_url": "https://pypi.org/project/stats_arrays/",
    "install": {
        "pip": "pip install stats_arrays",
        "conda": "conda install -c conda-forge stats_arrays",
    },
    "python_requires": ">=3.9",
    "license": "BSD-3-Clause",
    "key_dependencies": [
        "numpy",
        "scipy",
    ],
    "sections": [
        {
            "id": "overview",
            "title": "Overview",
            "url": "https://stats-arrays.readthedocs.io/en/latest/",
            "description": (
                "Introduction to stats_arrays, supported probability distributions, "
                "and Monte Carlo sampling."
            ),
        },
    ],
}
