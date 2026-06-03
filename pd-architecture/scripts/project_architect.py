"""
Analyze project structure, detect architectural patterns, code smells.

Usage:
    python project_architect.py <project_dir> [--depth N]
"""

import os
import re
import sys
from collections import Counter, defaultdict


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Analyze project architecture")
    parser.add_argument("project_dir", help="Path to project directory")
    parser.add_argument("--depth", type=int, default=3,
                        help="Max directory depth to analyze (default: 3)")
    args = parser.parse_args()

    if not os.path.isdir(args.project_dir):
        print(f"Error: {args.project_dir} is not a directory", file=sys.stderr)
        sys.exit(1)

    files_by_type = Counter()
    files_by_dir = defaultdict(list)
    smells = []

    for root, dirs, files in os.walk(args.project_dir):
        # Skip hidden/vendor directories
        dirs[:] = [d for d in dirs if not d.startswith((".", "__pycache__"))
                   and d not in ("venv", "node_modules", ".git", "dist", "build")]

        rel_root = os.path.relpath(root, args.project_dir)
        depth = rel_root.count(os.sep) + 1
        if depth > args.depth and rel_root != ".":
            dirs.clear()
            continue

        for f in files:
            filepath = os.path.join(root, f)
            ext = os.path.splitext(f)[1]
            files_by_type[ext] += 1
            files_by_dir[rel_root].append(f)

            # Detect code smells
            if ext == ".py":
                _check_python_file(filepath, rel_root, smells)

    # Report
    _print_report(files_by_type, files_by_dir, smells)


def _check_python_file(filepath, rel_dir, smells):
    """Check a Python file for common architectural issues."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except (UnicodeDecodeError, PermissionError):
        return

    filename = os.path.basename(filepath)

    for i, line in enumerate(lines, 1):
        stripped = line.strip()

        # God class detection
        if stripped.startswith("class ") and len(lines) > 300:
            smells.append(f"HIGH: {rel_dir}/{filename} - Class file >300 lines ({len(lines)} lines)")

        # Long function detection (heuristic: function with >50 lines before next def/class)
        if stripped.startswith("def ") or stripped.startswith("async def "):
            func_start = i
            func_lines = 0
            for j in range(i, min(i + 100, len(lines))):
                next_line = lines[j].strip()
                if next_line.startswith("def ") or next_line.startswith("class "):
                    func_lines = j - i
                    break
            if func_lines > 50:
                func_name = stripped.split("(")[0].replace("def ", "").replace("async def ", "")
                smells.append(f"MEDIUM: {rel_dir}/{filename}:{func_start} - Function '{func_name}' >50 lines ({func_lines} lines)")

        # Naked except
        if re.match(r"^\s*except\s*:", stripped):
            smells.append(f"MEDIUM: {rel_dir}/{filename}:{i} - Bare except clause")

        # Wildcard imports
        if stripped.startswith("from ") and stripped.endswith(" import *"):
            module = stripped.split(" ")[1]
            smells.append(f"LOW: {rel_dir}/{filename}:{i} - Wildcard import 'from {module} import *'")

        # print statements in non-test code
        if stripped.startswith("print(") and "test" not in rel_dir.lower() and "tests" not in rel_dir.lower():
            smells.append(f"LOW: {rel_dir}/{filename}:{i} - print() statement in production code")


def _print_report(files_by_type, files_by_dir, smells):
    print("=" * 60)
    print("PROJECT ARCHITECTURE ANALYSIS")
    print("=" * 60)

    print(f"\nFile types ({sum(files_by_type.values())} total):")
    for ext, count in files_by_type.most_common(15):
        label = ext if ext else "(no extension)"
        print(f"  {label}: {count}")

    print(f"\nTop directories by file count:")
    dir_counts = {d: len(fs) for d, fs in files_by_dir.items()}
    for d, count in sorted(dir_counts.items(), key=lambda x: -x[1])[:10]:
        print(f"  {d or '.'}: {count} files")

    print(f"\nArchitecture issues ({len(smells)}):")
    if not smells:
        print("  None detected")
    else:
        severity_order = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
        for smell in sorted(smells, key=lambda s: severity_order.get(s.split(":")[0], 3)):
            print(f"  {smell}")

    # Summary
    high = sum(1 for s in smells if s.startswith("HIGH"))
    medium = sum(1 for s in smells if s.startswith("MEDIUM"))
    low = sum(1 for s in smells if s.startswith("LOW"))
    print(f"\nSummary: {high} HIGH, {medium} MEDIUM, {low} LOW")


if __name__ == "__main__":
    main()
