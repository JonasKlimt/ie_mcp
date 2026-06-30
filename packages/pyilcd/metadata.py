"""
Tiny manifest for the `pyilcd` package.
"""

METADATA: dict = {
    "name": "pyilcd",
    "display_name": "PyILCD",
    "description": "A Python package that converts ILCD (International Life Cycle Data System) XML formats to their Python object equivalents and exports the same data back to XML. Provides full round-trip XML parsing for the ILCD data exchange format used by openLCA and other LCA tools.",
    "github_url": "https://github.com/brightway-lca/pyilcd",
    "github_repo": "brightway-lca/pyilcd",
    "readthedocs_slug": None,
    "docs_url": "https://github.com/brightway-lca/pyilcd",
    "pypi_url": "https://pypi.org/project/pyilcd/",
    "install": {
        "pip": "pip install pyilcd",
        "conda": "conda install -c conda-forge pyilcd",
    },
    "python_requires": ">=3.9",
    "license": "BSD-3-Clause",
    "key_dependencies": ["lxml"],
    "sections": [
        {
            "id": "readme",
            "title": "README / Overview",
            "url": "https://github.com/brightway-lca/pyilcd",
            "description": "Overview, installation, and usage.",
        },
    ],
}
