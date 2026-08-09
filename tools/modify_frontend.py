from pathlib import Path
from datetime import datetime
import shutil
import sys


PROJECT_ROOT = Path(r"D:\Projects\WebApps\webapp_2")

TARGET = (
    PROJECT_ROOT
    / "frontend"
    / "src"
    / "instance"
    / "modules"
    / "continuity-viewer"
    / "continuityData.js"
)

BACKUP_DIR = PROJECT_ROOT / "tools" / "backups"


def fail(message):
    print(f"ERROR: {message}")
    sys.exit(1)


if not TARGET.exists():
    fail(f"Expected file does not exist:\n{TARGET}")


text = TARGET.read_text(encoding="utf-8")

normalize_marker = "function normalize(value) {"

occurrences = []
position = 0

while True:
    found = text.find(normalize_marker, position)

    if found == -1:
        break

    occurrences.append(found)
    position = found + len(normalize_marker)


if len(occurrences) != 2:
    fail(
        "Expected exactly two normalize() declarations after the previous "
        f"parser repair, but found {len(occurrences)}."
    )


# The first normalize() belongs to the original parser foundation.
# The second was accidentally introduced by the repair and must be removed.
second_start = occurrences[1]

next_function = text.find("\nfunction ", second_start + len(normalize_marker))

if next_function == -1:
    fail(
        "Could not safely identify the end of the duplicate normalize() "
        "function."
    )


duplicate_block = text[second_start:next_function]


if "return value" not in duplicate_block:
    fail(
        "The second normalize() function does not have the expected "
        "structure. Refusing to modify the file."
    )


timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
BACKUP_DIR.mkdir(parents=True, exist_ok=True)

backup = (
    BACKUP_DIR
    / f"continuityData.js.pre-remove-duplicate-normalize-{timestamp}"
)

if backup.exists():
    fail(f"Backup already exists:\n{backup}")


shutil.copy2(TARGET, backup)


updated = text[:second_start] + text[next_function:]


# Verify exactly one normalize() remains.
remaining = []
position = 0

while True:
    found = updated.find(normalize_marker, position)

    if found == -1:
        break

    remaining.append(found)
    position = found + len(normalize_marker)


if len(remaining) != 1:
    fail(
        "Post-edit verification failed: expected exactly one normalize() "
        f"declaration, found {len(remaining)}."
    )


# Verify the parser repair itself remains intact.
required_markers = [
    "function findSections(sections, definition)",
    "function buildViewerSections(text)",
    "'CURRENT_IMPLEMENTED_ARCHITECTURE'",
    "'INSTANCE-LOCAL MODULE ARCHITECTURE'",
    "'CURRENT_IMMEDIATE_PRIORITY'",
    "'MODULARIZATION_PROTOCOL__VERY_IMPORTANT'",
    "export async function loadContinuitySections()",
]


for marker in required_markers:
    if marker not in updated:
        fail(
            "Post-edit verification failed. The expected parser repair "
            f"marker is missing:\n{marker}\n"
            f"Original file preserved at:\n{backup}"
        )


TARGET.write_text(updated, encoding="utf-8")


# Final read-back verification.
written = TARGET.read_text(encoding="utf-8")

if written.count("function normalize(value) {") != 1:
    fail(
        "Final verification failed: duplicate normalize() remains."
    )


print()
print("Duplicate normalize() declaration removed successfully.")
print()
print(f"Modified: {TARGET}")
print(f"Backup:   {backup}")
print()
print("Preserved:")
print("  - Existing parser repair")
print("  - Section aggregation")
print("  - Existing loadContinuitySections() interface")
print("  - Continuity document")
print("  - ContinuityViewer.jsx")
print()
print("The JavaScript syntax error should now be resolved.")