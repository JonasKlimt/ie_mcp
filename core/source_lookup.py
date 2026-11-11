"""
Routes source lookups: installed files first, then a PyPI release, then GitHub.

The tools pass a package, its registry metadata and an optional version; every result
states its source, version, installed_version, file and python_executable.
"""

from __future__ import annotations

import os
import tarfile
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import httpx

from . import github, pypi
from .config import setting
from .environment import (
    SERVER_ORIGIN,
    environment_fields,
    normalize_version,
    select_environment_hint,
)
from .local_source import (
    Definition,
    find_with_inheritance,
    list_installed_source,
    search_files,
)

MAX_MATCHES = int(setting("limits", "max_source_matches"))
DETAIL_LEVELS = ("full", "signature")
_PYPI_FAILURES = (httpx.HTTPError, ValueError, OSError, tarfile.TarError, zipfile.BadZipFile)
_GITHUB_FAILURES = (httpx.HTTPError, ValueError, OSError)


@dataclass
class SourceFiles:
    """Python files of one package version, ready to be searched.

    Attributes:
        source: Origin of the files: "local", "pypi" or "github".
        version: Exact version (or git ref) the files belong to.
        paths: Absolute paths of the Python files.
        root: Folder the paths are shown relative to; None shows absolute paths.
        web_url: GitHub URL prefix of the files, if they come from GitHub.
        warning: Note about incomplete files, added to every result.
    """

    source: str
    version: str
    paths: list[Path]
    root: Path | None = None
    web_url: str | None = None
    warning: str | None = None


@dataclass
class Route:
    """Outcome of the routing decision for one lookup.

    Attributes:
        source_files: The files to search, if a source could be opened.
        failure_result: The final answer when nothing can be looked up.
        pypi_error: Why PyPI was skipped in favour of GitHub.
    """

    source_files: SourceFiles | None = None
    failure_result: dict[str, Any] | None = None
    pypi_error: str | None = None


def not_installed_message(pypi_name: str, environment: dict[str, Any]) -> str:
    """Build the message for a package that is missing from the target environment.

    Args:
        pypi_name: Distribution name as published on PyPI.
        environment: Result of environment_fields().

    Returns:
        Text that names the interpreter and tells the model to ask the user.
    """
    where = f"({environment['python_executable']}, from {environment['python_executable_origin']})"
    if environment["python_executable_origin"] == SERVER_ORIGIN:
        return (
            f"The user's Python environment is not known yet: the server only sees its "
            f"own Python {where}, where '{pypi_name}' is not installed. "
            f"{select_environment_hint()} Then repeat this call."
        )
    return (
        f"'{pypi_name}' is not installed in the inspected Python environment {where}. "
        f"If this is not the environment of the user's file or project: "
        f"{select_environment_hint()} Otherwise tell the user, show them this "
        f"interpreter path, and ask before falling back to the latest version "
        f"(version='latest')."
    )


def _local_route(pypi_name: str) -> Route:
    """Route a lookup to the installed files.

    Args:
        pypi_name: Distribution name as published on PyPI.

    Returns:
        A route with the installed files, or a failure if there are none.
    """
    installed = list_installed_source(pypi_name)
    if not installed.files:
        message = (
            f"The installed distribution '{pypi_name}' contains no Python source "
            f"files (it may be a metapackage or compiled-only)."
        )
        return Route(failure_result={"error": message})
    return Route(source_files=SourceFiles("local", installed.version, installed.files))


def _github_route(
    package: str, meta: dict[str, Any], version: str, pypi_error: str | None
) -> Route:
    """Route a lookup to the package's GitHub repository at a tag, branch or HEAD.

    Args:
        package: Registry key of the package.
        meta: Registry metadata of the package.
        version: Cleaned version, branch name or "HEAD".
        pypi_error: Why PyPI could not serve this version, if it was tried.

    Returns:
        A route with the downloaded files, or a failure.
    """
    notes = {"pypi_error": pypi_error} if pypi_error else {}
    github_repo = meta.get("github_repo")
    if not github_repo:
        message = f"No GitHub repository registered for '{package}'."
        return Route(failure_result={"error": message, **notes})
    try:
        fetched = github.fetch_ref_files(package, github_repo, version)
    except _GITHUB_FAILURES as exc:
        message = (
            f"Version '{version}' could not be read from GitHub ({github_repo}): {exc}. "
            f"Call list_source_versions to see the available versions."
        )
        return Route(failure_result={"error": message, **notes})
    web_url = f"https://github.com/{github_repo}/blob/{fetched.ref}"
    warning = (
        f"The repository has more than {github.MAX_REPOSITORY_FILES} Python files; "
        f"only the first {github.MAX_REPOSITORY_FILES} were read."
        if fetched.truncated
        else None
    )
    source_files = SourceFiles("github", fetched.ref, fetched.paths, fetched.root, web_url, warning)
    return Route(source_files=source_files, pypi_error=pypi_error)


