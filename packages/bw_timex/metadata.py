"""
Tiny manifest for the `bw_timex` package.
"""

METADATA: dict = {
    "name": "bw_timex",
    "display_name": "bw_timex",
    "description": (
        "Time-explicit life cycle assessment (LCA) library for Brightway. An advanced "
        "framework for temporal LCA that models the time distribution of environmental "
        "flows and impacts over the life cycle, building on bw_temporalis with additional "
        "functionality for time-explicit supply chains."
    ),
    "github_url": "https://github.com/brightway-lca/bw_timex",
    "github_repo": "brightway-lca/bw_timex",
    "readthedocs_slug": None,
    "docs_url": "https://docs.brightway.dev/projects/bw-timex/en/latest/",
    "pypi_url": "https://pypi.org/project/bw_timex/",
    "install": {
        "pip": "pip install bw_timex",
        "conda": "conda install -c conda-forge bw_timex",
    },
    "python_requires": ">=3.9",
    "license": "BSD-3-Clause",
    "key_dependencies": ["brightway25"],
    "sections": [
        {
            "id": "overview",
            "title": "Documentation",
            "url": "https://docs.brightway.dev/projects/bw-timex/en/latest/",
            "description": "Overview, installation, and usage of bw_timex for time-explicit LCA.",
        },
    ],
}
