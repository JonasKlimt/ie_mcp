"""
Tiny manifest for the `bw_simple_graph` package.
"""

METADATA: dict = {
    "name": "bw_simple_graph",
    "display_name": "bw_simple_graph",
    "description": (
        "A simple graph database backend for Brightway without the full bw2data "
        "dependency. Provides a lightweight alternative backend for storing activities "
        "and exchanges, useful for small projects or educational purposes."
    ),
    "github_url": "https://github.com/brightway-lca/bw_simple_graph",
    "github_repo": "brightway-lca/bw_simple_graph",
    "readthedocs_slug": None,
    "docs_url": "https://github.com/brightway-lca/bw_simple_graph",
    "pypi_url": None,
    "install": {
        "git": "pip install git+https://github.com/brightway-lca/bw_simple_graph.git",
    },
    "python_requires": ">=3.9",
    "license": "BSD-3-Clause",
    "key_dependencies": ["brightway25"],
    "sections": [
        {
            "id": "readme",
            "title": "README / Overview",
            "url": "https://github.com/brightway-lca/bw_simple_graph",
            "description": "Overview, installation, and usage.",
        },
    ],
}
