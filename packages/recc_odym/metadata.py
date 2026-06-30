"""
Tiny manifest for the `recc_odym` package.

This file intentionally stays small: just enough metadata to locate the GitHub
repo, docs root, and section URLs. Documentation itself is fetched on demand
and cached outside the package tree.
"""

METADATA: dict = {
    "name": "recc_odym",
    "display_name": "RECC-ODYM",
    "description": (
        "RECC-ODYM (Resource Efficiency – Climate Change mitigation model) is a "
        "dynamic material flow analysis (MFA) framework built on ODYM for assessing "
        "material efficiency and its links to climate change mitigation. It models "
        "services (motorized transport, residential buildings), in-use stocks of "
        "products, and their material cycles. RECC scenarios are driven by shared "
        "socioeconomic pathways (SSP) and can assess ten material efficiency strategies "
        "simultaneously. Provides life cycle impact results for ambitious "
        "service-material decoupling concurrent with energy system decarbonization."
    ),
    "github_url": "https://github.com/IndEcol/RECC-ODYM",
    "github_repo": "IndEcol/RECC-ODYM",
    "readthedocs_slug": None,
    "docs_url": "https://github.com/IndEcol/RECC-ODYM",
    "pypi_url": None,
    "install": {
        "git": "git clone https://github.com/IndEcol/RECC-ODYM.git",
    },
    "python_requires": ">=3.8",
    "license": "MIT",
    "key_dependencies": ["odym", "numpy", "pandas", "scipy", "matplotlib"],
    "note": (
        "RECC-ODYM is a research model distributed via GitHub, not PyPI. "
        "See the README for setup instructions and the Zenodo repository "
        "(https://doi.org/10.5281/zenodo.3542680) for publications and data."
    ),
    "sections": [
        {
            "id": "readme",
            "title": "README / Overview",
            "url": "https://github.com/IndEcol/RECC-ODYM",
            "description": (
                "Overview of the RECC framework, model versions, scenario structure, "
                "SSP storylines, material efficiency strategies, and links to "
                "publications and data repositories."
            ),
        },
    ],
}
