from pathlib import Path
from datetime import datetime
import shutil
import subprocess
import sys
import re


# ============================================================
# Continuity Viewer phase-controls CSS cleanup
# ============================================================

TOOLS_DIR = Path(__file__).resolve().parent
REPO_ROOT = TOOLS_DIR.parent

EXPECTED_COMMIT = "4ac4989edcd0452371b790444296742630cee79b"

JSX_PATH = (
    REPO_ROOT
    / "frontend"
    / "src"
    / "instance"
    / "modules"
    / "continuity-viewer"
    / "ContinuityViewer.jsx"
)

CSS_PATH = (
    REPO_ROOT
    / "frontend"
    / "src"
    / "core"
    / "styles.css"
)

STAMP = datetime.now().strftime("%Y%m%d-%H%M%S")


# ============================================================
# Utilities
# ============================================================

def fail(message):
    print()
    print("ERROR")
    print("-----")
    print(message)
    print()
    print("No changes were made.")
    sys.exit(1)


def git_head():
    try:
        return subprocess.run(
            [
                "git",
                "-C",
                str(REPO_ROOT),
                "rev-parse",
                "HEAD",
            ],
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()
    except subprocess.CalledProcessError as exc:
        fail(
            "Could not determine the repository HEAD.\n\n"
            f"{exc.stderr.strip()}"
        )


def backup(path, label):
    destination = path.with_name(
        f"{path.name}.pre-{label}-{STAMP}"
    )

    if destination.exists():
        fail(
            "Backup already exists:\n"
            f"  {destination}"
        )

    shutil.copy2(path, destination)
    return destination


def require(text, value, description):
    if value not in text:
        fail(
            f"{description}\n\n"
            f"Required marker:\n"
            f"  {value}"
        )


def require_count(text, value, expected, description):
    actual = text.count(value)

    if actual != expected:
        fail(
            f"{description}\n\n"
            f"Expected: {expected}\n"
            f"Found: {actual}"
        )


# ============================================================
# Repository verification
# ============================================================

if not (REPO_ROOT / ".git").is_dir():
    fail(
        "This script must be placed in the WebApp-2 "
        "repository tools directory.\n\n"
        f"Expected .git directory:\n"
        f"  {REPO_ROOT / '.git'}"
    )

if not JSX_PATH.exists():
    fail(
        "Required file does not exist:\n"
        f"  {JSX_PATH}"
    )

if not CSS_PATH.exists():
    fail(
        "Required file does not exist:\n"
        f"  {CSS_PATH}"
    )


current_commit = git_head()

if current_commit != EXPECTED_COMMIT:
    fail(
        "Repository foundation does not match the verified commit.\n\n"
        f"Expected:\n  {EXPECTED_COMMIT}\n\n"
        f"Found:\n  {current_commit}"
    )


jsx = JSX_PATH.read_text(encoding="utf-8")
css = CSS_PATH.read_text(encoding="utf-8")


print("Foundation verified:")
print(f"  {EXPECTED_COMMIT}")


# ============================================================
# Verify current JSX
# ============================================================

jsx_markers = [
    "continuity-phase-status-indicator",
    "continuity-phase-status-controls",
    "continuity-phase-status-option",
    "checked={state.active}",
    "checked={state.complete}",
    "onPhaseStateChange(",
    "Phase {index + 1}",
    "const setPhaseState = (",
    "webapp2-continuity-phase-statuses",
    "export default ContinuityViewer;",
]

for marker in jsx_markers:
    require(
        jsx,
        marker,
        "Could not verify the current Continuity Viewer JSX."
    )


require_count(
    jsx,
    "continuity-phase-status-controls",
    1,
    "Expected exactly one phase status controls container."
)

require_count(
    jsx,
    "continuity-phase-status-option",
    2,
    "Expected exactly two phase status options."
)

require_count(
    jsx,
    'type="checkbox"',
    2,
    "Expected exactly two phase status checkboxes."
)


# ============================================================
# Exact obsolete-control detection
# ============================================================

# IMPORTANT:
# Do NOT use:
#
#     ".continuity-phase-status-control" in css
#
# because that is a substring of:
#
#     ".continuity-phase-status-controls"
#
# Instead, detect the singular selector as an actual CSS
# selector boundary.

obsolete_selector_pattern = re.compile(
    r"(?<![A-Za-z0-9_-])"
    r"\.continuity-phase-status-control"
    r"(?!s)(?![A-Za-z0-9_-])"
)

obsolete_matches = list(
    obsolete_selector_pattern.finditer(css)
)


# ============================================================
# Locate and remove obsolete CSS if present
# ============================================================

old_css_start_marker = (
    "/* ============================================================\n"
    "   CONTINUITY VIEWER UI CLEANUP — PHASE STATUS\n"
    "   ============================================================ */"
)

new_css_start_marker = (
    "/* ============================================================\n"
    "   CONTINUITY PHASE CONTROLS REFINEMENT V2\n"
    "   ============================================================ */"
)


if obsolete_matches:
    old_start = css.find(old_css_start_marker)

    if old_start == -1:
        fail(
            "The obsolete clickable phase-status selector exists, "
            "but its historical CSS section could not be safely "
            "located.\n\n"
            "No changes were made."
        )

    new_start = css.find(
        new_css_start_marker,
        old_start,
    )

    if new_start == -1:
        fail(
            "Could not safely locate the end of the obsolete "
            "phase-status CSS section.\n\n"
            "No changes were made."
        )

    old_section = css[
        old_start:new_start
    ]

    if not obsolete_selector_pattern.search(old_section):
        fail(
            "The located historical CSS section does not contain "
            "the obsolete selector.\n\n"
            "No changes were made."
        )

    css_modified = (
        css[:old_start]
        + css[new_start:]
    )

else:
    # The old CSS is already gone.
    css_modified = css


# ============================================================
# Remove an existing V2 section before rebuilding it
# ============================================================

v2_start_marker = (
    "/* ============================================================\n"
    "   CONTINUITY PHASE CONTROLS REFINEMENT V2\n"
    "   ============================================================ */"
)

v2_start = css_modified.find(
    v2_start_marker
)

if v2_start == -1:
    fail(
        "Could not locate the existing Continuity Viewer "
        "phase-controls CSS section.\n\n"
        "No changes were made."
    )


# This section is expected to be the final generated section.
# Verify the expected rules exist before replacing it.
existing_v2 = css_modified[v2_start:]

for marker in [
    ".continuity-phase-status-indicator",
    ".continuity-phase-status-controls",
    ".continuity-phase-status-option",
]:
    require(
        existing_v2,
        marker,
        "The existing phase-controls CSS section is incomplete."
    )


# ============================================================
# Canonical phase-controls CSS
# ============================================================

clean_css_section = """
/* ============================================================
   CONTINUITY PHASE CONTROLS
   ============================================================ */

.continuity-phase-main {
    min-width: 0;
    flex: 1;
}

.continuity-phase-title {
    min-width: 0;
}

.continuity-phase-title > span {
    display: block;

    color: var(--theme-text-muted);

    font-size: 8px;
    letter-spacing: 0.08em;

    text-transform: uppercase;
}

.continuity-phase strong {
    display: block;

    margin-top: 2px;

    color: var(--theme-text-primary);
    font-size: 11px;
}


/* ------------------------------------------------------------
   Phase status indicator
   ------------------------------------------------------------ */

.continuity-phase-status-indicator {
    flex: 0 0 auto;

    min-width: 58px;

    padding: 4px 7px;

    border: 1px solid var(--theme-border);
    border-radius: 4px;

    background: transparent;
    color: var(--theme-text-muted);

    font-size: 8px;
    font-weight: 500;
    letter-spacing: 0.08em;
    line-height: 1.2;

    text-align: center;
    text-transform: uppercase;
}

.continuity-phase-status-indicator.active,
.continuity-phase-status-indicator.complete {
    background: var(--theme-bg-panel);
    border-color: var(--theme-border-strong);
    color: var(--theme-text-primary);
}


/* ------------------------------------------------------------
   Phase status controls
   ------------------------------------------------------------ */

.continuity-phase-status-controls {
    display: flex;
    align-items: center;

    gap: 8px;

    margin-top: 7px;
}

.continuity-phase-status-option {
    display: inline-flex;
    align-items: center;

    gap: 5px;

    color: var(--theme-text-muted);

    font-size: 9px;
    line-height: 1;

    cursor: pointer;
}

.continuity-phase-status-option:hover {
    color: var(--theme-text-primary);
}

.continuity-phase-status-option input {
    width: 11px;
    height: 11px;

    margin: 0;

    accent-color: var(--theme-text-primary);
}

.continuity-phase-status-option span {
    white-space: nowrap;
}


/* ------------------------------------------------------------
   Goal action buttons
   ------------------------------------------------------------ */

.continuity-goal-actions {
    display: flex;
    align-items: center;

    gap: 7px;

    flex-shrink: 0;
}

.continuity-goal-actions > button {
    min-width: 96px;

    padding: 8px 12px;

    text-align: center;
}

.continuity-goal-actions > button.primary,
.continuity-goal-actions > button.secondary {
    font-size: 10px;
}
"""


# Replace everything from the old V2 section to EOF.
css_modified = (
    css_modified[:v2_start].rstrip()
    + "\n\n"
    + clean_css_section.strip()
    + "\n"
)


# ============================================================
# Final verification
# ============================================================

# The JSX must not be modified by this build.
if jsx != JSX_PATH.read_text(encoding="utf-8"):
    fail(
        "ContinuityViewer.jsx changed unexpectedly.\n\n"
        "This build is CSS-only and will not overwrite JSX."
    )


# The exact obsolete selector must be absent.
if obsolete_selector_pattern.search(css_modified):
    fail(
        "The obsolete clickable phase-status CSS remains.\n\n"
        "No changes were made."
    )


# New plural selector must be present.
require(
    css_modified,
    ".continuity-phase-status-controls",
    "The new phase status controls CSS is missing."
)

require(
    css_modified,
    ".continuity-phase-status-option",
    "The new phase status option CSS is missing."
)

require(
    css_modified,
    ".continuity-phase-status-indicator",
    "The phase status indicator CSS is missing."
)


# The singular selector must not be mistaken for the plural
# selector by our verification.
if re.search(
    r"\.continuity-phase-status-control\s*\{",
    css_modified,
):
    fail(
        "An exact singular continuity-phase-status-control "
        "CSS rule remains.\n\n"
        "No changes were made."
    )


# Ensure the new section exists only once.
require_count(
    css_modified,
    "CONTINUITY PHASE CONTROLS",
    1,
    "Expected exactly one canonical phase-controls CSS section."
)


# ============================================================
# Backup
# ============================================================

css_backup = backup(
    CSS_PATH,
    "continuity-phase-controls-cleanup",
)


# ============================================================
# Write
# ============================================================

try:
    CSS_PATH.write_text(
        css_modified,
        encoding="utf-8",
        newline="",
    )

except Exception as exc:
    try:
        shutil.copy2(
            css_backup,
            CSS_PATH,
        )
    except Exception:
        pass

    fail(
        "Could not safely write styles.css.\n\n"
        f"{exc}"
    )


# ============================================================
# Success
# ============================================================

print()
print("SUCCESS")
print("-------")
print("Continuity Viewer phase-controls CSS cleaned successfully.")

print()
print("Implemented:")
print("  - Removed obsolete clickable status CSS.")
print("  - Preserved Active/Complete controls.")
print("  - Preserved existing phase-state architecture.")
print("  - Preserved existing phase persistence.")
print("  - Preserved left-most phase status indicator.")
print("  - Preserved Phase 1 / Phase 2 title numbering.")
print("  - Preserved removal of redundant standalone numbering.")
print("  - Normalized phase-control CSS.")
print("  - Balanced goal action button sizing.")
print("  - ContinuityViewer.jsx was not modified.")

print()
print("Modified:")
print(f"  {CSS_PATH}")

print()
print("Backup:")
print(f"  {css_backup}")

print()
print("Foundation:")
print(f"  {EXPECTED_COMMIT}")

print()
print("WebApp-2 source code was modified successfully.")