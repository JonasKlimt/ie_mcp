"""
Tiny manifest for the `brightway2-speedups` package.
"""

METADATA: dict = {
    "name": "brightway2-speedups",
    "display_name": "Brightway2 Speedups",
    "description": "Performance speedups for Brightway2 LCA calculations using compiled Cython extensions. Provides faster implementations of common operations in the Brightway LCA framework.",
    "github_url": "https://github.com/brightway-lca/brightway2-speedups",
    "github_repo": "brightway-lca/brightway2-speedups",
    "readthedocs_slug": None,
    "docs_url": "https://github.com/brightway-lca/brightway2-speedups",
    "pypi_url": None,
    "install": {
        "git": "pip install git+https://github.com/brightway-lca/brightway2-speedups.git",
    },
    "python_requires": ">=3.9",
    "license": "BSD-3-Clause",
    "key_dependencies": [],
    "sections": [
        {
            "id": "readme",
            "title": "README / Overview",
            "url": "https://github.com/brightway-lca/brightway2-speedups",
            "description": "Overview, installation, and usage.",
        },
    ],
}
