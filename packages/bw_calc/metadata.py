"""
Tiny manifest for the `bw_calc` package.
"""

METADATA: dict = {
    "name": "bw_calc",
    "display_name": "bw_calc",
    "description": (
        "Early prototype of matrix calculations for the Brightway 3 framework "
        "(distinct from bw2calc for Brightway 2/2.5). This was an early pre-release "
        "experiment and is superseded by bw2calc >=2.x for Brightway 2.5."
    ),
    "note": (
        "This is an early prototype repository; for Brightway 2.5, use bw2calc "
        "(>=2.x) instead."
    ),
    "github_url": "https://github.com/brightway-lca/bw_calc",
    "github_repo": "brightway-lca/bw_calc",
    "readthedocs_slug": None,
    "docs_url": "https://github.com/brightway-lca/bw_calc",
    "pypi_url": "https://pypi.org/project/bw_calc/",
    "install": {
        "pip": "pip install bw_calc",
        "conda": "conda install -c conda-forge bw_calc",
    },
    "python_requires": ">=3.9",
    "license": "BSD-3-Clause",
    "key_dependencies": ["brightway25"],
    "sections": [
        {
            "id": "readme",
            "title": "README / Overview",
            "url": "https://github.com/brightway-lca/bw_calc",
            "description": "Overview, installation, and usage.",
        },
    ],
}
