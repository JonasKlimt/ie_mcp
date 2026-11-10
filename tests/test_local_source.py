"""Local lookup: AST extraction, text search, and a really installed package (httpx)."""

from __future__ import annotations

from importlib.metadata import version as installed_version
from pathlib import Path

import pytest

from core import source_lookup
from core.local_source import (
    find_definitions,
    find_with_inheritance,
    list_installed_source,
    search_files,
)

HTTPX = {"name": "httpx"}

SAMPLE = '''
import functools


def helper(x: int, *, y: str = "a") -> bool:
    """Tell something about x."""
    return bool(x)


class Outer:
    """An outer class."""

    @functools.cache
    def run(self) -> None:
        """Run the outer thing."""

    class Inner:
        async def run(self, n: int) -> int:
            return n


if True:
    def conditional():
        pass
'''


# --- AST extraction on inline source -------------------------------------------------


def test_plain_function_is_split_into_signature_docstring_and_code() -> None:
    (definition,) = find_definitions(SAMPLE, "helper")

    assert definition.kind == "function"
    assert definition.signature == "def helper(x: int, *, y: str='a') -> bool:"
    assert definition.docstring == "Tell something about x."
    assert definition.code.startswith("def helper(") and "return bool(x)" in definition.code


def test_plain_name_returns_all_matches() -> None:
    names = [d.qualified_name for d in find_definitions(SAMPLE, "run")]
    assert names == ["Outer.run", "Outer.Inner.run"]


def test_dotted_name_selects_one_method() -> None:
    (definition,) = find_definitions(SAMPLE, "Outer.run")

    assert definition.kind == "method"
    assert definition.signature == "@functools.cache\ndef run(self) -> None:"
    assert definition.code.startswith("@functools.cache")

    (inner,) = find_definitions(SAMPLE, "Inner.run")
    assert inner.signature == "async def run(self, n: int) -> int:"


def test_class_name_returns_the_class_with_its_methods() -> None:
    (definition,) = find_definitions(SAMPLE, "Outer")

    assert definition.kind == "class"
    assert definition.signature == "class Outer:"
    assert definition.docstring == "An outer class."
    assert definition.methods == ["@functools.cache\ndef run(self) -> None:"]


def test_module_prefix_is_matched_against_the_file_path() -> None:
    file = Path("pkg") / "sub" / "mod.py"

    assert find_definitions(SAMPLE, "mod.Outer.run", file)
    assert find_definitions(SAMPLE, "pkg.sub.mod.helper", file)
    assert not find_definitions(SAMPLE, "other.Outer.run", file)


def test_definitions_inside_blocks_are_found() -> None:
    assert [d.qualified_name for d in find_definitions(SAMPLE, "conditional")] == ["conditional"]


def test_unparsable_source_gives_no_matches() -> None:
    assert find_definitions("def broken(:", "broken") == []


def test_inherited_method_is_found_on_the_base_class(tmp_path: Path) -> None:
    base = tmp_path / "base.py"
    base.write_text("class Base:\n    def lci(self):\n        return 1\n", encoding="utf-8")
    child = tmp_path / "child.py"
    child.write_text("from base import Base\n\nclass LCA(Base):\n    pass\n", encoding="utf-8")

    matches, note = find_with_inheritance([base, child], "LCA.lci")

    assert [(file.name, d.qualified_name) for file, d in matches] == [("base.py", "Base.lci")]
    assert "inherits it from 'Base'" in note


def test_search_is_case_insensitive_and_limited(tmp_path: Path) -> None:
    file = tmp_path / "mod.py"
    file.write_text("x = 1\nNeedle = 2\n# needle again\n", encoding="utf-8")

    assert search_files([file], "NEEDLE") == [
        {"file": file, "line": 2, "text": "Needle = 2"},
        {"file": file, "line": 3, "text": "# needle again"},
    ]
    assert len(search_files([file], "needle", max_results=1)) == 1


# --- a really installed package ------------------------------------------------------


def test_installed_files_are_listed() -> None:
    installed = list_installed_source("httpx")

    assert installed.version == installed_version("httpx")
    assert installed.files and all(file.is_file() for file in installed.files)
    assert list_installed_source("ie-mcp-package-that-does-not-exist") is None


def test_installed_function() -> None:
    result = source_lookup.get_function_source("httpx", HTTPX, "create_ssl_context", None, "full")

    assert result["source"] == "local"
    assert result["version"] == result["installed_version"] == installed_version("httpx")
    assert result["kind"] == "function"
    assert Path(result["file"]).is_file()
    assert result["code"].startswith("def create_ssl_context(")
    assert result["signature"].startswith("def create_ssl_context(")
    assert result["python_executable_origin"] == "sys.executable"


def test_installed_class_method() -> None:
    result = source_lookup.get_function_source("httpx", HTTPX, "Client.send", None, "full")

    assert result["qualified_name"] == "Client.send"
    assert result["kind"] == "method"
    assert result["source"] == "local"


def test_installed_class() -> None:
    result = source_lookup.get_function_source("httpx", HTTPX, "Timeout", None, "signature")

    assert result["kind"] == "class"
    assert result["signature"].startswith("class Timeout")
    assert any("__init__" in method for method in result["methods"])
    assert "code" not in result


def test_name_with_several_matches_lists_them_without_code() -> None:
    result = source_lookup.get_function_source("httpx", HTTPX, "request", None, "full")

    names = {match["qualified_name"] for match in result["matches"]}
    assert {"request", "Client.request", "AsyncClient.request"} <= names
    assert result["match_count"] == len(result["matches"]) > 1
    assert all("code" not in match and "signature" in match for match in result["matches"])
    assert "Class.method" in result["message"]
    assert result["source"] == "local"


def test_installed_search() -> None:
    results = source_lookup.search_source("httpx", HTTPX, "def create_ssl_context", None)

    assert results[0]["source"] == "local"
    assert results[0]["line"] > 0
    assert "create_ssl_context" in results[0]["text"]


def test_unknown_detail_is_rejected() -> None:
    result = source_lookup.get_function_source("httpx", HTTPX, "Timeout", None, "everything")
    assert "Unknown detail" in result["error"]


@pytest.mark.parametrize("name", ["no_such_function_anywhere", "Client.no_such_method"])
def test_missing_name_is_an_error_with_provenance(name: str) -> None:
    result = source_lookup.get_function_source("httpx", HTTPX, name, None, "full")

    assert "not found" in result["error"]
    assert result["source"] == "local"
    assert result["version"] == installed_version("httpx")
