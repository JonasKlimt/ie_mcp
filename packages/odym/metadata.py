"""
Tiny manifest for the `odym` package.

This file intentionally stays small: just enough metadata to locate the GitHub
repo, docs root, and section URLs. Documentation itself is fetched on demand
and cached outside the package tree.
"""

METADATA: dict = {
    "name": "odym",
    "display_name": "ODYM",
    "description": (
        "ODYM (Open Dynamic Material Systems Model) is an open-source Python framework "
        "for dynamic material flow analysis (MFA). It models biophysical stock-flow "
        "relations in socioeconomic metabolism using an object-based description of "
        "systems, processes, stocks, flows, and parameters. ODYM can simultaneously "
        "trace products, components, materials, alloys, waste, and chemical elements. "
        "All input/output data are stored in a standardized file format for exchange "
        "across projects. Includes an extended library for dynamic stock modeling."
    ),
    "github_url": "https://github.com/IndEcol/ODYM",
    "github_repo": "IndEcol/ODYM",
    "readthedocs_slug": "odym",
    "docs_url": "https://odym.readthedocs.io/en/latest/",
    "pypi_url": None,
    "install": {
        "git": "git clone https://github.com/IndEcol/ODYM.git && pip install -e ODYM",
    },
    "python_requires": ">=3.8",
    "license": "MIT",
    "key_dependencies": ["numpy", "pandas", "scipy", "matplotlib"],
    "sections": [
        {
            "id": "overview",
            "title": "Overview",
            "url": "https://odym.readthedocs.io/en/latest/",
            "description": (
                "Introduction to ODYM: dynamic material flow analysis, object-based "
                "system description, stock modeling, and data format."
            ),
        },
    ],
}
