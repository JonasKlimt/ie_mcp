"""
Tiny manifest for the `bw_exiobase` package.
"""

METADATA: dict = {
    "name": "bw_exiobase",
    "display_name": "bw_exiobase",
    "description": (
        "Painlessly import EXIOBASE multi-regional input-output (MRIO) tables into "
        "Brightway for hybrid LCA and MRIO analysis. Supports multiple EXIOBASE versions "
        "and system types (pxp, ixi)."
    ),
    "github_url": "https://github.com/brightway-lca/bw_exiobase",
    "github_repo": "brightway-lca/bw_exiobase",
    "readthedocs_slug": None,
    "docs_url": "https://github.com/brightway-lca/bw_exiobase",
    "pypi_url": None,
    "install": {
        "git": "pip install git+https://github.com/brightway-lca/bw_exiobase.git",
    },
    "python_requires": ">=3.9",
    "license": "BSD-3-Clause",
    "key_dependencies": ["brightway25"],
    "sections": [
        {
            "id": "readme",
            "title": "README / Overview",
            "url": "https://github.com/brightway-lca/bw_exiobase",
            "description": "Overview, installation, and usage.",
        },
    ],
}
