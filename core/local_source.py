"""
Finds functions, methods and classes in Python files on disk, and searches them as text.

Used for the installed package in the target environment and for files unpacked from
PyPI or downloaded from GitHub, so all three origins return the same shape.
"""

from __future__ import annotations

import ast
import json
import os
import textwrap
import warnings
from dataclasses import dataclass, field
from pathlib import Path, PurePath
from typing import Any
from urllib.parse import urlparse
from urllib.request import url2pathname

from .config import setting
from .environment import get_distribution_info

SKIPPED_DIRECTORIES = frozenset({"build", "dist", "node_modules", "__pycache__", "venv", "env"})
MAX_SEARCH_RESULTS = int(setting("limits", "max_source_matches"))
MAX_LINE_LENGTH = int(setting("limits", "max_line_length"))
MAX_INHERITANCE_STEPS = int(setting("limits", "max_inheritance_steps"))

_DEFINITION_NODES = (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)
DefinitionNode = ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef


@dataclass
class Definition:
    """One function, method or class found in a Python file.

    Attributes:
        qualified_name: Dotted name inside the file, e.g. "LCA.lci".
        kind: "function", "method" or "class".
        line: Line number of the def or class statement.
        signature: Decorators plus the def or class header.
        docstring: The docstring, or None.
        code: Full source text, dedented.
        methods: Signatures of the methods, for a class.
        bases: Base classes as written in the source, for a class.
    """

    qualified_name: str
    kind: str
    line: int
    signature: str
    docstring: str | None
    code: str
    methods: list[str] = field(default_factory=list)
    bases: list[str] = field(default_factory=list)


@dataclass
class InstalledSource:
    """The Python files of one installed distribution.

    Attributes:
        version: Installed version.
        files: Absolute paths of the Python files.
    """

    version: str
    files: list[Path]


# ---------------------------------------------------------------------------
# Finding the installed files
# ---------------------------------------------------------------------------


def _parse_direct_url(text: str | None) -> dict[str, Any]:
    """Parse the direct_url.json of a distribution.

    Args:
        text: Raw text of direct_url.json, or None if the file is absent.

    Returns:
        The decoded document, or an empty dict if it is absent or malformed.
    """
    try:
        return json.loads(text) if text else {}
    except json.JSONDecodeError:
        return {}


def _editable_roots(direct_url: dict[str, Any], pth_lines: list[str]) -> list[Path]:
    """Find the source folders of an editable install.

    Folders listed in the .pth file are preferred because they point at the
    importable code (e.g. src/). The project folder from direct_url.json is the
    fallback when the .pth file only installs an import hook.

    Args:
        direct_url: Parsed direct_url.json (empty if absent).
        pth_lines: Lines of the distribution's .pth files.

    Returns:
        Existing source folders, possibly empty.
    """
    roots = [Path(line.strip()) for line in pth_lines if line.strip()]
    roots = [root for root in roots if root.is_absolute() and root.is_dir()]
    url = direct_url.get("url", "")
    if roots or not url.startswith("file:"):
        return roots
    project = Path(url2pathname(urlparse(url).path))
    return [project] if project.is_dir() else []


def _walk_python_files(root: Path) -> list[Path]:
    """Collect the .py files below a folder, skipping tool and build folders.

    Args:
        root: Folder to walk.

    Returns:
        Sorted absolute paths of the Python files.
    """
    found: list[Path] = []
    for folder, subfolders, filenames in os.walk(root):
        subfolders[:] = [
            name
            for name in subfolders
            if name not in SKIPPED_DIRECTORIES
            and not name.startswith(".")
            and not name.endswith(".egg-info")
        ]
        found.extend(Path(folder) / name for name in filenames if name.endswith(".py"))
    return sorted(found)


