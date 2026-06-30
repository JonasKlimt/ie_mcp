"""
Tiny manifest for the `bw_interface_schemas` package.
"""

METADATA: dict = {
    "name": "bw_interface_schemas",
    "display_name": "bw_interface_schemas",
    "description": (
        "Interface schemas for standardized data transfer in the Brightway LCA framework. "
        "Defines Pydantic data models and schemas for activities, exchanges, LCIA methods, "
        "and other LCA data structures to ensure interoperability between Brightway "
        "components."
    ),
    "github_url": "https://github.com/brightway-lca/bw_interface_schemas",
    "github_repo": "brightway-lca/bw_interface_schemas",
    "readthedocs_slug": None,
    "docs_url": "https://github.com/brightway-lca/bw_interface_schemas",
    "pypi_url": "https://pypi.org/project/bw_interface_schemas/",
    "install": {
        "pip": "pip install bw_interface_schemas",
        "conda": "conda install -c conda-forge bw_interface_schemas",
    },
    "python_requires": ">=3.9",
    "license": "BSD-3-Clause",
    "key_dependencies": ["brightway25"],
    "sections": [
        {
            "id": "readme",
            "title": "README / Overview",
            "url": "https://github.com/brightway-lca/bw_interface_schemas",
            "description": "Overview, installation, and usage.",
        },
    ],
}
