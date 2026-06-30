"""
Tiny manifest for the `brightway2-regional` package.
"""

METADATA: dict = {
    "name": "brightway2-regional",
    "display_name": "Brightway2 Regional",
    "description": "Regionalized LCA calculations for the Brightway LCA framework. Extends Brightway2 to support spatially differentiated life cycle assessment, allowing impact assessment methods to be applied with geographical specificity using spatial units and regionalized characterization factors.",
    "github_url": "https://github.com/brightway-lca/brightway2-regional",
    "github_repo": "brightway-lca/brightway2-regional",
    "readthedocs_slug": None,
    "docs_url": "https://github.com/brightway-lca/brightway2-regional",
    "pypi_url": None,
    "install": {
        "git": "pip install git+https://github.com/brightway-lca/brightway2-regional.git",
    },
    "python_requires": ">=3.9",
    "license": "BSD-3-Clause",
    "key_dependencies": ["brightway2", "pandarus"],
    "sections": [
        {
            "id": "readme",
            "title": "README / Overview",
            "url": "https://github.com/brightway-lca/brightway2-regional",
            "description": "Overview, installation, and usage.",
        },
    ],
}
