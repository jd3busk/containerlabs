#!/usr/bin/env python3
"""Recursively replace a hostname in file contents and filenames (Python 3.8+).

Usage: python3 rename_hostname.py joker riddler [--root LAB] [--dry-run]
Matching is literal, case-insensitive, and includes substrings. Every match is
replaced with the exact spelling of NEW. Directories themselves are not renamed.
UTF-8 text (including SVG/JSON/YAML) is edited without changing line endings.
Binary/non-UTF-8 contents, symlinks, this script, .git, .venv, and __pycache__
are skipped. Binary filenames can still be renamed. No dependencies required.
"""

import argparse
import os
from pathlib import Path
import re
import sys
from dataclasses import dataclass


@dataclass
class Change:
    path: Path
    target: Path
    original: bytes
    updated: bytes
    content_count: int
    name_count: int


def validate_name(value, strict=False):
    if not 1 <= len(value) <= 63:
        raise ValueError("Hostname must contain 1–63 characters.")
    allowed = r"[A-Za-z0-9-]+" if strict else r"[A-Za-z0-9_-]+"
    if not re.fullmatch(allowed, value):
        raise ValueError("Use only ASCII letters, digits, and hyphens" +
                         ("." if strict else " or underscores."))
    if not re.match(r"[A-Za-z]", value):
        raise ValueError("Hostname must start with a letter.")
    if not re.search(r"[A-Za-z0-9]$", value):
        raise ValueError("Hostname must end with a letter or digit.")


def scan(root, pattern, new):
    changes = []
    skipped = []
    own_path = Path(__file__).resolve()
    for directory, dirs, files in os.walk(root, followlinks=False):
        dirs[:] = sorted(d for d in dirs if d not in
                         {".git", ".venv", "__pycache__"} and
                         not (Path(directory) / d).is_symlink())
        for name in sorted(files):
            path = Path(directory) / name
            if path.is_symlink() or not path.is_file() or path.resolve() == own_path:
                continue
            target_name, name_count = pattern.subn(new, name)
            target = path.with_name(target_name)
            original = path.read_bytes()
            updated = original
            content_count = 0
            try:
                if b"\0" in original:
                    raise UnicodeError()
                text = original.decode("utf-8")
                text, content_count = pattern.subn(new, text)
                updated = text.encode("utf-8")
            except UnicodeError:
                skipped.append(path)
            if content_count or name_count:
                changes.append(Change(path, target, original, updated,
                                      content_count, name_count))
    return changes, skipped


def check_collisions(changes):
    # Case-folded checks also protect users copying the lab to macOS/Windows.
    targets = set()
    for change in changes:
        if change.path == change.target:
            continue
        key = str(change.target).casefold()
        if key in targets:
            raise ValueError("Multiple files would become: " + str(change.target))
        targets.add(key)
        for sibling in change.target.parent.iterdir():
            if sibling != change.path and sibling.name.casefold() == change.target.name.casefold():
                raise ValueError("Rename would collide with: " + str(sibling))


def apply(changes):
    # Recheck after confirmation, before changing anything.
    check_collisions(changes)
    for change in changes:
        if change.path.is_symlink() or change.path.read_bytes() != change.original:
            raise ValueError("File changed since preview: " + str(change.path))
    written = []
    renamed = []
    try:
        for change in changes:
            if change.updated != change.original:
                written.append(change)  # Include a potentially partial write.
                change.path.write_bytes(change.updated)
        for change in changes:
            if change.path != change.target:
                change.path.rename(change.target)
                renamed.append(change)
    except (OSError, KeyboardInterrupt):
        errors = []
        for change in reversed(renamed):
            try:
                change.target.rename(change.path)
            except OSError as exc:
                errors.append(str(exc))
        for change in reversed(written):
            try:
                location = change.path if change.path.exists() else change.target
                location.write_bytes(change.original)
            except OSError as exc:
                errors.append(str(exc))
        if errors:
            print("Rollback incomplete: " + "; ".join(errors), file=sys.stderr)
        else:
            print("Changes rolled back.", file=sys.stderr)
        raise


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("old", help="Hostname to find")
    parser.add_argument("new", help="Replacement hostname")
    parser.add_argument("--root", type=Path, default=Path.cwd(),
                        help="Lab directory (default: current directory)")
    parser.add_argument("--dry-run", action="store_true", help="Preview only")
    parser.add_argument("--case-sensitive", action="store_true")
    parser.add_argument("--strict-cisco", action="store_true",
                        help="Reject underscores under documented Cisco naming rules")
    args = parser.parse_args()
    try:
        # OLD is a literal identifier, not a regex or path.
        if not re.fullmatch(r"[A-Za-z0-9_-]+", args.old):
            raise ValueError("Old hostname must contain only ASCII letters, digits, - or _.")
        validate_name(args.new, args.strict_cisco)
        if args.old == args.new:
            raise ValueError("Old and new hostnames are identical.")
        root = args.root.expanduser().resolve()
        if not root.is_dir():
            raise ValueError("Lab directory does not exist: " + str(root))
        flags = re.ASCII | (0 if args.case_sensitive else re.IGNORECASE)
        pattern = re.compile(re.escape(args.old), flags)
        changes, skipped = scan(root, pattern, args.new)
        check_collisions(changes)
        contents = sum(c.content_count for c in changes)
        names = sum(c.name_count for c in changes)
        print("Directory: " + str(root))
        for c in changes:
            label = str(c.path.relative_to(root))
            if c.path != c.target:
                label += " -> " + str(c.target.relative_to(root))
            print("  {}: {} content, {} filename occurrence(s)".format(
                label, c.content_count, c.name_count))
        print("Found {} occurrence(s): {} in contents, {} in filenames.".format(
            contents + names, contents, names))
        if skipped:
            print("Skipped binary/non-UTF-8 contents in {} file(s).".format(len(skipped)))
        if not changes or args.dry_run:
            return 0
        answer = input("Replace {!r} with {!r} in place? [y/N] ".format(args.old, args.new))
        if answer.strip().lower() not in {"y", "yes"}:
            print("Cancelled; no changes made.")
            return 0
        apply(changes)
        print("Done: {} file(s) edited, {} file(s) renamed.".format(
            sum(c.updated != c.original for c in changes),
            sum(c.path != c.target for c in changes)))
        return 0
    except (OSError, ValueError) as exc:
        print("Error: " + str(exc), file=sys.stderr)
        return 1
    except (EOFError, KeyboardInterrupt):
        print("\nCancelled.", file=sys.stderr)
        return 130


if __name__ == "__main__":
    sys.exit(main())
