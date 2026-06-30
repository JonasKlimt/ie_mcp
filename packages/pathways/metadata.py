"""
Tiny manifest for the `pathways` package.

This file intentionally stays small: just enough metadata to locate the GitHub
repo, docs root, and section URLs. Documentation itself is fetched on demand
and cached outside the package tree.
"""

METADATA: dict = {
    "name": "pathways",
    "display_name": "pathways",
    "description": (
        "pathways is a Python package from the polca project for scenario-driven "
        "transformations of life cycle inventories and datasets. It provides "
        "configurable pathways logic that can be integrated into prospective LCA "
        "workflows and related data-processing pipelines."
    ),
    "github_url": "https://github.com/polca/pathways",
    "github_repo": "polca/pathways",
    "readthedocs_slug": "pathways",
    "docs_url": "https://pathways.readthedocs.io/en/latest/index.html",
    "pypi_url": "https://pypi.org/project/pathways/",
    "install": {
        "pip": "pip install pathways",
    },
    "python_requires": ">=3.9",
    "license": "MIT",
    "key_dependencies": ["numpy", "pandas"],
    "sections": [
        {
            "id": "overview",
            "title": "Overview",
            "url": "https://pathways.readthedocs.io/en/latest/index.html",
            "description": (
                "Project overview, installation details, and entry point to the "
                "full Pathways documentation."
            ),
        },
    ],
}
