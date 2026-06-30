"""
Tiny manifest for the `edge-of-the-world` package.
"""

METADATA: dict = {
    "name": "edge-of-the-world",
    "display_name": "Edge of the World",
    "description": "An alternate Brightway backend that allows richer edge (exchange) descriptions that don't map 1-to-1 to matrix values. Experimental backend for Brightway that supports more complex exchange representations beyond the standard technosphere/biosphere/characterization structure.",
    "github_url": "https://github.com/brightway-lca/edge-of-the-world",
    "github_repo": "brightway-lca/edge-of-the-world",
    "readthedocs_slug": None,
    "docs_url": "https://github.com/brightway-lca/edge-of-the-world",
    "pypi_url": None,
    "install": {
        "git": "pip install git+https://github.com/brightway-lca/edge-of-the-world.git",
    },
    "python_requires": ">=3.9",
    "license": "BSD-3-Clause",
    "key_dependencies": [],
    "sections": [
        {
            "id": "readme",
            "title": "README / Overview",
            "url": "https://github.com/brightway-lca/edge-of-the-world",
            "description": "Overview, installation, and usage.",
        },
    ],
}
