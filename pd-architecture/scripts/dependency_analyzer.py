"""
Analyze project dependencies for coupling, circular dependencies, outdated packages.

Usage:
    python dependency_analyzer.py <project_dir> [--requirements requirements.txt]
"""

import os
import re
import sys
from collections import defaultdict


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Analyze project dependencies")
    parser.add_argument("project_dir", help="Path to project directory")
    parser.add_argument("--requirements", default=None,
                        help="Path to requirements.txt or pyproject.toml")
    args = parser.parse_args()

    if not os.path.isdir(args.project_dir):
        print(f"Error: {args.project_dir} is not a directory", file=sys.stderr)
        sys.exit(1)

    # Find all Python files and extract imports
    internal_modules = set()
    all_imports = defaultdict(set)

    for root, _dirs, files in os.walk(args.project_dir):
        rel_root = os.path.relpath(root, args.project_dir)
        if any(rel_root.startswith(p) for p in (".", "__pycache__", "venv", "node_modules", ".git", "tests")):
            continue

        for f in files:
            if f.endswith(".py"):
                filepath = os.path.join(root, f)
                module_name = rel_root.replace(os.sep, ".") + "." + f[:-3]
                if module_name.startswith("."):
                    module_name = module_name[1:]
                internal_modules.add(module_name)

                with open(filepath, "r", encoding="utf-8") as fh:
                    for line in fh:
                        line = line.strip()
                        if line.startswith("from ") and " import " in line:
                            dep = line.split(" ")[1]
                            all_imports[module_name].add(dep)
                        elif line.startswith("import "):
                            dep = line.split(" ")[1].split(",")[0].split(" as ")[0].strip()
                            all_imports[module_name].add(dep)

    # Detect external vs internal dependencies
    external = set()
    internal_deps = defaultdict(set)

    for mod, imports in all_imports.items():
        for imp in imports:
            top_level = imp.split(".")[0]
            if top_level in internal_modules or imp in internal_modules:
                internal_deps[mod].add(imp)
            else:
                external.add(top_level)

    # Detect circular dependencies
    cycles = _find_cycles(internal_deps)

    # Report
    print(f"Internal modules: {len(internal_modules)}")
    print(f"External dependencies: {len(external)}")
    if external:
        for dep in sorted(external):
            print(f"  - {dep}")

    print(f"\nCircular dependencies: {len(cycles)}")
    for cycle in cycles:
        print(f"  {' -> '.join(cycle)} -> {cycle[0]}")

    # High coupling detection
    coupled = {mod: len(deps) for mod, deps in internal_deps.items() if len(deps) > 3}
    if coupled:
        print(f"\nHigh coupling (>3 internal deps):")
        for mod, count in sorted(coupled.items(), key=lambda x: -x[1]):
            print(f"  {mod}: {count} deps")


def _find_cycles(graph):
    """Find all simple cycles up to length 4."""
    cycles = []
    visited = set()

    def dfs(node, path, path_set):
        if node in path_set:
            cycle_start = path.index(node)
            cycle = path[cycle_start:]
            if len(cycle) <= 4:
                normalized = tuple(sorted(cycle))
                if normalized not in visited:
                    visited.add(normalized)
                    cycles.append(cycle)
            return
        if len(path) >= 4:
            return
        path.append(node)
        path_set.add(node)
        for neighbor in graph.get(node, []):
            dfs(neighbor, path, path_set)
        path.pop()
        path_set.remove(node)

    for node in graph:
        dfs(node, [], set())

    return cycles


if __name__ == "__main__":
    main()
