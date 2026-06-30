"""
Tiny manifest for the `brightway-olca` package.
"""

METADATA: dict = {
    "name": "brightway-olca",
    "display_name": "Brightway openLCA",
    "description": "Library for interacting with openLCA via the openLCA IPC Server from within Brightway. Allows importing and exporting LCA data between Brightway and openLCA, and calling openLCA calculation methods from Python.",
    "github_url": "https://github.com/brightway-lca/brightway-olca",
    "github_repo": "brightway-lca/brightway-olca",
    "readthedocs_slug": None,
    "docs_url": "https://github.com/brightway-lca/brightway-olca",
    "pypi_url": None,
    "install": {
        "git": "pip install git+https://github.com/brightway-lca/brightway-olca.git",
    },
    "python_requires": ">=3.9",
    "license": "BSD-3-Clause",
    "key_dependencies": [],
    "sections": [
        {
            "id": "readme",
            "title": "README / Overview",
            "url": "https://github.com/brightway-lca/brightway-olca",
            "description": "Overview, installation, and usage.",
        },
    ],
}
