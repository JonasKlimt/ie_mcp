"""
Tiny manifest for the `simapro_ecoinvent_elementary_flows` package.
"""

METADATA: dict = {
    "name": "simapro_ecoinvent_elementary_flows",
    "display_name": "SimaPro Ecoinvent Elementary Flows",
    "description": "Utilities and correspondence lists for working with SimaPro and ecoinvent elementary flows. Provides mapping tables between SimaPro's flow nomenclature and ecoinvent's elementary flows, used in bw2io and bw_simapro_csv for import/export workflows.",
    "github_url": "https://github.com/brightway-lca/simapro_ecoinvent_elementary_flows",
    "github_repo": "brightway-lca/simapro_ecoinvent_elementary_flows",
    "readthedocs_slug": None,
    "docs_url": "https://github.com/brightway-lca/simapro_ecoinvent_elementary_flows",
    "pypi_url": None,
    "install": {
        "pip": "pip install simapro_ecoinvent_elementary_flows",
    },
    "python_requires": ">=3.9",
    "license": "BSD-3-Clause",
    "key_dependencies": ["bw_simapro_csv", "bw2io"],
    "sections": [
        {
            "id": "readme",
            "title": "README / Overview",
            "url": "https://github.com/brightway-lca/simapro_ecoinvent_elementary_flows",
            "description": "Overview, installation, and usage.",
        },
    ],
}
