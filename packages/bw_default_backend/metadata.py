"""
Tiny manifest for the `bw_default_backend` package.
"""

METADATA: dict = {
    "name": "bw_default_backend",
    "display_name": "bw_default_backend",
    "description": (
        "Default SQLite3-based backend for the Brightway LCA framework using peewee ORM. "
        "Provides the persistent storage layer for activities, exchanges, and LCIA methods. "
        "This was an early Brightway 3 design experiment; functionality is now integrated "
        "into bw2data."
    ),
    "note": (
        "Early design prototype; functionality is integrated into bw2data for current "
        "Brightway 2.5."
    ),
    "github_url": "https://github.com/brightway-lca/bw_default_backend",
    "github_repo": "brightway-lca/bw_default_backend",
    "readthedocs_slug": None,
    "docs_url": "https://github.com/brightway-lca/bw_default_backend",
    "pypi_url": None,
    "install": {
        "git": "pip install git+https://github.com/brightway-lca/bw_default_backend.git",
    },
    "python_requires": ">=3.9",
    "license": "BSD-3-Clause",
    "key_dependencies": ["brightway25"],
    "sections": [
        {
            "id": "readme",
            "title": "README / Overview",
            "url": "https://github.com/brightway-lca/bw_default_backend",
            "description": "Overview, installation, and usage.",
        },
    ],
}
