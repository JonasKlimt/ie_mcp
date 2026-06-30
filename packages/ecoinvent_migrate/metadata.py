"""
Tiny manifest for the `ecoinvent_migrate` package.
"""

METADATA: dict = {
    "name": "ecoinvent_migrate",
    "display_name": "Ecoinvent Migrate",
    "description": "Code to generate Randonneur-format migration files for ecoinvent database releases. Provides tools to create transformation datasets that map activities and flows from one ecoinvent version to another, used for updating existing Brightway projects to newer ecoinvent releases.",
    "github_url": "https://github.com/brightway-lca/ecoinvent_migrate",
    "github_repo": "brightway-lca/ecoinvent_migrate",
    "readthedocs_slug": None,
    "docs_url": "https://github.com/brightway-lca/ecoinvent_migrate",
    "pypi_url": None,
    "install": {
        "pip": "pip install ecoinvent_migrate",  # check GitHub for install instructions
    },
    "python_requires": ">=3.9",
    "license": "BSD-3-Clause",
    "key_dependencies": ["randonneur", "ecoinvent_interface"],
    "sections": [
        {
            "id": "readme",
            "title": "README / Overview",
            "url": "https://github.com/brightway-lca/ecoinvent_migrate",
            "description": "Overview, installation, and usage.",
        },
    ],
}
