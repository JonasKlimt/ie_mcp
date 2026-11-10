"""Tests that need the internet. Skipped by default; run with: pytest -m network"""

from __future__ import annotations

import pytest

from core import github, pypi, source_lookup
from core.local_source import find_in_files

pytestmark = pytest.mark.network

# A small pure-Python package from the registry, with a fixed old release.
PACKAGE = "stats_arrays"
META = {"name": "stats_arrays", "github_repo": "brightway-lca/stats_arrays"}
OLD_VERSION = "0.6.5"


def test_pypi_lists_versions_newest_first() -> None:
    versions = pypi.list_versions(PACKAGE)

    assert OLD_VERSION in versions
    assert versions[0] == pypi.latest_version(PACKAGE)


def test_pypi_release_is_downloaded_once_and_searchable() -> None:
    root = pypi.fetch_release(PACKAGE, OLD_VERSION)
    files = pypi.list_release_files(root)

    assert files and all(file.suffix == ".py" for file in files)
    assert find_in_files(files, "UncertaintyBase")
    assert pypi.fetch_release(PACKAGE, OLD_VERSION) == root  # served from the cache


def test_unknown_version_is_not_on_pypi() -> None:
    with pytest.raises(pypi.VersionNotOnPyPI):
        pypi.fetch_release(PACKAGE, "0.0.0.dev999")


def test_other_version_comes_from_pypi() -> None:
    result = source_lookup.get_function_source(
        PACKAGE, META, "UncertaintyBase", OLD_VERSION, "signature"
    )

    assert (result["source"], result["version"]) == ("pypi", OLD_VERSION)
    assert result["kind"] == "class"


def test_head_comes_from_github() -> None:
    result = source_lookup.get_function_source(
        PACKAGE, META, "UncertaintyBase", "HEAD", "signature"
    )

    assert (result["source"], result["version"]) == ("github", "HEAD")
    assert result["html_url"].startswith("https://github.com/brightway-lca/stats_arrays/blob/HEAD/")


def test_github_tags_are_listed() -> None:
    assert github.list_tags(META["github_repo"])
