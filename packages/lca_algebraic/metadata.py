"""
Tiny manifest for the `lca_algebraic` package.

This file intentionally stays small: just enough metadata to locate the GitHub
repo, docs root, and section URLs. Documentation itself is fetched on demand
and cached outside the package tree.
"""

METADATA: dict = {
    "name": "lca_algebraic",
    "display_name": "lca_algebraic",
    "description": (
        "lca_algebraic is a Python layer above Brightway2 for defining parametric "
        "LCA inventories with fast computation of impacts, suited for Monte Carlo "
        "analysis and global sensitivity analysis (Sobol indices). It integrates "
        "Sympy so parametric formulas can be written as regular Python expressions. "
        "Provides helper functions for compact, human-readable activity definitions, "
        "parameter management, fast LCA computation, and sensitivity analysis."
    ),
    "github_url": "https://github.com/oie-mines-paristech/lca_algebraic",
    "github_repo": "oie-mines-paristech/lca_algebraic",
    "readthedocs_slug": "lca-algebraic",
    "docs_url": "https://lca-algebraic.readthedocs.io/en/stable/",
    "pypi_url": "https://pypi.org/project/lca-algebraic/",
    "install": {
        "pip": "pip install lca_algebraic",
    },
    "python_requires": ">=3.9",
    "license": "BSD-3-Clause",
    "key_dependencies": ["brightway2 or brightway25", "sympy", "numpy", "pandas"],
    "sections": [
        {
            "id": "overview",
            "title": "Overview",
            "url": "https://lca-algebraic.readthedocs.io/en/stable/",
            "description": (
                "Introduction to lca_algebraic: parametric inventories, Monte Carlo, "
                "global sensitivity analysis (Sobol indices), and installation."
            ),
        },
    ],
}
