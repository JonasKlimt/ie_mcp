"""
Tiny manifest for the `bw_campaigns` package.
"""

METADATA: dict = {
    "name": "bw_campaigns",
    "display_name": "bw_campaigns",
    "description": (
        "Easily store and manage Brightway datapackages as named campaigns. "
        "Provides a lightweight way to organize and reuse sets of datapackages "
        "(scenarios) for batch LCA calculations."
    ),
    "github_url": "https://github.com/brightway-lca/bw_campaigns",
    "github_repo": "brightway-lca/bw_campaigns",
    "readthedocs_slug": None,
    "docs_url": "https://github.com/brightway-lca/bw_campaigns",
    "pypi_url": None,
    "install": {
        "git": "pip install git+https://github.com/brightway-lca/bw_campaigns.git",
    },
    "python_requires": ">=3.9",
    "license": "BSD-3-Clause",
    "key_dependencies": ["brightway25"],
    "sections": [
        {
            "id": "readme",
            "title": "README / Overview",
            "url": "https://github.com/brightway-lca/bw_campaigns",
            "description": "Overview, installation, and usage.",
        },
    ],
}
