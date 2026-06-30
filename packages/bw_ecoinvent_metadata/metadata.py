"""
Tiny manifest for the `bw_ecoinvent_metadata` package.
"""

METADATA: dict = {
    "name": "bw_ecoinvent_metadata",
    "display_name": "bw_ecoinvent_metadata",
    "description": (
        "Base ecoinvent elementary flows, LCIA methods, and characterization factors as "
        "data files for the Brightway LCA framework. Early design experiment providing "
        "ecoinvent metadata as structured data packages."
    ),
    "github_url": "https://github.com/brightway-lca/bw_ecoinvent_metadata",
    "github_repo": "brightway-lca/bw_ecoinvent_metadata",
    "readthedocs_slug": None,
    "docs_url": "https://github.com/brightway-lca/bw_ecoinvent_metadata",
    "pypi_url": None,
    "install": {
        "git": "pip install git+https://github.com/brightway-lca/bw_ecoinvent_metadata.git",
    },
    "python_requires": ">=3.9",
    "license": "BSD-3-Clause",
    "key_dependencies": ["brightway25"],
    "sections": [
        {
            "id": "readme",
            "title": "README / Overview",
            "url": "https://github.com/brightway-lca/bw_ecoinvent_metadata",
            "description": "Overview, installation, and usage.",
        },
    ],
}
