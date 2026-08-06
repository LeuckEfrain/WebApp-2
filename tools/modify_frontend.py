from pathlib import Path
from datetime import datetime
import shutil
import subprocess
import sys
import re


# ============================================================
# Continuity Viewer phase-status UI refinement
# ============================================================

TOOLS_DIR = Path(__file__).resolve().parent
REPO_ROOT = TOOLS_DIR.parent

EXPECTED_COMMIT = "3c3c4e69382386cc9c39875432234696c679d50a"

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


def require(text, marker, description):
    if marker not in text:
        fail(
            f"{description}\n\n"
            f"Required marker:\n"
            f"  {marker}"
        )


def require_count(text, marker, expected, description):
    actual = text.count(marker)

    if actual != expected:
        fail(
            f"{description}\n\n"
            f"Expected: {expected}\n"
            f"Found: {actual}"
        )


def replace_exact(text, old, new, description):
    count = text.count(old)

    if count != 1:
        fail(
            f"{description}\n\n"
            f"Expected exactly 1 occurrence.\n"
            f"Found: {count}"
        )

    return text.replace(old, new, 1)


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
        f"Expected:\n"
        f"  {EXPECTED_COMMIT}\n\n"
        f"Found:\n"
        f"  {current_commit}"
    )


jsx_original = JSX_PATH.read_text(
    encoding="utf-8"
)

css_original = CSS_PATH.read_text(
    encoding="utf-8"
)


jsx = jsx_original
css = css_original


print("Foundation verified:")
print(f"  {EXPECTED_COMMIT}")


# ============================================================
# Verify existing Continuity Viewer architecture
# ============================================================

required_jsx_markers = [
    "const [phaseStatuses, setPhaseStatuses] = useState(",
    "const getPhaseState = (goalId, phaseIndex) => {",
    "const setPhaseState = (",
    "webapp2-continuity-phase-statuses",
    "openGoalPhases",
    "onGoalPhaseToggle",
    "continuity-phase-status-indicator",
    "continuity-phase-status-controls",
    "continuity-phase-status-option",
    "checked={state.active}",
    "checked={state.complete}",
    "onPhaseStateChange(",
    "Phase {index + 1}",
    "export default ContinuityViewer;",
]


for marker in required_jsx_markers:
    require(
        jsx,
        marker,
        "Could not verify the existing Continuity Viewer architecture."
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
    "Expected exactly two phase status controls."
)


require_count(
    jsx,
    'type="checkbox"',
    2,
    "Expected exactly two phase status checkboxes."
)


# ============================================================
# Verify the existing state semantics
# ============================================================

require(
    jsx,
    "active: !currentPhase.active",
    "Could not verify existing Active state behavior."
)


require(
    jsx,
    "complete: false",
    "Could not verify that Active clears Complete."
)


require(
    jsx,
    "active: false",
    "Could not verify that Complete clears Active."
)


require(
    jsx,
    "complete: !currentPhase.complete",
    "Could not verify existing Complete state behavior."
)


# ============================================================
# Change user-facing "Neither" -> "Pending"
# ============================================================

pending_expression = ": 'Pending'"

if pending_expression in jsx:
    print("  Pending label already present.")

else:
    neither_expression = ": 'Neither'"

    jsx = replace_exact(
        jsx,
        neither_expression,
        pending_expression,
        "Could not locate the existing Neither status label."
    )


# ============================================================
# Ensure the old user-facing word is gone
# ============================================================

if "Neither" in jsx:
    fail(
        "The old user-facing 'Neither' status remains.\n\n"
        "No changes were made."
    )


# ============================================================
# Verify the underlying state was NOT renamed
# ============================================================

# The implementation should continue to use two booleans:
#
#   active: false
#   complete: false
#
# The third user-facing state is simply Pending.
#
# Do not introduce a persisted "pending" property.

if re.search(
    r"\b(?:pending|Pending)\s*:",
    jsx
):
    fail(
        "A new persisted pending state was introduced.\n\n"
        "Pending must remain a user-facing label only.\n\n"
        "No changes were made."
    )


# ============================================================
# Replace the existing checkbox-control styling
# ============================================================

# The JSX structure already has:
#
# <label className="continuity-phase-status-option">
#     <input ... />
#     <span>Active</span>
# </label>
#
# and the equivalent Complete control.
#
# We preserve that structure and state wiring. Only the visual
# treatment is changed.

css_section_marker = (
    "/* ============================================================\n"
    "   CONTINUITY PHASE CONTROLS\n"
    "   ============================================================ */"
)


css_section_pos = css.find(
    css_section_marker
)


if css_section_pos == -1:
    fail(
        "Could not locate the existing Continuity Viewer "
        "phase-controls CSS section.\n\n"
        "No changes were made."
    )


