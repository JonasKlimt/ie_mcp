"""
Tiny manifest for the `bw_hestia_bridge` package.
"""

METADATA: dict = {
    "name": "bw_hestia_bridge",
    "display_name": "bw_hestia_bridge",
    "description": (
        "Bridge library to consume the HESTIA API in Brightway. Allows importing "
        "agricultural LCA data from the HESTIA platform (hestia.earth) directly into "
        "Brightway projects for LCA calculations."
    ),
    "github_url": "https://github.com/brightway-lca/bw_hestia_bridge",
    "github_repo": "brightway-lca/bw_hestia_bridge",
    "readthedocs_slug": None,
    "docs_url": "https://github.com/brightway-lca/bw_hestia_bridge",
    "pypi_url": "https://pypi.org/project/bw_hestia_bridge/",
    "install": {
        "pip": "pip install bw_hestia_bridge",
        "conda": "conda install -c conda-forge bw_hestia_bridge",
    },
    "python_requires": ">=3.9",
    "license": "BSD-3-Clause",
    "key_dependencies": ["brightway25"],
    "sections": [
        {
            "id": "readme",
            "title": "README / Overview",
            "url": "https://github.com/brightway-lca/bw_hestia_bridge",
            "description": "Overview, installation, and usage.",
        },
    ],
}
