"""
Tiny manifest for the `bw_recipe_2016` package.
"""

METADATA: dict = {
    "name": "bw_recipe_2016",
    "display_name": "bw_recipe_2016",
    "description": (
        "ReCiPe 2016 life cycle impact assessment (LCIA) method for the Brightway LCA "
        "framework. Provides midpoint and endpoint characterization factors for the "
        "ReCiPe 2016 methodology in a Brightway-compatible format."
    ),
    "github_url": "https://github.com/brightway-lca/bw_recipe_2016",
    "github_repo": "brightway-lca/bw_recipe_2016",
    "readthedocs_slug": None,
    "docs_url": "https://github.com/brightway-lca/bw_recipe_2016",
    "pypi_url": "https://pypi.org/project/bw_recipe_2016/",
    "install": {
        "pip": "pip install bw_recipe_2016",
        "conda": "conda install -c conda-forge bw_recipe_2016",
    },
    "python_requires": ">=3.9",
    "license": "BSD-3-Clause",
    "key_dependencies": ["brightway25"],
    "sections": [
        {
            "id": "readme",
            "title": "README / Overview",
            "url": "https://github.com/brightway-lca/bw_recipe_2016",
            "description": "Overview, installation, and usage.",
        },
    ],
}
