"""
scripts/fetch_docs.py
---------------------
Fetches online documentation for registered packages and saves each section
into the shared local cache under .cache/docs/{package}/{section_id}.md.

Usage:
    # Fetch all packages
    python scripts/fetch_docs.py

    # Fetch a specific package
    python scripts/fetch_docs.py --package premise

    # Fetch a specific section of a package
    python scripts/fetch_docs.py --package premise --section faq

    # Force re-fetch even if the cached file already exists
    python scripts/fetch_docs.py --package premise --force
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

# Make sure root is on the path so `packages` can be imported
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from core.cache import refresh_page  # noqa: E402
from core.registry import PackageRegistry  # noqa: E402


# ---------------------------------------------------------------------------
# Main logic
# ---------------------------------------------------------------------------

def fetch_package(
    registry: PackageRegistry,
    package: str,
    section_filter: str | None = None,
    force: bool = False,
) -> None:
    meta = registry.get_metadata(package)
    if meta is None:
        print(f"[ERROR] Unknown package '{package}'. Available: {registry.list_packages()}")
        return

    content_dir = registry.get_content_dir(package)
    meta = registry.get_metadata(package)
    assert meta is not None

    sections = meta.get("sections", [])
    if section_filter:
        sections = [s for s in sections if s["id"] == section_filter]
        if not sections:
            print(f"[ERROR] Section '{section_filter}' not found in '{package}'.")
            print(f"  Available sections: {[s['id'] for s in meta.get('sections', [])]}")
            return

    print(f"\n=== Fetching docs for '{package}' ({len(sections)} section(s)) ===")

    for sec in sections:
        out_path = Path(ROOT / ".cache" / "docs" / package / f"{sec['id']}.md")
        if out_path.exists() and not force:
            print(f"  [skip] {sec['id']} (already cached — use --force to re-fetch)")
            continue

        print(f"  [fetch] {sec['id']}  →  {sec['url']}")
        try:
            markdown = refresh_page(package, sec["id"], sec["url"])
            print(f"  [ok]   saved {out_path.relative_to(ROOT)} ({len(markdown):,} chars)")
        except Exception as exc:  # noqa: BLE001
            print(f"  [FAIL] {sec['id']}: {exc}")

        # Be polite to the docs server
        time.sleep(0.5)


def main() -> None:
    parser = argparse.ArgumentParser(description="Fetch and cache docs for registered packages.")
    parser.add_argument(
        "--package",
        metavar="NAME",
        help="Package to fetch (default: all registered packages).",
    )
    parser.add_argument(
        "--section",
        metavar="ID",
        help="Only fetch this section (requires --package).",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Re-fetch even if the Markdown file already exists.",
    )
    args = parser.parse_args()

    if args.section and not args.package:
        parser.error("--section requires --package")

    registry = PackageRegistry()

    if args.package:
        fetch_package(registry, args.package, args.section, args.force)
    else:
        for pkg in registry.list_packages():
            fetch_package(registry, pkg, force=args.force)

    print("\nDone.")


if __name__ == "__main__":
    main()
