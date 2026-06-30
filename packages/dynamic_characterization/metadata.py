"""
Tiny manifest for the `dynamic_characterization` package.
"""

METADATA: dict = {
    "name": "dynamic_characterization",
    "display_name": "Dynamic Characterization",
    "description": "Collection of dynamic characterization functions for life cycle inventories with temporal information. Provides time-dependent characterization factors for climate change and other impact categories, enabling dynamic LCA calculations that account for the timing of emissions (e.g., radiative forcing over time).",
    "github_url": "https://github.com/brightway-lca/dynamic_characterization",
    "github_repo": "brightway-lca/dynamic_characterization",
    "readthedocs_slug": None,
    "docs_url": "https://github.com/brightway-lca/dynamic_characterization",
    "pypi_url": "https://pypi.org/project/dynamic_characterization/",
    "install": {
        "pip": "pip install dynamic_characterization",
        "conda": "conda install -c conda-forge dynamic_characterization",
    },
    "python_requires": ">=3.9",
    "license": "BSD-3-Clause",
    "key_dependencies": ["bw_temporalis or bw_timex", "numpy", "pandas"],
    "sections": [
        {
            "id": "readme",
            "title": "README / Overview",
            "url": "https://github.com/brightway-lca/dynamic_characterization",
            "description": "Overview, installation, and usage.",
        },
    ],
}
