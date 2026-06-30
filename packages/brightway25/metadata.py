"""
Tiny manifest for the `brightway25` package.

This file intentionally stays small: just enough metadata to locate the GitHub
repo, docs root, and section URLs. Documentation itself is fetched on demand
and cached outside the package tree.
"""

METADATA: dict = {
    "name": "brightway25",
    "display_name": "Brightway 2.5",
    "description": (
        "A metapackage/wrapper library for easy installation of the Brightway 2.5 "
        "life cycle assessment (LCA) framework. It installs all core brightway2.5 "
        "components: bw2analyzer, bw2calc, bw2data, bw2io, bw2parameters, "
        "bw_migrations, bw_processing, bw_simapro_csv, ecoinvent_interface, "
        "matrix_utils, mrio_common_metadata, multifunctional, randonneur, "
        "randonneur_data, and stats_arrays."
    ),
    "github_url": "https://github.com/brightway-lca/brightway25",
    "github_repo": "brightway-lca/brightway25",
    "readthedocs_slug": None,
    "docs_url": "https://docs.brightway.dev/en/latest/",
    "pypi_url": "https://pypi.org/project/brightway25/",
    "install": {
        "pip": "pip install brightway25",
        "conda": "conda install -c conda-forge brightway25",
    },
    "python_requires": ">=3.9",
    "license": "BSD-3-Clause",
    "key_dependencies": [
        "bw2analyzer",
        "bw2calc",
        "bw2data",
        "bw2io",
        "bw2parameters",
        "bw_migrations",
        "bw_processing",
        "bw_simapro_csv",
        "ecoinvent_interface",
        "matrix_utils",
        "mrio_common_metadata",
        "multifunctional",
        "randonneur",
        "randonneur_data",
        "stats_arrays",
    ],
    "sections": [
        {
            "id": "overview",
            "title": "What is Brightway?",
            "url": "https://docs.brightway.dev/en/latest/",
            "description": (
                "Introduction to Brightway LCA framework, core concepts, "
                "and the brightway2.5 package ecosystem."
            ),
        },
        {
            "id": "installation",
            "title": "Installation",
            "url": "https://docs.brightway.dev/en/latest/content/installation/index.html",
            "description": (
                "Installation instructions for brightway2.5 on all platforms."
            ),
        },
        {
            "id": "cheatsheet",
            "title": "Cheat Sheet",
            "url": "https://docs.brightway.dev/en/latest/content/cheatsheet/index.html",
            "description": (
                "Quick reference for common Brightway operations."
            ),
        },
        {
            "id": "api",
            "title": "API Reference",
            "url": "https://docs.brightway.dev/en/latest/content/api/index.html",
            "description": (
                "Full API reference for brightway2.5."
            ),
        },
    ],
}
