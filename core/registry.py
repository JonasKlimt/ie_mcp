"""
PackageRegistry: auto-discovers package modules under packages/.

Each package module must contain a metadata.py file with a METADATA dict.
The metadata is intentionally tiny: just enough to locate the package repo,
docs root, and section URLs.
"""

from __future__ import annotations

import importlib
import re
from pathlib import Path


class PackageRegistry:
    def __init__(self) -> None:
        self._packages: dict[str, dict] = {}
        self._load_all()

    # ------------------------------------------------------------------
    # Discovery
    # ------------------------------------------------------------------

    def _load_all(self) -> None:
        packages_dir = Path(__file__).parent.parent / "packages"
        if not packages_dir.exists():
            return

        for pkg_dir in sorted(packages_dir.iterdir()):
            if not pkg_dir.is_dir():
                continue
            if not (pkg_dir / "metadata.py").exists():
                continue
            try:
                module = importlib.import_module(f"packages.{pkg_dir.name}.metadata")
                self._packages[pkg_dir.name] = {"metadata": module.METADATA}
            except Exception as exc:  # noqa: BLE001
                print(f"[ie-mcp] Warning: could not load package '{pkg_dir.name}': {exc}")

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def list_packages(self) -> list[str]:
        return list(self._packages.keys())

    def get_metadata(self, package: str) -> dict | None:
        entry = self._packages.get(package)
        return entry["metadata"] if entry else None

    def get_sections(self, package: str) -> list[str]:
        meta = self.get_metadata(package)
        if not meta:
            return []
        return [section["id"] for section in meta.get("sections", [])]

    def get_section_info(self, package: str, section: str) -> dict | None:
        meta = self.get_metadata(package)
        if not meta:
            return None
        for section_info in meta.get("sections", []):
            if section_info["id"] == section:
                return section_info
        return None

    # ------------------------------------------------------------------
    # Version-aware URL helpers
    # ------------------------------------------------------------------

    _VERSION_PATTERN = re.compile(r"/en/[^/]+/")

    @staticmethod
    def _substitute_version(url: str, version: str) -> str:
        """Replace the version segment in a ReadTheDocs URL.

        Handles URLs like: https://pkg.readthedocs.io/en/latest/page.html
        Leaves non-versioned URLs (e.g. wurst's index.html) unchanged.
        """
        return re.sub(r"(/en/)[^/]+(/)", rf"\g<1>{version}\2", url)

    @classmethod
    def _url_supports_versioning(cls, url: str) -> bool:
        """Return True if the URL contains a ReadTheDocs version segment."""
        return bool(cls._VERSION_PATTERN.search(url))

    def supports_versioning(self, package: str) -> bool:
        """Return True if at least one section URL in this package supports versioning."""
        meta = self.get_metadata(package)
        if not meta:
            return False
        return any(
            self._url_supports_versioning(s["url"])
            for s in meta.get("sections", [])
        )

    def get_section_url(self, package: str, section: str, version: str = "latest") -> str | None:
        section_info = self.get_section_info(package, section)
        if not section_info:
            return None
        return self._substitute_version(section_info["url"], version)

    def get_all_section_urls(self, package: str, version: str = "latest") -> list[tuple[str, str]]:
        meta = self.get_metadata(package)
        if not meta:
            return []
        return [
            (section["id"], self._substitute_version(section["url"], version))
            for section in meta.get("sections", [])
        ]
