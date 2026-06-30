"""
Tiny manifest for the `bw_io` package.
"""

METADATA: dict = {
    "name": "bw_io",
    "display_name": "bw_io",
    "description": (
        "Early prototype IO tools for the Brightway LCA framework (distinct from bw2io). "
        "This was an early Brightway 3 design experiment for import/export functionality "
        "and is superseded by bw2io for current Brightway 2.5."
    ),
    "note": "Early design prototype; use bw2io for current Brightway 2.5.",
    "github_url": "https://github.com/brightway-lca/bw_io",
    "github_repo": "brightway-lca/bw_io",
    "readthedocs_slug": None,
    "docs_url": "https://github.com/brightway-lca/bw_io",
    "pypi_url": None,
    "install": {
        "git": "pip install git+https://github.com/brightway-lca/bw_io.git",
    },
    "python_requires": ">=3.9",
    "license": "BSD-3-Clause",
    "key_dependencies": ["brightway25"],
    "sections": [
        {
            "id": "readme",
            "title": "README / Overview",
            "url": "https://github.com/brightway-lca/bw_io",
            "description": "Overview, installation, and usage.",
        },
    ],
}