def list_installed_source(pypi_name: str) -> InstalledSource | None:
    """List the Python files of a distribution installed in the target environment.

    Regular installs are read from the distribution's file record. Editable
    installs are resolved to their real source folder.

    Args:
        pypi_name: Distribution name as published on PyPI.

    Returns:
        Version and files of the installed distribution, or None if it is not
        installed.

    Raises:
        TargetEnvironmentError: If the target interpreter cannot be inspected.
    """
    info = get_distribution_info(pypi_name)
    if not info["installed"]:
        return None
    files = [Path(path) for path in info["py_files"]]
    direct_url = _parse_direct_url(info["direct_url"])
    if direct_url.get("dir_info", {}).get("editable") or not files:
        roots = _editable_roots(direct_url, info["pth_lines"])
        files = [path for root in roots for path in _walk_python_files(root)] or files
    return InstalledSource(info["version"], files)


# ---------------------------------------------------------------------------
# AST extraction
# ---------------------------------------------------------------------------


def _signature(node: DefinitionNode) -> str:
    """Rebuild the header of a definition: decorators plus the def or class line.

    Args:
        node: Function or class node.

    Returns:
        The signature as source text, without the body.
    """
    lines = [f"@{ast.unparse(decorator)}" for decorator in node.decorator_list]
    if isinstance(node, ast.ClassDef):
        parents = [ast.unparse(base) for base in node.bases]
        parents += [ast.unparse(keyword) for keyword in node.keywords]
        lines.append(
            f"class {node.name}({', '.join(parents)}):" if parents else f"class {node.name}:"
        )
        return "\n".join(lines)
    keyword = "async def" if isinstance(node, ast.AsyncFunctionDef) else "def"
    returns = f" -> {ast.unparse(node.returns)}" if node.returns else ""
    lines.append(f"{keyword} {node.name}({ast.unparse(node.args)}){returns}:")
    return "\n".join(lines)


def _node_code(node: DefinitionNode, lines: list[str]) -> str:
    """Cut the source of a node, including its decorators, out of the file.

    Args:
        node: Function or class node.
        lines: The file's lines, with line endings.

    Returns:
        The dedented source text of the node.
    """
    first = min([node.lineno] + [d.lineno for d in node.decorator_list])
    return textwrap.dedent("".join(lines[first - 1 : node.end_lineno]))


def _walk_definitions(
    node: ast.AST, parents: tuple[str, ...], in_class: str | None
) -> list[tuple[tuple[str, ...], DefinitionNode, str | None]]:
    """List all definitions below a node with their qualified-name parts.

    Definitions inside if/try blocks and nested definitions are included.

    Args:
        node: Module, class, function or any other node to look into.
        parents: Qualified-name parts of the enclosing definitions.
        in_class: Name of the directly enclosing class, if any.

    Returns:
        Tuples of (qualified-name parts, node, directly enclosing class name).
    """
    found = []
    for child in ast.iter_child_nodes(node):
        if isinstance(child, _DEFINITION_NODES):
            parts = parents + (child.name,)
            found.append((parts, child, in_class))
            inner_class = child.name if isinstance(child, ast.ClassDef) else None
            found.extend(_walk_definitions(child, parts, inner_class))
        else:
            found.extend(_walk_definitions(child, parents, in_class))
    return found


def _module_parts(file: PurePath | None) -> tuple[str, ...]:
    """Turn a file path into dotted-module parts (bw2calc/lca.py → bw2calc, lca).

    Args:
        file: Path of the Python file, or None if unknown.

    Returns:
        The path parts without suffix; a trailing __init__ is dropped.
    """
    if file is None:
        return ()
    parts = file.with_suffix("").parts
    return parts[:-1] if parts[-1] == "__init__" else parts


def find_definitions(source: str, name: str, file: PurePath | None = None) -> list[Definition]:
    """Find all functions, methods and classes in Python source that match a name.

    A plain name (lci) matches every definition with that name. A dotted name
    (LCA.lci, lca.LCA.lci) must match the end of the qualified name, optionally
    preceded by the module path.

    Args:
        source: Python source text.
        name: Plain or dotted name of a function, method or class.
        file: Path of the file, used to match leading module parts of the name.

    Returns:
        All matching definitions in file order; empty if none match or the
        source cannot be parsed.
    """
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")  # third-party SyntaxWarnings are noise
            tree = ast.parse(source)
    except (SyntaxError, ValueError):
        return []

    wanted = tuple(name.strip().split("."))
    module = _module_parts(file)
    lines = source.splitlines(keepends=True)
    matches = []
    for parts, node, class_name in _walk_definitions(tree, (), None):
        full = module + parts
        if full[-len(wanted) :] != wanted:
            continue
        is_class = isinstance(node, ast.ClassDef)
        methods = [
            _signature(child)
            for child in node.body
            if is_class and isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef))
        ]
        matches.append(
            Definition(
                qualified_name=".".join(parts),
                kind="class" if is_class else ("method" if class_name else "function"),
                line=node.lineno,
                signature=_signature(node),
                docstring=ast.get_docstring(node),
                code=_node_code(node, lines),
                methods=methods,
                bases=[ast.unparse(base) for base in node.bases] if is_class else [],
            )
        )
    return sorted(matches, key=lambda definition: definition.line)


