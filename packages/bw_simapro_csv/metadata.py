"""
Tiny manifest for the `bw_simapro_csv` package.

This file intentionally stays small: just enough metadata to locate the GitHub
repo, docs root, and section URLs. Documentation itself is fetched on demand
and cached outside the package tree.
"""

METADATA: dict = {
    "name": "bw_simapro_csv",
    "display_name": "bw_simapro_csv",
    "description": (
        "Read and parse SimaPro CSV LCI and LCIA files for import into the "
        "Brightway LCA framework. Handles the SimaPro CSV export format, including "
        "processes, flows, impact assessment methods, and waste scenarios."
    ),
    "github_url": "https://github.com/brightway-lca/bw_simapro_csv",
    "github_repo": "brightway-lca/bw_simapro_csv",
    "readthedocs_slug": None,
    "docs_url": "https://github.com/brightway-lca/bw_simapro_csv",
    "pypi_url": "https://pypi.org/project/bw_simapro_csv/",
    "install": {
        "pip": "pip install bw_simapro_csv",
        "conda": "conda install -c conda-forge bw_simapro_csv",
    },
    "python_requires": ">=3.9",
    "license": "BSD-3-Clause",
    "key_dependencies": [
        "bw2io",
        "randonneur",
        "pydantic",
        "loguru",
    ],
    "sections": [
        {
            "id": "readme",
            "title": "README / Overview",
            "url": "https://github.com/brightway-lca/bw_simapro_csv",
            "description": (
                "Overview of bw_simapro_csv: supported SimaPro CSV blocks, "
                "parsing, and usage examples."
            ),
        },
    ],
}
