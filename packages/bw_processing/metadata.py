"""
Tiny manifest for the `bw_processing` package.

This file intentionally stays small: just enough metadata to locate the GitHub
repo, docs root, and section URLs. Documentation itself is fetched on demand
and cached outside the package tree.
"""

METADATA: dict = {
    "name": "bw_processing",
    "display_name": "bw_processing",
    "description": (
        "Tools to create and work with structured NumPy arrays (datapackages) in "
        "a common format for the Brightway LCA framework. Provides the core data "
        "packaging layer used to pass matrix data between components, including "
        "creating, reading, and iterating over datapackages stored as zip archives."
    ),
    "github_url": "https://github.com/brightway-lca/bw_processing",
    "github_repo": "brightway-lca/bw_processing",
    "readthedocs_slug": None,
    "docs_url": "https://docs.brightway.dev/projects/bw-processing/",
    "pypi_url": "https://pypi.org/project/bw_processing/",
    "install": {
        "pip": "pip install bw_processing",
        "conda": "conda install -c conda-forge bw_processing",
    },
    "python_requires": ">=3.9",
    "license": "BSD-3-Clause",
    "key_dependencies": [
        "numpy",
        "pandas",
        "fsspec",
    ],
    "sections": [
        {
            "id": "overview",
            "title": "Overview",
            "url": "https://docs.brightway.dev/projects/bw-processing/",
            "description": (
                "Introduction to bw_processing datapackages, structured arrays, "
                "and the datapackage format."
            ),
        },
    ],
}
