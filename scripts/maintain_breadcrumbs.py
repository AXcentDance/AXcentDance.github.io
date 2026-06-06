#!/usr/bin/env python3
"""Validate and narrowly maintain AXcent breadcrumb JSON-LD.

V1 is intentionally small: validate existing static HTML breadcrumbs and fix
localized German blog breadcrumb URLs without regenerating full schema blocks.
"""

from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Iterable

from breadcrumb_validation import (
    BASE_URL,
    BreadcrumbValidationError,
    breadcrumb_url,
    find_breadcrumb,
    find_breadcrumb_script,
    validate_breadcrumb_content,
)

SUPPORTED_LOCALES = {"de"}
SUPPORTED_SECTIONS = {"blog-posts"}
TODAY = date.today().isoformat()


class BreadcrumbError(Exception):
    """Raised for actionable breadcrumb maintenance failures."""


@dataclass(frozen=True)
class FieldChange:
    label: str
    before: str
    after: str


@dataclass
class FilePlan:
    path: Path
    original: str
    updated: str
    changes: list[FieldChange]

    @property
    def has_changes(self) -> bool:
        return self.original != self.updated


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def rel_path(path: Path, root: Path) -> str:
    return path.resolve().relative_to(root.resolve()).as_posix()


def run_git(root: Path, args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=root,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def git_dirty_paths(root: Path) -> set[str]:
    result = run_git(root, ["status", "--porcelain"])
    if result.returncode != 0:
        raise BreadcrumbError(f"Unable to inspect git status: {result.stderr.strip()}")

    paths: set[str] = set()
    for line in result.stdout.splitlines():
        if not line:
            continue
        # Porcelain v1 path begins after the two status columns and a space.
        path_text = line[3:]
        if " -> " in path_text:
            path_text = path_text.split(" -> ", 1)[1]
        paths.add(path_text)
    return paths


def warn_dirty_tree(root: Path) -> set[str]:
    dirty = git_dirty_paths(root)
    if dirty:
        print(
            f"WARNING: git working tree is dirty ({len(dirty)} path(s)). "
            "Unrelated dirty files will not block execution.",
            file=sys.stderr,
        )
    return dirty


def refuse_dirty_targets(root: Path, plans: Iterable[FilePlan], force: bool) -> None:
    target_paths = {rel_path(plan.path, root) for plan in plans if plan.has_changes}
    if not target_paths:
        return

    dirty_targets = sorted(target_paths & git_dirty_paths(root))
    if not dirty_targets:
        return

    if force:
        print(
            "WARNING: --force allows writing dirty target file(s): "
            + ", ".join(dirty_targets),
            file=sys.stderr,
        )
        return

    raise BreadcrumbError(
        "Refusing to write target file(s) with existing uncommitted changes: "
        + ", ".join(dirty_targets)
        + ". Review those changes or rerun with --force."
    )


def html_files(root: Path) -> list[Path]:
    ignored_dirs = {".git", "node_modules"}
    files: list[Path] = []
    for current_root, dirs, names in os.walk(root):
        dirs[:] = [name for name in dirs if name not in ignored_dirs]
        for name in names:
            if name.endswith(".html"):
                files.append(Path(current_root) / name)
    return sorted(files)


def target_files(root: Path, locale: str, section: str, path_arg: str | None) -> list[Path]:
    if locale not in SUPPORTED_LOCALES:
        raise BreadcrumbError(f"Unsupported locale '{locale}'. Supported: de")
    if section not in SUPPORTED_SECTIONS:
        raise BreadcrumbError(f"Unsupported section '{section}'. Supported: blog-posts")

    if path_arg:
        path = (root / path_arg).resolve()
        if not path.exists():
            raise BreadcrumbError(f"Target path does not exist: {path_arg}")
        if not path.is_relative_to(root.resolve()):
            raise BreadcrumbError(f"Target path is outside repository: {path_arg}")
        if path.is_file():
            return [path]
        return sorted(path.glob("*.html"))

    return sorted((root / locale / section).glob("*.html"))


def validate_repo(root: Path) -> int:
    issues: list[str] = []
    total = 0
    skipped = {"index.html", "404.html", "de/index.html", "de/404.html"}

    for path in html_files(root):
        rel = rel_path(path, root)
        if rel in skipped:
            continue
        total += 1
        issues.extend(validate_breadcrumb_content(path.read_text(encoding="utf-8"), rel))

    print(f"Breadcrumb maintenance validation scanned {total} HTML files.")
    if issues:
        print("Issues:")
        for issue in issues:
            print(f"  - {issue}")
        return 1

    print("No breadcrumb schema issues found.")
    return 0


def replace_json_string_field(content: str, before: str, after: str) -> tuple[str, bool]:
    old = f'"{before}"'
    new = f'"{after}"'
    if old not in content:
        return content, False
    return content.replace(old, new, 1), True


def update_first_date_modified(content: str, modified_date: str) -> tuple[str, bool, str | None]:
    pattern = re.compile(r'("dateModified"\s*:\s*")([^"]+)(")')
    match = pattern.search(content)
    if not match:
        return content, False, None
    before = match.group(2)
    if before == modified_date:
        return content, False, before
    return content[: match.start(2)] + modified_date + content[match.end(2) :], True, before


def build_fix_plan(root: Path, path: Path) -> FilePlan:
    original = path.read_text(encoding="utf-8")
    rel = rel_path(path, root)
    changes: list[FieldChange] = []

    try:
        script = find_breadcrumb_script(original, rel)
        breadcrumb = find_breadcrumb(script.objects)
    except BreadcrumbValidationError as exc:
        raise BreadcrumbError(f"Cannot fix {rel}: {exc}") from exc

    script_body = script.body
    elements = breadcrumb.get("itemListElement")
    if not isinstance(elements, list):
        raise BreadcrumbError(f"Cannot fix {rel}: BreadcrumbList itemListElement is not a list")

    for element in elements:
        if not isinstance(element, dict):
            continue
        position = element.get("position")
        url = breadcrumb_url(element)
        if rel.startswith("de/blog-posts/") and position == 2 and url == f"{BASE_URL}/blog":
            after = f"{BASE_URL}/de/blog"
            script_body, did_replace = replace_json_string_field(script_body, url, after)
            if not did_replace:
                raise BreadcrumbError(f"Cannot patch {rel}: parent breadcrumb string not found")
            changes.append(FieldChange("breadcrumb parent URL", url, after))
        if position == len(elements) and script.canonical_url and url != script.canonical_url:
            script_body, did_replace = replace_json_string_field(script_body, url or "", script.canonical_url)
            if not did_replace:
                raise BreadcrumbError(f"Cannot patch {rel}: final breadcrumb string not found")
            changes.append(FieldChange("final breadcrumb URL", url or "", script.canonical_url))

    if changes and "blog-posts/" in rel:
        updated_after_date, date_changed, before_date = update_first_date_modified(script_body, TODAY)
        if date_changed and before_date:
            script_body = updated_after_date
            changes.append(FieldChange("dateModified", before_date, TODAY))

    updated = original[: script.start] + script_body + original[script.end :]
    return FilePlan(path=path, original=original, updated=updated, changes=changes)


def validate_plans(root: Path, plans: list[FilePlan]) -> None:
    errors: list[str] = []
    for plan in plans:
        rel = rel_path(plan.path, root)
        errors.extend(validate_breadcrumb_content(plan.updated, rel))
    if errors:
        raise BreadcrumbError("Validation failed after planned changes:\n  - " + "\n  - ".join(errors))


def print_plan(root: Path, plans: list[FilePlan]) -> None:
    changed = [plan for plan in plans if plan.has_changes]
    if not changed:
        print("No breadcrumb changes needed.")
        return

    print(f"Planned breadcrumb changes for {len(changed)} file(s):")
    for plan in changed:
        print(f"\n{rel_path(plan.path, root)}")
        for change in plan.changes:
            print(f"  - {change.label}: {change.before} -> {change.after}")


def atomic_write(path: Path, content: str) -> None:
    fd, tmp_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=str(path.parent), text=True)
    tmp_path = Path(tmp_name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(content)
        os.replace(tmp_path, path)
    finally:
        if tmp_path.exists():
            tmp_path.unlink()


def write_plans(plans: list[FilePlan]) -> None:
    for plan in plans:
        if plan.has_changes:
            atomic_write(plan.path, plan.updated)


def run_fix(args: argparse.Namespace) -> int:
    root = repo_root()
    warn_dirty_tree(root)
    paths = target_files(root, args.locale, args.section, args.path)
    plans = [build_fix_plan(root, path) for path in paths]
    validate_plans(root, plans)
    print_plan(root, plans)

    if args.dry_run:
        return 0

    refuse_dirty_targets(root, plans, args.force)
    write_plans(plans)
    changed_count = sum(1 for plan in plans if plan.has_changes)
    print(f"Wrote breadcrumb changes to {changed_count} file(s).")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("validate", help="Validate breadcrumb schema across all HTML files.")

    fix_parser = subparsers.add_parser("fix", help="Plan or apply narrow breadcrumb schema fixes.")
    fix_parser.add_argument("--locale", required=True, help="Locale to fix. V1 supports: de")
    fix_parser.add_argument("--section", required=True, help="Section to fix. V1 supports: blog-posts")
    fix_parser.add_argument("--path", help="Optional file or directory path to limit the fix.")
    mode_group = fix_parser.add_mutually_exclusive_group()
    mode_group.add_argument("--dry-run", action="store_true", help="Show planned changes without writing.")
    mode_group.add_argument("--write", action="store_true", help="Write planned changes atomically.")
    fix_parser.add_argument("--force", action="store_true", help="Allow writes to dirty target files.")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        if args.command == "validate":
            return validate_repo(repo_root())
        if args.command == "fix":
            if not args.dry_run and not args.write:
                parser.error("fix requires either --dry-run or --write")
            return run_fix(args)
    except BreadcrumbError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    parser.error(f"Unknown command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
