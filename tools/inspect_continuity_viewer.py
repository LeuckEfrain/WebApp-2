from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent

print()
print("=" * 70)
print("WEBAPP-2 CONTINUITY VIEWER DIAGNOSTIC")
print("=" * 70)
print()
print(f"Project root: {PROJECT_ROOT}")
print()


# ---------------------------------------------------------------------
# 1. Find every ContinuityViewer.jsx in the project.
# ---------------------------------------------------------------------

viewer_files = sorted(
    PROJECT_ROOT.rglob("ContinuityViewer.jsx")
)

print("CONTINUITYVIEWER.JSX FILES")
print("-" * 70)

if not viewer_files:
    print("NONE FOUND")
else:
    for path in viewer_files:
        print(path)
        print(f"  size: {path.stat().st_size} bytes")

print()


# ---------------------------------------------------------------------
# 2. Find every source file importing ContinuityViewer.
# ---------------------------------------------------------------------

print("FILES IMPORTING CONTINUITYVIEWER")
print("-" * 70)

imports_found = []

for path in PROJECT_ROOT.rglob("*"):
    if not path.is_file():
        continue

    if any(
        part in {
            "node_modules",
            ".git",
            "dist",
            "build",
        }
        for part in path.parts
    ):
        continue

    try:
        text = path.read_text(
            encoding="utf-8"
        )
    except (
        UnicodeDecodeError,
        PermissionError,
        OSError,
    ):
        continue

    if (
        "ContinuityViewer" in text
        or "continuity-viewer/ContinuityViewer" in text
        or "./ContinuityViewer" in text
    ):
        imports_found.append(path)

for path in imports_found:
    print(path)

if not imports_found:
    print("NONE FOUND")

print()


# ---------------------------------------------------------------------
# 3. Inspect each ContinuityViewer.jsx for the relevant state logic.
# ---------------------------------------------------------------------

print("RELEVANT CONTINUITY VIEWER CONTENT")
print("-" * 70)

for path in viewer_files:
    print()
    print(f"FILE: {path}")
    print()

    try:
        lines = path.read_text(
            encoding="utf-8"
        ).splitlines()
    except Exception as error:
        print(f"Unable to read: {error}")
        continue

    interesting = (
        "useState",
        "openSections",
        "setOpenSections",
        "continuitySections",
        "loadContinuitySections",
        "export default ContinuityViewer",
    )

    found = False

    for index, line in enumerate(lines, start=1):
        if any(token in line for token in interesting):
            found = True

            start = max(1, index - 2)
            end = min(len(lines), index + 3)

            print(
                f"--- lines {start}-{end} ---"
            )

            for line_number in range(start, end + 1):
                print(
                    f"{line_number:4}: "
                    f"{lines[line_number - 1]}"
                )

            print()

    if not found:
        print(
            "No expected ContinuityViewer state/import "
            "markers found."
        )


# ---------------------------------------------------------------------
# 4. Search for the exact marker from our previous modification.
# ---------------------------------------------------------------------

print()
print("PREVIOUS FIX MARKER")
print("-" * 70)

marker = "WEBAPP2_GOALS_OPEN_AFTER_LOAD"

marker_files = []

for path in PROJECT_ROOT.rglob("*"):
    if not path.is_file():
        continue

    if any(
        part in {
            "node_modules",
            ".git",
            "dist",
            "build",
        }
        for part in path.parts
    ):
        continue

    try:
        text = path.read_text(
            encoding="utf-8"
        )
    except (
        UnicodeDecodeError,
        PermissionError,
        OSError,
    ):
        continue

    if marker in text:
        marker_files.append(path)

if marker_files:
    for path in marker_files:
        print(path)
else:
    print(
        "The previous fix marker was not found anywhere "
        "outside excluded directories."
    )

print()
print("=" * 70)
print("DIAGNOSTIC COMPLETE")
print("=" * 70)
print()