def _read_text(file: Path, texts: dict[Path, str | None] | None = None) -> str | None:
    """Read a source file, tolerating unreadable files and odd encodings.

    Args:
        file: Path of the file.
        texts: Texts already read in this lookup; filled as files are read.

    Returns:
        The file's text, or None if it cannot be read.
    """
    if texts is not None and file in texts:
        return texts[file]
    try:
        text = file.read_text(encoding="utf-8", errors="replace")
    except OSError:
        text = None
    if texts is not None:
        texts[file] = text
    return text


def find_in_files(
    files: list[Path], name: str, texts: dict[Path, str | None] | None = None
) -> list[tuple[Path, Definition]]:
    """Find all definitions matching a name across several Python files.

    Args:
        files: Python files to look in.
        name: Plain or dotted name of a function, method or class.
        texts: Texts already read in this lookup, so files are read only once.

    Returns:
        Pairs of (file, definition) for every match.
    """
    last_part = name.strip().split(".")[-1]
    found = []
    for file in files:
        source = _read_text(file, texts)
        if source is None or last_part not in source:  # cheap filter before parsing
            continue
        found.extend((file, definition) for definition in find_definitions(source, name, file))
    return found


def find_with_inheritance(
    files: list[Path], name: str
) -> tuple[list[tuple[Path, Definition]], str | None]:
    """Find definitions by name, following base classes for inherited methods.

    If Class.method is not defined on the class itself, the base classes that
    live in the same files are searched, nearest first.

    Args:
        files: Python files to look in.
        name: Plain or dotted name of a function, method or class.

    Returns:
        The matches, and a note naming the base class if the method was
        inherited (otherwise None).
    """
    texts: dict[Path, str | None] = {}
    matches = find_in_files(files, name, texts)
    if matches or "." not in name:
        return matches, None

    owner, method = name.strip().rsplit(".", 1)
    queue, seen = [owner], set()
    while queue and len(seen) < MAX_INHERITANCE_STEPS:
        class_name = queue.pop(0)
        if class_name in seen:
            continue
        seen.add(class_name)
        for _, definition in find_in_files(files, class_name, texts):
            for base in definition.bases:
                base_name = base.split("[")[0].split(".")[-1]  # drop generics and modules
                inherited = find_in_files(files, f"{base_name}.{method}", texts)
                if inherited:
                    note = (
                        f"'{owner}' does not define '{method}'; it inherits it from '{base_name}'."
                    )
                    return inherited, note
                queue.append(base_name)
    return [], None


def search_files(
    files: list[Path], query: str, max_results: int = MAX_SEARCH_RESULTS
) -> list[dict[str, Any]]:
    """Search Python files for a text string, like a case-insensitive grep.

    Args:
        files: Python files to search.
        query: Text to look for.
        max_results: Stop after this many matching lines.

    Returns:
        Dicts with file (Path), line (1-based) and text (the matching line,
        stripped and shortened).
    """
    needle = query.lower()
    results: list[dict[str, Any]] = []
    for file in files:
        source = _read_text(file)
        if source is None or needle not in source.lower():
            continue
        for number, line in enumerate(source.splitlines(), start=1):
            if needle in line.lower():
                results.append(
                    {"file": file, "line": number, "text": line.strip()[:MAX_LINE_LENGTH]}
                )
                if len(results) >= max_results:
                    return results
    return results
