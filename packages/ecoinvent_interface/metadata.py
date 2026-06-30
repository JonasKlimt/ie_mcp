"""
Tiny manifest for the `ecoinvent_interface` package.

This file intentionally stays small: just enough metadata to locate the GitHub
repo, docs root, and section URLs. Documentation itself is fetched on demand
and cached outside the package tree.
"""

METADATA: dict = {
    "name": "ecoinvent_interface",
    "display_name": "ecoinvent_interface",
    "description": (
        "Unofficial Python interface to ecoinvent data. Provides programmatic "
        "access to download ecoinvent databases directly, including version "
        "selection, system model selection (cut-off, consequential, APOS), and "
        "authentication handling. Used by premise and other tools."
    ),
    "github_url": "https://github.com/brightway-lca/ecoinvent_interface",
    "github_repo": "brightway-lca/ecoinvent_interface",
    "readthedocs_slug": None,
    "docs_url": "https://github.com/brightway-lca/ecoinvent_interface",
    "pypi_url": "https://pypi.org/project/ecoinvent_interface/",
    "install": {
        "pip": "pip install ecoinvent_interface",
        "conda": "conda install -c conda-forge ecoinvent_interface",
    },
    "python_requires": ">=3.9",
    "license": "BSD-3-Clause",
    "key_dependencies": [
        "requests",
        "platformdirs",
        "pydantic",
    ],
    "sections": [
        {
            "id": "readme",
            "title": "README / Overview",
            "url": "https://github.com/brightway-lca/ecoinvent_interface",
            "description": (
                "Overview of ecoinvent_interface: authentication, available "
                "versions, downloading databases."
            ),
        },
    ],
}
