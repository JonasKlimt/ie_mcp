"""
Tiny manifest for the `edges` package.

This file intentionally stays small: just enough metadata to locate the GitHub
repo, docs root, and section URLs. Documentation itself is fetched on demand
and cached outside the package tree.
"""

METADATA: dict = {
    "name": "edges",
    "display_name": "edges",
    "description": (
        "edges is a Python library for flexible, edge-based Life Cycle Impact "
        "Assessment (LCIA) for the Brightway2/Brightway2.5 LCA framework. "
        "Unlike traditional LCIA methods that apply characterization factors (CFs) "
        "solely to nodes (elementary flows), edges applies CFs directly on the "
        "exchanges between suppliers and consumers, enabling context-sensitive "
        "impact characterization. Supports geographic resolution (346 regions), "
        "scenario-based and parameterized CFs, uncertainty modeling, technosphere "
        "CFs (e.g., GeoPolRisk), and life cycle costing (LCC). Built-in methods "
        "include AWARE 2.0, ImpactWorld+ 2.1, GeoPolRisk, GLAM3, and IBIF v2."
    ),
    "github_url": "https://github.com/Laboratory-for-Energy-Systems-Analysis/edges",
    "github_repo": "Laboratory-for-Energy-Systems-Analysis/edges",
    "readthedocs_slug": "edges",
    "docs_url": "https://edges.readthedocs.io/en/stable/",
    "pypi_url": "https://pypi.org/project/edges/",
    "install": {
        "pip": "pip install edges",
    },
    "python_requires": ">=3.9",
    "license": "MIT",
    "key_dependencies": ["brightway25", "numpy", "pandas"],
    "sections": [
        {
            "id": "overview",
            "title": "Overview",
            "url": "https://edges.readthedocs.io/en/stable/",
            "description": (
                "Introduction to edge-based LCIA, citation, and table of contents."
            ),
        },
        {
            "id": "theory",
            "title": "Theory",
            "url": "https://edges.readthedocs.io/en/stable/theory.html",
            "description": (
                "Theoretical background: node-based vs edge-based LCIA, matching logic, "
                "regionalization mechanisms, symbolic and scenario-based CFs, "
                "uncertainty modeling, and technosphere CFs."
            ),
        },
        {
            "id": "quickstart",
            "title": "Quick Start",
            "url": "https://edges.readthedocs.io/en/stable/quickstart.html",
            "description": (
                "Quick-start guide showing how to set up and run edge-based LCIA "
                "with a brightway2.5 project."
            ),
        },
        {
            "id": "user_guide",
            "title": "User Guide",
            "url": "https://edges.readthedocs.io/en/stable/user_guide.html",
            "description": (
                "Step-by-step usage: simple LCIA, built-in methods, regionalized LCIA, "
                "custom method JSON files, parameterized CFs, uncertainty-aware LCIA, "
                "joint Monte Carlo, technosphere CFs, and exporting results."
            ),
        },
        {
            "id": "methods",
            "title": "Available Methods",
            "url": "https://edges.readthedocs.io/en/stable/methods.html",
            "description": (
                "Catalogue of built-in LCIA methods: AWARE 2.0, GeoPolRisk 1.0, "
                "ImpactWorld+ 2.1, SCP 1.0, parameterized GWP, GLAM3, IBIF v2."
            ),
        },
        {
            "id": "nomenclature",
            "title": "Nomenclature and Custom LCIA Method Format",
            "url": "https://edges.readthedocs.io/en/stable/nomenclature.html",
            "description": (
                "File structure, exchange structure, matching logic, advanced features, "
                "examples, and saving/loading custom LCIA method JSON files."
            ),
        },
        {
            "id": "api_reference",
            "title": "API Reference",
            "url": "https://edges.readthedocs.io/en/stable/api_reference.html",
            "description": (
                "Full API reference for EdgeLCIA and CostLCIA classes and functions."
            ),
        },
    ],
}