def _remote_route(package: str, meta: dict[str, Any], pypi_name: str, version: str) -> Route:
    """Route a lookup to PyPI, or to GitHub if PyPI cannot serve the version.

    Args:
        package: Registry key of the package.
        meta: Registry metadata of the package.
        pypi_name: Distribution name as published on PyPI.
        version: Cleaned version, "latest", "HEAD" or a branch name.

    Returns:
        A route with the unpacked PyPI release or the GitHub files, or a failure.
    """
    if version.upper() == "HEAD":
        return _github_route(package, meta, "HEAD", None)
    try:
        if version.lower() == "latest":
            version = pypi.latest_version(pypi_name)
        root = pypi.fetch_release(pypi_name, version)
    except pypi.VersionNotOnPyPI as exc:
        return _github_route(package, meta, version, str(exc))
    except _PYPI_FAILURES as exc:
        return _github_route(package, meta, version, f"PyPI download failed: {exc}")
    paths = pypi.list_release_files(root)
    return Route(source_files=SourceFiles("pypi", version, paths, root))


def choose_route(
    package: str, meta: dict[str, Any], version: str | None, environment: dict[str, Any]
) -> Route:
    """Decide where the source of a package version is read from.

    No version, or the installed version, is read locally. Another version is
    read from PyPI, then GitHub. Not installed and no version is a failure.

    Args:
        package: Registry key of the package.
        meta: Registry metadata of the package.
        version: Requested version as given by the caller, or None.
        environment: Result of environment_fields().

    Returns:
        The route: local, PyPI or GitHub files, or a failure.
    """
    pypi_name = meta.get("name", package)
    requested = normalize_version(version)
    installed = environment["installed_version"]
    if requested is None:
        if "environment_error" in environment:
            return Route(failure_result={"error": environment["environment_error"]})
        if installed is None:
            message = not_installed_message(pypi_name, environment)
            return Route(failure_result={"status": "not_installed", "message": message})
        return _local_route(pypi_name)
    if installed is not None and requested == normalize_version(installed):
        return _local_route(pypi_name)
    return _remote_route(package, meta, pypi_name, requested)


def _open_source(
    package: str, meta: dict[str, Any], version: str | None
) -> tuple[SourceFiles | None, dict[str, Any]]:
    """Open the source files of a package version and collect the provenance.

    Args:
        package: Registry key of the package.
        meta: Registry metadata of the package.
        version: Requested version, or None for the installed version.

    Returns:
        The source files and the provenance fields for every result. If no
        source could be opened, the files are None and the dict is the final result.
    """
    environment = environment_fields(meta.get("name", package))
    route = choose_route(package, meta, version, environment)
    if route.failure_result:
        return None, {**route.failure_result, "package": package, **environment}

    source_files = route.source_files
    provenance = {"source": source_files.source, "version": source_files.version, **environment}
    if route.pypi_error:
        provenance["pypi_error"] = route.pypi_error
    if source_files.warning:
        provenance["warning"] = source_files.warning
    return source_files, provenance


def _display_path(file: Path, root: Path | None) -> str:
    """Format a file path for a result.

    Args:
        file: Absolute path of the file.
        root: Folder the path should be shown relative to, or None.

    Returns:
        A relative POSIX path if a root is given and the file is inside it, else
        the absolute path.
    """
    if root is None or not file.is_relative_to(root):
        return str(file)
    return file.relative_to(root).as_posix()


def _definition_fields(
    definition: Definition, file: str, detail: str, source_files: SourceFiles
) -> dict[str, Any]:
    """Turn one definition into result fields.

    Args:
        definition: The definition that was found.
        file: Path of its file as shown to the user.
        detail: "full" to include the code, "signature" to leave it out.
        source_files: The files the definition was found in.

    Returns:
        Dict with qualified_name, kind, file, line, signature, docstring and,
        depending on detail, kind and source: code, methods and html_url.
    """
    fields = {
        "qualified_name": definition.qualified_name,
        "kind": definition.kind,
        "file": file,
        "line": definition.line,
        "signature": definition.signature,
        "docstring": definition.docstring,
    }
    if source_files.web_url:
        fields["html_url"] = f"{source_files.web_url}/{file}#L{definition.line}"
    if definition.kind == "class":
        fields["methods"] = definition.methods
    if detail == "full":
        fields["code"] = definition.code
    return fields


