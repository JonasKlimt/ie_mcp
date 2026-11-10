"""
PyPI helpers for reading the source of a specific released version.

Uses the PyPI JSON API to list versions and to locate release files. A release
is downloaded once, its Python files are unpacked into
.cache/pypi/{package}/{version}/, and later lookups reuse that folder.
"""

from __future__ import annotations

import hashlib
import io
import re
import shutil
import tarfile
import tempfile
import zipfile
from pathlib import Path, PurePosixPath
from typing import Any

import httpx

from .cache import cache_root

PYPI_API = "https://pypi.org/pypi"
PURE_WHEEL_SUFFIX = "-py3-none-any.whl"
REQUEST_TIMEOUT_SECONDS = 60.0
_VERSION_PATTERN = re.compile(r"[A-Za-z0-9]+([._+!-][A-Za-z0-9]+)*")


class VersionNotOnPyPI(LookupError):
    """The package or the requested version is not published on PyPI."""


def _get_json(url: str) -> dict[str, Any]:
    """Fetch a PyPI JSON document.

    Args:
        url: Full URL of the JSON API endpoint.

    Returns:
        The decoded JSON document.

    Raises:
        VersionNotOnPyPI: If PyPI answers 404.
        httpx.HTTPError: For any other network or HTTP failure.
    """
    response = httpx.get(url, follow_redirects=True, timeout=REQUEST_TIMEOUT_SECONDS)
    if response.status_code == 404:
        raise VersionNotOnPyPI(f"Not found on PyPI: {url}")
    response.raise_for_status()
    return response.json()


def list_versions(pypi_name: str) -> list[str]:
    """List the versions of a package published on PyPI, newest upload first.

    Args:
        pypi_name: Distribution name as published on PyPI.

    Returns:
        Version strings of all releases that have at least one file.

    Raises:
        VersionNotOnPyPI: If the package is not on PyPI.
        httpx.HTTPError: For any other network or HTTP failure.
    """
    releases = _get_json(f"{PYPI_API}/{pypi_name}/json")["releases"]
    uploaded = {
        version: max(file["upload_time_iso_8601"] for file in files)
        for version, files in releases.items()
        if files
    }
    return sorted(uploaded, key=uploaded.get, reverse=True)


def latest_version(pypi_name: str) -> str:
    """Return the newest version of a package according to PyPI.

    Args:
        pypi_name: Distribution name as published on PyPI.

    Returns:
        The version string PyPI reports as current.

    Raises:
        VersionNotOnPyPI: If the package is not on PyPI.
        httpx.HTTPError: For any other network or HTTP failure.
    """
    return _get_json(f"{PYPI_API}/{pypi_name}/json")["info"]["version"]


def choose_release_file(files: list[dict[str, Any]]) -> dict[str, Any] | None:
    """Pick the release file that is easiest to read source code from.

    Preference: pure-Python wheel, then source distribution, then any wheel.

    Args:
        files: The "urls" list of a PyPI release JSON document.

    Returns:
        The chosen file entry, or None if there is no wheel or .tar.gz/.zip sdist.
    """
    pure_wheels = [f for f in files if f["filename"].endswith(PURE_WHEEL_SUFFIX)]
    sdists = [f for f in files if f["filename"].endswith((".tar.gz", ".zip"))]
    wheels = [f for f in files if f["filename"].endswith(".whl")]
    candidates = pure_wheels + sdists + wheels
    return candidates[0] if candidates else None


def _safe_target(root: Path, member_name: str) -> Path | None:
    """Map an archive member to a path inside the extraction folder.

    Args:
        root: Extraction folder.
        member_name: Path of the member inside the archive.

    Returns:
        The target path, or None for non-Python files and unsafe paths
        (absolute paths or paths that leave the folder).
    """
    member = PurePosixPath(member_name.replace("\\", "/"))
    if member.suffix != ".py" or member.is_absolute() or ".." in member.parts:
        return None
    if any(":" in part for part in member.parts):  # Windows drive letters
        return None
    return root.joinpath(*member.parts)


def _extract_python_files(archive: bytes, filename: str, root: Path) -> None:
    """Unpack only the .py files of a wheel or sdist.

    Args:
        archive: Raw bytes of the downloaded file.
        filename: Name of the release file, used to tell zip from tar.
        root: Folder to extract into.
    """
    # Only .py members are read: releases can hold large data files.
    if filename.endswith(".tar.gz"):
        with tarfile.open(fileobj=io.BytesIO(archive), mode="r:gz") as tar:
            members = [m for m in tar.getmembers() if m.isfile() and _safe_target(root, m.name)]
            contents = [(m.name, tar.extractfile(m).read()) for m in members]
    else:
        with zipfile.ZipFile(io.BytesIO(archive)) as zipped:
            contents = [(n, zipped.read(n)) for n in zipped.namelist() if _safe_target(root, n)]

    for name, data in contents:
        target = _safe_target(root, name)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)


def release_cache_path(pypi_name: str, version: str) -> Path:
    """Return the cache folder for one unpacked release.

    Args:
        pypi_name: Distribution name as published on PyPI.
        version: Exact version string.

    Returns:
        Path of .cache/pypi/{package}/{version}/ (it may not exist yet).

    Raises:
        VersionNotOnPyPI: If the version is not a valid PyPI version string
            (e.g. a branch name or a path).
    """
    if not _VERSION_PATTERN.fullmatch(version):
        raise VersionNotOnPyPI(f"'{version}' is not a PyPI version.")
    return cache_root() / "pypi" / pypi_name / version


def fetch_release(pypi_name: str, version: str) -> Path:
    """Download one release from PyPI and unpack its Python files into the cache.

    An already unpacked release is reused without any network access.

    Args:
        pypi_name: Distribution name as published on PyPI.
        version: Exact version string, without a leading "v".

    Returns:
        Folder that contains the unpacked .py files.

    Raises:
        VersionNotOnPyPI: If the version is not on PyPI or has no usable file.
        ValueError: If the download does not match PyPI's sha256 checksum.
        httpx.HTTPError: For network or HTTP failures.
    """
    target = release_cache_path(pypi_name, version)
    if target.is_dir():
        return target

    release_file = choose_release_file(_get_json(f"{PYPI_API}/{pypi_name}/{version}/json")["urls"])
    if release_file is None:
        raise VersionNotOnPyPI(f"No wheel or sdist for {pypi_name} {version} on PyPI.")

    response = httpx.get(
        release_file["url"], follow_redirects=True, timeout=REQUEST_TIMEOUT_SECONDS
    )
    response.raise_for_status()
    if hashlib.sha256(response.content).hexdigest() != release_file["digests"]["sha256"]:
        raise ValueError(f"Checksum mismatch for {release_file['filename']}.")

    # Unpack next to the target, then rename: a crash leaves no half-filled cache.
    target.parent.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(dir=target.parent, prefix=f".{version}-"))
    try:
        _extract_python_files(response.content, release_file["filename"], staging)
        if not target.is_dir():  # another request may have finished first
            staging.rename(target)
    finally:
        shutil.rmtree(staging, ignore_errors=True)
    return target


def list_release_files(release_root: Path) -> list[Path]:
    """List the Python files of an unpacked release.

    Args:
        release_root: Folder returned by fetch_release().

    Returns:
        Sorted paths of all .py files in the folder.
    """
    return sorted(release_root.rglob("*.py"))
