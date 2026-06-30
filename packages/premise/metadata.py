"""
Tiny manifest for the `premise` package.

This file intentionally stays small: just enough metadata to locate the GitHub
repo, docs root, and section URLs. Documentation itself is fetched on demand
and cached outside the package tree.
"""

METADATA: dict = {
    "name": "premise",
    "display_name": "premise",
    "description": (
        "premise (PRospective EnvironMental Impact AsSEssment) is a Python tool "
        "for prospective life cycle assessment (LCA). It projects the ecoinvent 3 "
        "inventory database into the future by coupling it with scenarios from "
        "Integrated Assessment Models (IAMs) such as REMIND, IMAGE, MESSAGEix, "
        "TIAM-UCL, and GCAM. It modifies ecoinvent datasets to reflect projected "
        "energy policy trajectories, emerging technologies, shifting market shares, "
        "and technology efficiencies. Outputs can be used in Brightway 2/2.5, "
        "Activity Browser, SimaPro, OpenLCA, or directly in Python."
    ),
    "github_url": "https://github.com/polca/premise",
    "github_repo": "polca/premise",
    "readthedocs_slug": "premise",
    "docs_url": "https://premise.readthedocs.io/en/latest/",
    "pypi_url": "https://pypi.org/project/premise/",
    "install": {
        "pip (Brightway 2.5)": "pip install premise",
        "pip (Brightway 2)": "pip install \"premise[bw2]\"",
        "conda (Brightway 2.5)": "conda install -c conda-forge premise-bw25",
        "conda (Brightway 2)": "conda install -c conda-forge premise-bw2",
    },
    "python_requires": ">=3.10",
    "license": "BSD-3-Clause",
    "key_dependencies": ["brightway2 or brightway2.5", "ecoinvent license (not included)"],
    "note": (
        "An encryption key is required to use standard IAM scenarios. "
        "Request it by email from romain.sacchi@psi.ch."
    ),
    "sections": [
        {
            "id": "introduction",
            "title": "In a nutshell",
            "url": "https://premise.readthedocs.io/en/latest/introduction.html",
            "description": (
                "Overview, purpose, scope, IAM models supported, workflow, "
                "installation, and quick-start usage."
            ),
        },
        {
            "id": "extract",
            "title": "EXTRACT",
            "url": "https://premise.readthedocs.io/en/latest/extract.html",
            "description": (
                "How premise extracts data: supported ecoinvent versions, "
                "input sources (Brightway2 project or ecospold2 files), "
                "additional inventories (PV, hydrogen, steel, cement, vehicles…), "
                "and IAM data collection."
            ),
        },
        {
            "id": "transform",
            "title": "TRANSFORM",
            "url": "https://premise.readthedocs.io/en/latest/transform.html",
            "description": (
                "Sector-by-sector transformation: electricity, transport, cement, "
                "steel, fuels, hydrogen, heat, batteries, metals, biomass, DAC, "
                "and more. Explains efficiency adjustments, market creation, "
                "regionalization, and GAINS emission factors."
            ),
        },
        {
            "id": "load",
            "title": "LOAD",
            "url": "https://premise.readthedocs.io/en/latest/load.html",
            "description": (
                "Exporting modified databases: back to Brightway2/2.5, "
                "as sparse matrices, as SimaPro CSV, as OpenLCA CSV, "
                "or as a data package."
            ),
        },
        {
            "id": "mapping",
            "title": "Mapping",
            "url": "https://premise.readthedocs.io/en/latest/mapping.html",
            "description": (
                "How IAM model variables are mapped to ecoinvent datasets. "
                "How to link a new IAM model, IAM scenario file format."
            ),
        },
        {
            "id": "user_scenarios",
            "title": "User-defined scenarios",
            "url": "https://premise.readthedocs.io/en/latest/user_scenarios.html",
            "description": (
                "How to create and use your own custom scenarios "
                "(datapackage.json, scenario data CSV, config.yaml). "
                "Includes an ammonia scenario example."
            ),
        },
        {
            "id": "consequential",
            "title": "Consequential modelling",
            "url": "https://premise.readthedocs.io/en/latest/consequential.html",
            "description": (
                "How to run premise in consequential LCA mode: "
                "range time, duration, foresight, lead time, "
                "capital replacement rate, and database creation."
            ),
        },
        {
            "id": "faq",
            "title": "Frequently Asked Questions",
            "url": "https://premise.readthedocs.io/en/latest/faq.html",
            "description": (
                "Answers to common questions about ecoinvent, IAM models, "
                "regionalization, efficiency adjustments, additional inventories, "
                "and data sharing."
            ),
        },
    ],
}
