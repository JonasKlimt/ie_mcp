"""
Tiny manifest for the `brightway2-ui` package.
"""

METADATA: dict = {
    "name": "brightway2-ui",
    "display_name": "Brightway2 UI",
    "description": "Command-line user interface (CLI) tool for the Brightway2 LCA framework. Provides interactive shell commands for managing Brightway projects, databases, and performing common LCA tasks from the terminal.",
    "github_url": "https://github.com/brightway-lca/brightway2-ui",
    "github_repo": "brightway-lca/brightway2-ui",
    "readthedocs_slug": None,
    "docs_url": "https://github.com/brightway-lca/brightway2-ui",
    "pypi_url": None,
    "install": {
        "git": "pip install git+https://github.com/brightway-lca/brightway2-ui.git",
    },
    "python_requires": ">=3.9",
    "license": "BSD-3-Clause",
    "key_dependencies": [],
    "sections": [
        {
            "id": "readme",
            "title": "README / Overview",
            "url": "https://github.com/brightway-lca/brightway2-ui",
            "description": "Overview, installation, and usage.",
        },
    ],
}
