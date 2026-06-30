"""
Tiny manifest for the `regioinvent` package.

This file intentionally stays small: just enough metadata to locate the GitHub
repo, docs root, and section URLs. Documentation itself is fetched on demand
and cached outside the package tree.
"""

METADATA: dict = {
    "name": "regioinvent",
    "display_name": "Regioinvent",
    "description": (
        "Regioinvent is a Python package that automatically regionalizes the ecoinvent "
        "LCA database by connecting it to BACI, an international trade database. "
        "It creates national production processes and consumption markets for traded "
        "commodities, replacing broad regional proxies (RER, RoW, GLO) with "
        "country-specific supply chains based on import and production data. "
        "The package also spatializes elementary flows and connects them to "
        "regionalized LCIA methods (IMPACT World+ v2.1, EF 3.1, ReCiPe 2016 v1.03)."
    ),
    "github_url": "https://github.com/CIRAIG/Regioinvent",
    "github_repo": "CIRAIG/Regioinvent",
    "readthedocs_slug": None,
    "docs_url": "https://github.com/CIRAIG/Regioinvent",
    "pypi_url": "https://pypi.org/project/regioinvent/",
    "install": {
        "pip": "pip install regioinvent",
    },
    "python_requires": ">=3.9",
    "license": "BSD-3-Clause",
    "key_dependencies": ["brightway25", "ecoinvent_interface", "pandas", "numpy"],
    "sections": [
        {
            "id": "readme",
            "title": "README / Overview",
            "url": "https://github.com/CIRAIG/Regioinvent",
            "description": (
                "Overview of Regioinvent: regionalization approach, national production "
                "processes, consumption markets, spatialized elementary flows, "
                "and supported LCIA methods."
            ),
        },
    ],
}
