#!/usr/bin/env python3
"""Plan the publishing order of the plugins in a directory.

Reads every ``<plugins_dir>/*/pyproject.toml``, builds the dependency graph between the local packages, drops the
packages whose current version already exists on PyPI, and groups the rest into dependency levels:

* dependency level 0 - packages that depend on no other unpublished local package,
* dependency level 1 - packages whose local dependencies are all in dependency level 0 (or already published),
* dependency level N - and so on, for dependency chains of any depth.

Packages within one dependency level are independent, so they can be published in parallel;
dependency levels must run sequentially.

Usage: plan_publish.py [plugins_dir] [--max-dependency-levels N]

Writes ``dependency_levels`` (JSON list of lists of directory names) and ``count`` to ``$GITHUB_OUTPUT`` when it is
set, and prints a human-readable summary (also to ``$GITHUB_STEP_SUMMARY``).
"""

import argparse
import json
import os
import re
import sys
import tomllib
import urllib.error
import urllib.request
from pathlib import Path


def normalize(name: str) -> str:
    """Normalize a distribution name per PEP 503."""
    return re.sub(r"[-_.]+", "-", name).lower()


def requirement_name(requirement: str) -> str:
    """Extract the distribution name from a PEP 508 requirement string."""
    return normalize(re.match(r"\s*([A-Za-z0-9][A-Za-z0-9._-]*)", requirement).group(1))


def read_package(path: Path) -> dict:
    """Read name, version and the set of declared dependency names from a pyproject.toml (PEP 621 or Poetry)."""
    data = tomllib.loads(path.read_text())
    project = data.get("project", {})
    poetry = data.get("tool", {}).get("poetry", {})

    name = project.get("name") or poetry["name"]
    version = project.get("version") or poetry["version"]

    deps: set[str] = set()
    for requirement in project.get("dependencies", []):
        deps.add(requirement_name(requirement))
    for requirements in project.get("optional-dependencies", {}).values():
        deps.update(requirement_name(r) for r in requirements)
    deps.update(normalize(n) for n in poetry.get("dependencies", {}))
    for group in poetry.get("group", {}).values():
        deps.update(normalize(n) for n in group.get("dependencies", {}))

    return {"dir": path.parent.name, "name": normalize(name), "version": version, "deps": deps}


def is_published(name: str, version: str) -> bool:
    """Return True if ``name==version`` already exists on PyPI."""
    url = f"https://pypi.org/pypi/{name}/{version}/json"
    try:
        with urllib.request.urlopen(url, timeout=30):
            return True
    except urllib.error.HTTPError as error:
        if error.code == 404:
            return False
        raise


def build_dependency_levels(packages: dict[str, dict]) -> list[list[str]]:
    """Group packages into dependency levels (Kahn's algorithm). Raises on dependency cycles."""
    remaining = set(packages)
    levels: list[list[str]] = []
    while remaining:
        level = sorted(n for n in remaining if not (packages[n]["deps"] & remaining))
        if not level:
            raise SystemExit(f"Dependency cycle between: {', '.join(sorted(remaining))}")
        levels.append(level)
        remaining -= set(level)
    return levels


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("plugins_dir", nargs="?", default="plugins")
    parser.add_argument(
        "--max-dependency-levels", type=int, default=6, help="Number of dependency-level jobs the workflow provides."
    )
    args = parser.parse_args()

    all_packages = [read_package(p) for p in sorted(Path(args.plugins_dir).glob("*/pyproject.toml"))]
    local_names = {p["name"] for p in all_packages}

    pending: dict[str, dict] = {}
    lines = ["| Package | Version | Status |", "|---|---|---|"]
    for package in all_packages:
        if is_published(package["name"], package["version"]):
            lines.append(f"| {package['name']} | {package['version']} | already published, skipped |")
        else:
            package["deps"] &= local_names  # only local packages affect ordering
            pending[package["name"]] = package

    # Dependencies that are already published impose no ordering constraint.
    for package in pending.values():
        package["deps"] &= set(pending)

    levels = build_dependency_levels(pending)
    if len(levels) > args.max_dependency_levels:
        raise SystemExit(
            f"Dependency depth {len(levels)} exceeds the {args.max_dependency_levels} dependency levels "
            "the workflow provides."
        )

    dir_levels = [[pending[n]["dir"] for n in level] for level in levels]
    for index, level in enumerate(levels):
        for name in level:
            lines.append(f"| {name} | {pending[name]['version']} | publish in dependency level {index} |")

    summary = "\n".join(lines)
    print(summary)
    if os.environ.get("GITHUB_STEP_SUMMARY"):
        with open(os.environ["GITHUB_STEP_SUMMARY"], "a") as f:
            f.write(summary + "\n")
    if os.environ.get("GITHUB_OUTPUT"):
        with open(os.environ["GITHUB_OUTPUT"], "a") as f:
            f.write(f"dependency_levels={json.dumps(dir_levels)}\n")
            f.write(f"count={len(pending)}\n")


if __name__ == "__main__":
    sys.exit(main())
