from pathlib import Path


def print_tree(path, prefix="", max_depth=5, depth=0):
    if depth > max_depth:
        return

    try:
        entries = sorted(
            path.iterdir(),
            key=lambda p: (p.is_file(), p.name.lower())
        )
    except OSError as exc:
        print(f"{prefix}[ERROR READING] {exc}")
        return

    for index, entry in enumerate(entries):
        last = index == len(entries) - 1
        branch = "└── " if last else "├── "
        print(f"{prefix}{branch}{entry.name}")

        if entry.is_dir():
            extension = "    " if last else "│   "
            print_tree(
                entry,
                prefix + extension,
                max_depth,
                depth + 1,
            )


def main():
    project_root = Path(__file__).resolve().parent.parent
    src = project_root / "frontend" / "src"

    print("WebApp-2 Architecture Inspection")
    print("================================")
    print()
    print(f"Project root:")
    print(f"  {project_root}")
    print()
    print(f"Source directory:")
    print(f"  {src}")
    print()

    if not src.exists():
        print("ERROR: frontend/src does not exist.")
        return

    print("CURRENT SOURCE TREE")
    print("-------------------")
    print()

    print_tree(src, max_depth=6)

    print()
    print("IMPORTANT FILE LOCATIONS")
    print("------------------------")

    targets = [
        "App.jsx",
        "main.jsx",
        "styles.css",
        "components",
        "core",
        "instance",
        "audio",
        "modules",
    ]

    for target in targets:
        path = src / target
        print(f"{target:15} {'EXISTS' if path.exists() else 'missing'}")

    print()
    print("Inspection complete.")
    print("No files were modified.")


if __name__ == "__main__":
    main()