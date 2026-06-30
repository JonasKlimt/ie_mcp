"""
Tiny manifest for the `wurst` package.

This file intentionally stays small: just enough metadata to locate the GitHub
repo, docs root, and section URLs. Documentation itself is fetched on demand
and cached outside the package tree.
"""

METADATA: dict = {
    "name": "wurst",
    "display_name": "wurst",
    "description": (
        "wurst is a Python package for linking and modifying industrial ecology "
        "models, with a focus on sparse matrices in life cycle assessment (LCA). "
        "It treats each LCI activity as a document with metadata and a list of "
        "exchanges that can be filtered and modified programmatically. Typical "
        "use cases include modifying the ecoinvent LCI database with scenario "
        "data, changing input efficiencies, adjusting market shares, and "
        "regionalising global datasets. It is commonly used alongside Brightway2."
    ),
    "github_url": "https://github.com/polca/wurst",
    "github_repo": "polca/wurst",
    "readthedocs_slug": "wurst",
    "docs_url": "https://wurst.readthedocs.io/index.html",
    "pypi_url": "https://pypi.org/project/wurst/",
    "install": {
        "conda": (
            "conda install -y -q -c conda-forge -c cmutel -c haasad "
            "-c konstantinstadler brightway2 jupyter wurst"
        ),
        "pip": "pip install wurst",
    },
    "python_requires": ">=3.8",
    "license": "BSD-3-Clause",
    "key_dependencies": ["brightway2", "numpy", "scipy"],
    "sections": [
        {
            "id": "introduction",
            "title": "Introduction",
            "url": "https://wurst.readthedocs.io/index.html",
            "description": (
                "Overview of wurst, its document-based approach to LCI modification, "
                "installation instructions, internal data format, searching and "
                "filtering helper functions, exchange iterators (technosphere, "
                "biosphere, production), and the change_exchanges_by_constant_factor "
                "transformation."
            ),
        },
        {
            "id": "technical",
            "title": "Technical API reference",
            "url": "https://wurst.readthedocs.io/technical.html",
            "description": (
                "Full API reference: searching functions (equals, contains, "
                "startswith, either, exclude, doesnt_contain_any, get_many, "
                "get_one), exchange iterators (technosphere, biosphere, production, "
                "reference_product), geo transformation functions "
                "(copy_to_new_location, relink_technosphere_exchanges, "
                "allocate_inputs), and activity transformation utilities."
            ),
        },
    ],
}
