"""
Tiny manifest for the `pyecospold` package.
"""

METADATA: dict = {
    "name": "pyecospold",
    "display_name": "PyEcoSpold",
    "description": "A Python package that converts ecospold XML formats (EcoSpold1 and EcoSpold2) to their Python object equivalents and exports the same data back to XML. Provides full round-trip XML parsing for the ecoinvent EcoSpold data exchange format.",
    "github_url": "https://github.com/brightway-lca/pyecospold",
    "github_repo": "brightway-lca/pyecospold",
    "readthedocs_slug": None,
    "docs_url": "https://github.com/brightway-lca/pyecospold",
    "pypi_url": "https://pypi.org/project/pyecospold/",
    "install": {
        "pip": "pip install pyecospold",
        "conda": "conda install -c conda-forge pyecospold",
    },
    "python_requires": ">=3.9",
    "license": "BSD-3-Clause",
    "key_dependencies": ["lxml"],
    "sections": [
        {
            "id": "readme",
            "title": "README / Overview",
            "url": "https://github.com/brightway-lca/pyecospold",
            "description": "Overview, installation, and usage.",
        },
    ],
}