existing_css_section = css[
    css_section_pos:
]


for marker in [
    ".continuity-phase-status-indicator",
    ".continuity-phase-status-controls",
    ".continuity-phase-status-option",
]:
    require(
        existing_css_section,
        marker,
        "The existing Continuity Viewer phase-controls CSS "
        "section is incomplete."
    )


# ============================================================
# Canonical Continuity Viewer UI
# ============================================================

new_css_section = """
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
    font-weight: 600;
    letter-spacing: 0.12em;
    line-height: 1.2;

    text-transform: uppercase;
}

.continuity-phase strong {
    display: block;

    margin-top: 3px;

    color: var(--theme-text-primary);
    font-size: 11px;
    font-weight: 600;
    line-height: 1.4;
}


/* ------------------------------------------------------------
   Phase status indicator
   ------------------------------------------------------------ */

.continuity-phase-status-indicator {
    display: inline-flex;
    align-items: center;
    justify-content: center;

    flex: 0 0 auto;

    min-width: 58px;
    min-height: 22px;

    padding: 3px 7px;

    border: 1px solid var(--theme-border);
    border-radius: 4px;

    background: transparent;
    color: var(--theme-text-muted);

    font-size: 8px;
    font-weight: 600;
    letter-spacing: 0.1em;
    line-height: 1;

    text-align: center;
    text-transform: uppercase;
}

.continuity-phase-status-indicator.active {
    border-color: var(--theme-border-strong);
    background: var(--theme-bg-panel);
    color: var(--theme-text-primary);
}

.continuity-phase-status-indicator.complete {
    border-color: var(--theme-border-strong);
    background: var(--theme-text-primary);
    color: var(--theme-bg-control);
}

.continuity-phase-status-indicator:not(.active):not(.complete) {
    opacity: 0.75;
}


/* ------------------------------------------------------------
   Phase status controls
   ------------------------------------------------------------ */

.continuity-phase-status-controls {
    display: flex;
    align-items: center;

    gap: 6px;

    margin-top: 9px;
}


/*
 * The browser checkbox is retained for semantics and state
 * management but visually replaced by the compact control
 * treatment below.
 */

.continuity-phase-status-option {
    position: relative;

    display: inline-flex;
    align-items: center;

    margin: 0;

    cursor: pointer;
}

.continuity-phase-status-option input {
    position: absolute;

    width: 1px;
    height: 1px;

    margin: -1px;
    padding: 0;

    overflow: hidden;
    clip: rect(0, 0, 0, 0);

    white-space: nowrap;

    border: 0;
}

.continuity-phase-status-option span {
    display: inline-flex;
    align-items: center;
    justify-content: center;

    min-width: 66px;
    min-height: 24px;

    padding: 4px 9px;

    border: 1px solid var(--theme-border);
    border-radius: 4px;

    background: var(--theme-bg-control);
    color: var(--theme-text-muted);

    font-size: 8px;
    font-weight: 600;
    letter-spacing: 0.09em;
    line-height: 1;

    text-transform: uppercase;

    transition:
        background 0.15s ease,
        border-color 0.15s ease,
        color 0.15s ease;
}

.continuity-phase-status-option:hover span {
    border-color: var(--theme-border-strong);
    color: var(--theme-text-primary);
}

.continuity-phase-status-option input:focus-visible + span {
    outline: 1px solid var(--theme-border-strong);
    outline-offset: 2px;
}

.continuity-phase-status-option input:checked + span {
    border-color: var(--theme-border-strong);
    background: var(--theme-bg-panel);
    color: var(--theme-text-primary);
}


/*
 * Complete gets the strongest visual treatment, matching the
 * application's existing light primary-button language without
 * introducing a new accent color.
 */

.continuity-phase-status-option
input:checked + span {
    box-shadow: inset 0 0 0 1px transparent;
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


# Replace everything from the canonical Continuity Viewer
# section to the end of the stylesheet.
css = (
    css[:css_section_pos].rstrip()
    + "\n\n"
    + new_css_section.strip()
    + "\n"
)


# ============================================================
# Final verification — JSX
# ============================================================

# Pending must be visible.
require(
    jsx,
    ": 'Pending'",
    "The Pending status label was not created."
)


# Neither must be gone.
if "Neither" in jsx:
    fail(
        "The old Neither label remains in ContinuityViewer.jsx.\n\n"
        "No changes were made."
    )


# Existing controls must remain.
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
    "Expected exactly two semantic checkbox controls."
)


# Existing state wiring must remain.
require(
    jsx,
    "onPhaseStateChange(",
    "The existing phase-state handler is no longer connected."
)


require(
    jsx,
    "checked={state.active}",
    "The Active state binding was removed."
)


require(
    jsx,
    "checked={state.complete}",
    "The Complete state binding was removed."
)


# Persistence must remain.
require(
    jsx,
    "webapp2-continuity-phase-statuses",
    "Phase status persistence was removed."
)


# Goal completion logic must remain.
require(
    jsx,
    "allPhasesComplete",
    "Goal completion logic was unexpectedly removed."
)


require(
    jsx,
    "? 'Complete'",
    "Goal Complete status behavior was unexpectedly removed."
)


# The title must remain.
require(
    jsx,
    "Phase {index + 1}",
    "Phase title numbering was unexpectedly removed."
)


# Exactly one default export.
require_count(
    jsx,
    "export default ContinuityViewer;",
    1,
    "Expected exactly one ContinuityViewer default export."
)


# ============================================================
# Final verification — CSS
# ============================================================

required_css_markers = [
    ".continuity-phase-status-indicator",
    ".continuity-phase-status-indicator.active",
    ".continuity-phase-status-indicator.complete",
    ".continuity-phase-status-controls",
    ".continuity-phase-status-option",
    ".continuity-phase-status-option input",
    ".continuity-phase-status-option span",
    ".continuity-phase-status-option input:checked + span",
    ".continuity-goal-actions",
]


for marker in required_css_markers:
    require(
        css,
        marker,
        "The new Continuity Viewer CSS is incomplete."
    )


# Verify the browser-default checkbox is actually hidden.
require(
    css,
    "clip: rect(0, 0, 0, 0);",
    "The native checkbox was not safely visually replaced."
)


# Ensure the old generic checkbox sizing is gone.
if re.search(
    r"\.continuity-phase-status-option input\s*\{[^}]*"
    r"width:\s*11px[^}]*"
    r"height:\s*11px",
    css,
    re.DOTALL,
):
    fail(
        "The old browser-checkbox sizing remains in the "
        "phase status controls.\n\n"
        "No changes were made."
    )


# Exactly one canonical CSS section.
require_count(
    css,
    "CONTINUITY PHASE CONTROLS",
    1,
    "Expected exactly one Continuity Viewer phase-controls CSS section."
)


# ============================================================
# Verify only intended files will change
# ============================================================

if jsx == jsx_original:
    fail(
        "ContinuityViewer.jsx did not receive the Pending "
        "label update.\n\n"
        "No changes were made."
    )


if css == css_original:
    fail(
        "styles.css did not change.\n\n"
        "No changes were made."
    )


# ============================================================
# Backups
# ============================================================

jsx_backup = backup(
    JSX_PATH,
    "phase-status-ui-refinement",
)

css_backup = backup(
    CSS_PATH,
    "phase-status-ui-refinement",
)


# ============================================================
# Write
# ============================================================

try:
    JSX_PATH.write_text(
        jsx,
        encoding="utf-8",
        newline="",
    )

    CSS_PATH.write_text(
        css,
        encoding="utf-8",
        newline="",
    )

except Exception as exc:
    try:
        shutil.copy2(
            jsx_backup,
            JSX_PATH,
        )
        shutil.copy2(
            css_backup,
            CSS_PATH,
        )
    except Exception:
        pass

    fail(
        "Could not safely write the modified source files.\n\n"
        f"{exc}"
    )


# ============================================================
# Success
# ============================================================

print()
print("SUCCESS")
print("-------")
print("Continuity Viewer phase-status UI refined successfully.")

print()
print("Phase status:")
print("  - Neither is now displayed as Pending.")
print("  - Pending is presentation-only.")
print("  - Existing false/false state remains unchanged.")
print("  - Existing Active/Complete state logic remains unchanged.")
print("  - Existing localStorage persistence remains unchanged.")
print("  - Existing goal completion logic remains unchanged.")

print()
print("Controls:")
print("  - Native browser checkbox appearance removed.")
print("  - Active and Complete use compact custom controls.")
print("  - Controls match the existing border/background language.")
print("  - Selected controls receive a restrained highlighted state.")
print("  - Keyboard focus remains accessible.")
print("  - No new accent colors were introduced.")

print()
print("Layout:")
print("  - Left-most phase status indicator preserved.")
print("  - Phase title numbering preserved.")
print("  - Goal action sizing preserved.")

print()
print("Modified:")
print(f"  {JSX_PATH}")
print(f"  {CSS_PATH}")

print()
print("Backups:")
print(f"  {jsx_backup}")
print(f"  {css_backup}")

print()
print("Foundation:")
print(f"  {EXPECTED_COMMIT}")

print()
print("WebApp-2 source code was modified successfully.")

