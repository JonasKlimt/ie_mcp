"""
Tiny manifest for the `bw_temporalis` package.
"""

METADATA: dict = {
    "name": "bw_temporalis",
    "display_name": "bw_temporalis",
    "description": (
        "Temporalis library for time-explicit life cycle assessment (LCA) with Brightway "
        "2.5. Enables dynamic LCA calculations that consider the timing of emissions and "
        "interventions, supporting time-distributed life cycle inventories and dynamic "
        "characterization."
    ),
    "github_url": "https://github.com/brightway-lca/bw_temporalis",
    "github_repo": "brightway-lca/bw_temporalis",
    "readthedocs_slug": "temporalis",
    "docs_url": "https://temporalis.readthedocs.io/en/latest/",
    "pypi_url": "https://pypi.org/project/bw_temporalis/",
    "install": {
        "pip": "pip install bw_temporalis",
        "conda": "conda install -c conda-forge bw_temporalis",
    },
    "python_requires": ">=3.9",
    "license": "BSD-3-Clause",
    "key_dependencies": ["brightway25"],
    "sections": [
        {
            "id": "overview",
            "title": "Documentation",
            "url": "https://temporalis.readthedocs.io/en/latest/",
            "description": "Overview, installation, and usage of bw_temporalis for time-explicit LCA.",
        },
    ],
}
