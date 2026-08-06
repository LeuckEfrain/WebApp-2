from pathlib import Path
import shutil
from datetime import datetime

TOOLS_DIR = Path(__file__).resolve().parent
REPO_ROOT = TOOLS_DIR.parent

TARGET = (
    REPO_ROOT
    / "frontend"
    / "src"
    / "instance"
    / "modules"
    / "continuity-viewer"
    / "ContinuityViewer.jsx"
)

EXPORT = "export default ContinuityViewer;"

print("=" * 60)
print("Continuity Viewer duplicate-export repair")
print("=" * 60)

# ------------------------------------------------------------
# Safety checks
# ------------------------------------------------------------

if not (REPO_ROOT / ".git").exists():
    print("\nERROR")
    print("-----")
    print("Could not verify the WebApp-2 repository root:")
    print(REPO_ROOT)
    print("\nExpected .git directory:")
    print(REPO_ROOT / ".git")
    print("\nNo changes were made.")
    raise SystemExit(1)

if not TARGET.exists():
    print("\nERROR")
    print("-----")
    print("Required file does not exist:")
    print(TARGET)
    print("\nNo changes were made.")
    raise SystemExit(1)

# ------------------------------------------------------------
# Read source
# ------------------------------------------------------------

original = TARGET.read_text(encoding="utf-8")

occurrences = original.count(EXPORT)

if occurrences != 2:
    print("\nERROR")
    print("-----")
    print("Expected exactly 2 occurrences of:")
    print(EXPORT)
    print()
    print(f"Found: {occurrences}")
    print()
    print("No changes were made.")
    raise SystemExit(1)

# ------------------------------------------------------------
# Create backup
# ------------------------------------------------------------

timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")

backup = TARGET.with_name(
    TARGET.name + f".pre-duplicate-export-repair-{timestamp}"
)

if backup.exists():
    print("\nERROR")
    print("-----")
    print("Backup already exists:")
    print(backup)
    print()
    print("Refusing to overwrite it.")
    print("No changes were made.")
    raise SystemExit(1)

shutil.copy2(TARGET, backup)

# ------------------------------------------------------------
# Remove the SECOND occurrence only
# ------------------------------------------------------------

first_position = original.find(EXPORT)

second_position = original.find(
    EXPORT,
    first_position + len(EXPORT)
)

if first_position == -1 or second_position == -1:
    print("\nERROR")
    print("-----")
    print("Could not safely locate both exports.")
    print("\nNo changes were made.")
    raise SystemExit(1)

updated = (
    original[:second_position]
    + original[second_position + len(EXPORT):]
)

# ------------------------------------------------------------
# Verify modification before writing
# ------------------------------------------------------------

if updated.count(EXPORT) != 1:
    print("\nERROR")
    print("-----")
    print("Safety verification failed before writing.")
    print()
    print("Expected exactly 1 export after the change.")
    print(f"Found: {updated.count(EXPORT)}")
    print()
    print("No changes were made to the source file.")
    print(f"Backup created at:\n  {backup}")
    raise SystemExit(1)

# ------------------------------------------------------------
# Write
# ------------------------------------------------------------

TARGET.write_text(updated, encoding="utf-8", newline="")

# ------------------------------------------------------------
# Final verification
# ------------------------------------------------------------

verified = TARGET.read_text(encoding="utf-8")

if verified.count(EXPORT) != 1:
    print("\nERROR")
    print("-----")
    print("Final verification failed.")
    print()
    print("Expected exactly 1 export.")
    print(f"Found: {verified.count(EXPORT)}")
    print()
    print("Backup:")
    print(f"  {backup}")
    raise SystemExit(1)

print("\nSUCCESS")
print("-------")
print("Removed the second duplicate ContinuityViewer default export.")

print("\nModified:")
print(f"  {TARGET}")

print("\nBackup:")
print(f"  {backup}")

print("\nVerified:")
print("  Exactly one export default ContinuityViewer; remains.")

print("\nWebApp-2 source code was modified successfully.")