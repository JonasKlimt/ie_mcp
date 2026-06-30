"""
Tiny manifest for the `bw_graph_tools` package.
"""

METADATA: dict = {
    "name": "bw_graph_tools",
    "display_name": "bw_graph_tools",
    "description": (
        "Graph traversal classes and utilities for Brightway LCA supply chains. "
        "Provides tools to traverse the technosphere graph, identify dominant supply "
        "chains, and support contribution analysis, including cutoff-based traversal "
        "and node/edge data structures."
    ),
    "github_url": "https://github.com/brightway-lca/bw_graph_tools",
    "github_repo": "brightway-lca/bw_graph_tools",
    "readthedocs_slug": None,
    "docs_url": "https://docs.brightway.dev/projects/bw-graph-tools/",
    "pypi_url": "https://pypi.org/project/bw_graph_tools/",
    "install": {
        "pip": "pip install bw_graph_tools",
        "conda": "conda install -c conda-forge bw_graph_tools",
    },
    "python_requires": ">=3.9",
    "license": "BSD-3-Clause",
    "key_dependencies": ["brightway25"],
    "sections": [
        {
            "id": "readme",
            "title": "README / Overview",
            "url": "https://github.com/brightway-lca/bw_graph_tools",
            "description": "Overview, installation, and usage.",
        },
    ],
}
