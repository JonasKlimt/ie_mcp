"""
Tiny manifest for the `brightway_hybrid` package.
"""

METADATA: dict = {
    "name": "brightway_hybrid",
    "display_name": "Brightway Hybrid",
    "description": "Hybrid (Input-Output/Process-based) Life Cycle Assessment in Brightway. Combines process-based LCA data (e.g., ecoinvent) with multi-regional input-output (MRIO) tables to perform hybrid LCA calculations, bridging the gap between process LCA and MRIO analysis.",
    "github_url": "https://github.com/brightway-lca/BrightwayHybrid",
    "github_repo": "brightway-lca/BrightwayHybrid",
    "readthedocs_slug": None,
    "docs_url": "https://github.com/brightway-lca/BrightwayHybrid",
    "pypi_url": None,
    "install": {
        "pip": "pip install brightwayHybrid",  # check GitHub for install instructions
    },
    "python_requires": ">=3.9",
    "license": "BSD-3-Clause",
    "key_dependencies": ["brightway2 or brightway25", "bw_exiobase"],
    "sections": [
        {
            "id": "readme",
            "title": "README / Overview",
            "url": "https://github.com/brightway-lca/BrightwayHybrid",
            "description": "Overview, installation, and usage.",
        },
    ],
}