def format_matches(
    name: str,
    matches: list[tuple[Path, Definition]],
    detail: str,
    source_files: SourceFiles,
    provenance: dict[str, Any],
) -> dict[str, Any]:
    """Build the result for a definition lookup.

    One match is returned in full. Several matches are returned as a list of
    signatures and docstrings so the caller can pick one by its dotted name.

    Args:
        name: The name that was looked up.
        matches: Pairs of (file, definition).
        detail: "full" or "signature".
        source_files: The files that were searched.
        provenance: Fields added to every result (source, version, ...).

    Returns:
        The result dict; if nothing matched, status "not_found" with a message.
    """
    if not matches:
        message = (
            f"'{name}' was not found as a function, method or class in version "
            f"{source_files.version} ({source_files.source}). It may be named "
            f"differently in this version; try search_source to locate it."
        )
        return {"status": "not_found", "message": message, **provenance}
    shown = [(_display_path(file, source_files.root), d) for file, d in matches]
    if len(shown) == 1:
        file, definition = shown[0]
        fields = _definition_fields(definition, file, detail, source_files)
        return {"function": name, **fields, **provenance}
    message = (
        f"{len(shown)} definitions match '{name}'. Bodies are left out. Call "
        f"get_function_source again with a more specific dotted name "
        f"(Class.method or module.Class.method) to get one of them in full."
    )
    return {
        "function": name,
        "match_count": len(shown),
        "matches": [
            _definition_fields(definition, file, "signature", source_files)
            for file, definition in shown[:MAX_MATCHES]
        ],
        "message": message,
        **provenance,
    }


def get_function_source(
    package: str, meta: dict[str, Any], name: str, version: str | None, detail: str
) -> dict[str, Any]:
    """Find a function, method or class of a package and return it with provenance.

    Args:
        package: Registry key of the package.
        meta: Registry metadata of the package.
        name: Plain or dotted name of the function, method or class.
        version: Requested version, or None for the installed version.
        detail: "full" for signature, docstring and code; "signature" without code.

    Returns:
        The result dict (see format_matches), or a not_installed / error dict.
    """
    if detail not in DETAIL_LEVELS:
        return {"error": f"Unknown detail '{detail}'. Use one of {list(DETAIL_LEVELS)}."}
    source_files, provenance = _open_source(package, meta, version)
    if source_files is None:
        return provenance

    matches, inherited_note = find_with_inheritance(source_files.paths, name)
    result = format_matches(name, matches, detail, source_files, provenance)
    if inherited_note:
        result["note"] = inherited_note
    return result


def _search_root(paths: list[Path]) -> Path | None:
    """Find the folder that installed file paths are shown relative to.

    This is the site-packages folder if the files live in one; otherwise the folder
    all files share.

    Args:
        paths: Absolute paths of the installed Python files.

    Returns:
        The folder, or None if there is no common folder (e.g. several drives).
    """
    names = set(setting("paths", "site_packages_folders"))
    for index, part in enumerate(paths[0].parts):
        if part in names:
            return Path(*paths[0].parts[: index + 1])
    try:
        return Path(os.path.commonpath([str(path.parent) for path in paths]))
    except ValueError:
        return None


def search_source(
    package: str, meta: dict[str, Any], query: str, version: str | None
) -> dict[str, Any]:
    """Search the source code of a package version for a text string.

    Provenance is stated once for the whole result. Files of the installed package
    are shown relative to `root`, which is stated once as well.

    Args:
        package: Registry key of the package.
        meta: Registry metadata of the package.
        query: Text to search for (case-insensitive).
        version: Requested version, or None for the installed version.

    Returns:
        Dict with the provenance (source, version, installed_version, python_executable,
        ...) and matches (file, line, text); a message if there are no matches. If no
        source could be opened: a dict with status or error instead.
    """
    source_files, provenance = _open_source(package, meta, version)
    if source_files is None:
        return provenance

    root = source_files.root or _search_root(source_files.paths)
    if source_files.source == "local" and root is not None:
        provenance["root"] = str(root)
    hits = search_files(source_files.paths, query)
    matches = [{**hit, "file": _display_path(hit["file"], root)} for hit in hits]
    result = {**provenance, "matches": matches}
    if not matches:
        result["message"] = f"No results for '{query}'."
    return result
