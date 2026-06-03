"""
Generate architecture diagrams (Mermaid, PlantUML, ASCII) from project structure.

Usage:
    python architecture_diagram_generator.py <project_dir> [--format mermaid|plantuml|ascii]
"""

import argparse
import os
import sys


def main():
    parser = argparse.ArgumentParser(description="Generate architecture diagrams from project structure")
    parser.add_argument("project_dir", help="Path to project directory to analyze")
    parser.add_argument("--format", choices=["mermaid", "plantuml", "ascii"], default="mermaid",
                        help="Output format (default: mermaid)")
    args = parser.parse_args()

    if not os.path.isdir(args.project_dir):
        print(f"Error: {args.project_dir} is not a directory", file=sys.stderr)
        sys.exit(1)

    # Collect Python files and their import statements
    modules = []
    dependencies = []

    for root, _dirs, files in os.walk(args.project_dir):
        # Skip common non-project directories
        rel_root = os.path.relpath(root, args.project_dir)
        if rel_root.startswith((".", "__pycache__", "venv", "node_modules", ".git")):
            continue

        for f in files:
            if f.endswith(".py"):
                filepath = os.path.join(root, f)
                module_name = rel_root.replace(os.sep, ".") + "." + f[:-3]
                if module_name.startswith("."):
                    module_name = module_name[1:]
                modules.append(module_name)

                with open(filepath, "r", encoding="utf-8") as fh:
                    for line in fh:
                        line = line.strip()
                        if line.startswith("from ") and " import " in line:
                            dep = line.split(" ")[1].split(" import")[0]
                            dependencies.append((module_name, dep))
                        elif line.startswith("import "):
                            dep = line.split(" ")[1].split(",")[0].split(" as ")[0].strip()
                            dependencies.append((module_name, dep))

    # Deduplicate
    modules = sorted(set(modules))
    dependencies = sorted(set(dependencies))

    if args.format == "mermaid":
        _render_mermaid(modules, dependencies)
    elif args.format == "plantuml":
        _render_plantuml(modules, dependencies)
    else:
        _render_ascii(modules, dependencies)


def _render_mermaid(modules, dependencies):
    print("```mermaid")
    print("graph TD")
    for mod in modules:
        safe = mod.replace(".", "_")
        print(f"    {safe}[{mod}]")
    for src, dst in dependencies:
        if dst in modules:
            src_safe = src.replace(".", "_")
            dst_safe = dst.replace(".", "_")
            print(f"    {src_safe} --> {dst_safe}")
    print("```")


def _render_plantuml(modules, dependencies):
    print("@startuml")
    for mod in modules:
        print(f"component {mod.replace('.', '_')} as \"{mod}\"")
    for src, dst in dependencies:
        if dst in modules:
            print(f"{src.replace('.', '_')} --> {dst.replace('.', '_')}")
    print("@enduml")


def _render_ascii(modules, dependencies):
    print("Architecture Dependencies (ASCII)")
    print("=" * 50)
    for mod in modules:
        deps = [dst for src, dst in dependencies if src == mod and dst in modules]
        if deps:
            print(f"{mod}")
            for dep in deps:
                print(f"  -> {dep}")
        else:
            print(f"{mod} (leaf)")
    print()


if __name__ == "__main__":
    main()
