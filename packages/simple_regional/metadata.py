"""
Tiny manifest for the `simple_regional` package.
"""

METADATA: dict = {
    "name": "simple_regional",
    "display_name": "Simple Regional",
    "description": "Simple regional LCA calculations for a shared spatial scale. Provides lightweight regionalized LCA functionality for cases where all inventories and characterization factors share the same spatial resolution, without the full complexity of brightway2-regional.",
    "github_url": "https://github.com/brightway-lca/simple_regional",
    "github_repo": "brightway-lca/simple_regional",
    "readthedocs_slug": None,
    "docs_url": "https://github.com/brightway-lca/simple_regional",
    "pypi_url": "https://pypi.org/project/simple_regional/",
    "install": {
        "pip": "pip install simple_regional",
    },
    "python_requires": ">=3.9",
    "license": "BSD-3-Clause",
    "key_dependencies": ["brightway25"],
    "sections": [
        {
            "id": "readme",
            "title": "README / Overview",
            "url": "https://github.com/brightway-lca/simple_regional",
            "description": "Overview, installation, and usage.",
        },
    ],
}
