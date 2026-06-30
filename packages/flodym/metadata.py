"""
Tiny manifest for the `flodym` package.

This file intentionally stays small: just enough metadata to locate the GitHub
repo, docs root, and section URLs. Documentation itself is fetched on demand
and cached outside the package tree.
"""

METADATA: dict = {
    "name": "flodym",
    "display_name": "flodym",
    "description": (
        "flodym (Flexible Open Dynamic Material Systems Model) is a Python library "
        "for building dynamic material flow analysis (MFA) models. It is an adaptation "
        "of ODYM, providing: the MFASystem class as a template for custom MFA models; "
        "FlodymArray for dimension-aware multi-dimensional array operations (wrapping "
        "numpy einsum); stock accumulation classes with age-cohort tracking and "
        "lifetime distributions; and flexible data input, export, and visualization. "
        "Backed by Pydantic for type-checked system setup. Published in the Journal "
        "of Open Source Software (JOSS, 2026)."
    ),
    "github_url": "https://github.com/pik-piam/flodym",
    "github_repo": "pik-piam/flodym",
    "readthedocs_slug": "flodym",
    "docs_url": "https://flodym.readthedocs.io/en/latest/",
    "pypi_url": "https://pypi.org/project/flodym/",
    "install": {
        "pip": "pip install flodym",
    },
    "python_requires": ">=3.10",
    "license": "MIT",
    "key_dependencies": ["numpy", "pandas", "pydantic", "matplotlib"],
    "sections": [
        {
            "id": "overview",
            "title": "Overview",
            "url": "https://flodym.readthedocs.io/en/latest/",
            "description": (
                "Introduction to flodym: MFASystem, FlodymArray, stock classes, "
                "installation, why choose flodym (flexibility, simplicity, performance), "
                "citation, and contribution guide."
            ),
        },
    ],
}
