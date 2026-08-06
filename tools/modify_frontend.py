from pathlib import Path
from datetime import datetime
import shutil
import subprocess
import re
import sys


# ============================================================
# Configuration
# ============================================================

TOOLS_DIR = Path(__file__).resolve().parent
REPO_ROOT = TOOLS_DIR.parent

EXPECTED_COMMIT = (
    "8a0452bc303ab0f17000541db5f290b775ead438"
)

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

TIMESTAMP = datetime.now().strftime("%Y%m%d-%H%M%S")


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


def run_git(*args):
    try:
        result = subprocess.run(
            [
                "git",
                "-C",
                str(REPO_ROOT),
                *args,
            ],
            capture_output=True,
            text=True,
            check=True,
        )
    except subprocess.CalledProcessError as exc:
        fail(
            "Git verification failed.\n\n"
            + (exc.stderr or exc.stdout or str(exc)).strip()
        )

    return result.stdout.strip()


def backup_file(path, label):
    backup = path.with_name(
        f"{path.name}.pre-{label}-{TIMESTAMP}"
    )

    if backup.exists():
        fail(
            "Backup already exists:\n"
            f"  {backup}"
        )

    shutil.copy2(path, backup)
    return backup


def require_exactly(text, needle, count, description):
    actual = text.count(needle)

    if actual != count:
        fail(
            f"{description}\n\n"
            f"Expected exactly {count} occurrence(s), "
            f"found: {actual}\n\n"
            "No changes were made."
        )


# ============================================================
# Repository verification
# ============================================================

if not (REPO_ROOT / ".git").is_dir():
    fail(
        "This script must be placed in the WebApp-2 "
        "repository tools directory.\n\n"
        "Expected .git directory:\n"
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


current_commit = run_git(
    "rev-parse",
    "HEAD",
)

if current_commit != EXPECTED_COMMIT:
    fail(
        "Repository foundation does not match the verified "
        "foundation.\n\n"
        f"Expected:\n"
        f"  {EXPECTED_COMMIT}\n\n"
        f"Found:\n"
        f"  {current_commit}"
    )


jsx = JSX_PATH.read_text(
    encoding="utf-8"
)

css = CSS_PATH.read_text(
    encoding="utf-8"
)


print("Foundation verified:")
print(f"  {EXPECTED_COMMIT}")


# ============================================================
# Verify actual foundation architecture
# ============================================================

# These are not guesses about the UI. They are the actual
# state-management structures in the verified foundation.

required_foundation_markers = [
    "function Section({",
    "getPhaseState,",
    "onPhaseStateChange",
    "const getPhaseState = (goalId, phaseIndex) => {",
    "const setPhaseState = (",
    "const cyclePhaseState = (",
    "const state =",
    "getPhaseState(",
    "goal.id,",
    "index",
    "continuity-phase-status-control",
    "Phase {index + 1}",
    "className=\"continuity-phase-main\"",
    "className=\"continuity-phase-title\"",
    "export default ContinuityViewer;",
]


for marker in required_foundation_markers:
    if marker not in jsx:
        fail(
            "Required foundation marker does not exist:\n"
            f"  {marker}\n\n"
            "The repository may have changed since the "
            "verified foundation.\n\n"
            "No changes were made."
        )


# ============================================================
# Verify state-management integrity
# ============================================================

require_exactly(
    jsx,
    "const getPhaseState = (goalId, phaseIndex) => {",
    1,
    "Expected exactly one getPhaseState definition.",
)

require_exactly(
    jsx,
    "const setPhaseState = (",
    1,
    "Expected exactly one setPhaseState definition.",
)

require_exactly(
    jsx,
    "const cyclePhaseState = (",
    1,
    "Expected exactly one cyclePhaseState definition.",
)


# The persistence mechanism must remain present.
if "webapp2-continuity-phase-statuses" not in jsx:
    fail(
        "The existing phase-status localStorage key "
        "could not be verified.\n\n"
        "No changes were made."
    )


# The existing mutually-exclusive behavior must remain
# untouched. Verify the important assignments before editing.
if "active: !currentPhase.active" not in jsx:
    fail(
        "Could not verify the existing Active-state behavior.\n\n"
        "No changes were made."
    )

if "complete: false" not in jsx:
    fail(
        "Could not verify the existing Active-state exclusivity.\n\n"
        "No changes were made."
    )

if "active: false" not in jsx:
    fail(
        "Could not verify the existing Complete-state exclusivity.\n\n"
        "No changes were made."
    )

if "complete: !currentPhase.complete" not in jsx:
    fail(
        "Could not verify the existing Complete-state behavior.\n\n"
        "No changes were made."
    )


# ============================================================
# Locate the phase rendering block
# ============================================================

# Work from the exact semantic structure in the foundation.
phase_map_marker = "{goal.phases.map("

phase_map_pos = jsx.find(
    phase_map_marker
)

if phase_map_pos == -1:
    fail(
        "Could not locate the goal phase rendering map.\n\n"
        "No changes were made."
    )


phase_state_pos = jsx.find(
    "const state =",
    phase_map_pos
)

if phase_state_pos == -1:
    fail(
        "Could not locate the phase state lookup.\n\n"
        "No changes were made."
    )


phase_element_pos = jsx.find(
    "className={",
    phase_state_pos
)

if phase_element_pos == -1:
    fail(
        "Could not locate the phase element.\n\n"
        "No changes were made."
    )


phase_class_pos = jsx.find(
    "'continuity-phase'",
    phase_element_pos
)

if phase_class_pos == -1:
    fail(
        "Could not locate the continuity-phase class.\n\n"
        "No changes were made."
    )


# Make sure the phase title belongs to this same renderer.
phase_title_pos = jsx.find(
    "Phase {index + 1}",
    phase_state_pos
)

if phase_title_pos == -1:
    fail(
        "Could not locate the phase title inside the "
        "phase renderer.\n\n"
        "No changes were made."
    )


# ============================================================
# Remove redundant standalone number
# ============================================================

standalone_number_pattern = re.compile(
    r"""
    <span>
    \s*
    \{index \+ 1\}
    \s*
    </span>
    """,
    re.VERBOSE,
)

number_matches = list(
    standalone_number_pattern.finditer(
        jsx,
        phase_state_pos,
    )
)

if len(number_matches) != 1:
    fail(
        "Could not safely locate the redundant standalone "
        "phase number.\n\n"
        f"Expected exactly 1 occurrence, found: "
        f"{len(number_matches)}\n\n"
        "No changes were made."
    )


number_match = number_matches[0]

# Ensure the number is before the phase title and therefore
# is the standalone number, not the title's "Phase {index + 1}".
if number_match.start() > phase_title_pos:
    fail(
        "The located phase number appears after the phase "
        "title.\n\n"
        "No changes were made."
    )


# ============================================================
# Locate old status button
# ============================================================

status_button_pattern = re.compile(
    r"""
    <button
    \s*
    type="button"
    \s*
    className=\{
        \s*
        'continuity-phase-status-control'
        .*?
    \}
    \s*
    onClick=\{\(\)\s*=>\s*
        cyclePhaseState\(
            \s*
            goal\.id
            \s*,\s*
            index
            \s*
        \)
    \s*\}
    .*?
    </button>
    """,
    re.VERBOSE | re.DOTALL,
)

status_matches = list(
    status_button_pattern.finditer(
        jsx,
        phase_state_pos,
    )
)

if len(status_matches) != 1:
    fail(
        "Could not safely locate the existing phase status "
        "button.\n\n"
        f"Expected exactly 1 occurrence, found: "
        f"{len(status_matches)}\n\n"
        "No changes were made."
    )


status_match = status_matches[0]


# ============================================================
# Remove both obsolete UI elements
# ============================================================

# Remove the standalone number first.
jsx_after_number = (
    jsx[:number_match.start()]
    + jsx[number_match.end():]
)

# Recalculate the status-button match after the first edit.
status_matches_after_number = list(
    status_button_pattern.finditer(
        jsx_after_number,
        phase_state_pos,
    )
)

if len(status_matches_after_number) != 1:
    fail(
        "The phase status button could not be re-identified "
        "after removing the standalone phase number.\n\n"
        "No changes were made."
    )


status_match = status_matches_after_number[0]


# Replace the old clickable status button with a passive
# indicator. The actual controls are added separately below.
status_indicator = """<span
className={
'continuity-phase-status-indicator' +
(state.active
? ' active'
: state.complete
? ' complete'
: '')
}
>
{state.active
? 'Active'
: state.complete
? 'Complete'
: 'Neither'}
</span>"""


jsx_after_status = (
    jsx_after_number[:status_match.start()]
    + status_indicator
    + jsx_after_number[status_match.end():]
)


# ============================================================
# Locate phase title block
# ============================================================

title_container_marker = (
    '<div className="continuity-phase-title">'
)

title_container_pos = jsx_after_status.find(
    title_container_marker,
    phase_state_pos,
)

if title_container_pos == -1:
    fail(
        "Could not safely locate the phase title container.\n\n"
        "No changes were made."
    )


title_container_end = jsx_after_status.find(
    "</div>",
    title_container_pos,
)

if title_container_end == -1:
    fail(
        "Could not safely locate the end of the phase title "
        "container.\n\n"
        "No changes were made."
    )


title_container_end += len("</div>")


# ============================================================
# Insert Active / Complete controls
# ============================================================

if "continuity-phase-status-controls" in jsx_after_status:
    fail(
        "Phase status controls already exist in the current "
        "source.\n\n"
        "No changes were made."
    )


controls = """


<div className="continuity-phase-status-controls">
<label className="continuity-phase-status-option">
<input
type="checkbox"
checked={state.active}
onChange={() =>
onPhaseStateChange(
goal.id,
index,
'active'
)
}
/>
<span>Active</span>
</label>

<label className="continuity-phase-status-option">
<input
type="checkbox"
checked={state.complete}
onChange={() =>
onPhaseStateChange(
goal.id,
index,
'complete'
)
}
/>
<span>Complete</span>
</label>
</div>"""


jsx_modified = (
    jsx_after_status[:title_container_end]
    + controls
    + jsx_after_status[title_container_end:]
)


# ============================================================
# Remove obsolete cyclePhaseState definition
# ============================================================

cycle_start_marker = (
    "const cyclePhaseState = ("
)

cycle_start = jsx_modified.find(
    cycle_start_marker
)

if cycle_start == -1:
    fail(
        "Could not locate the obsolete cyclePhaseState "
        "definition.\n\n"
        "No changes were made."
    )


# The next function in the verified foundation is openAll.
open_all_marker = (
    "const openAll = () => {"
)

open_all_pos = jsx_modified.find(
    open_all_marker,
    cycle_start,
)

if open_all_pos == -1:
    fail(
        "Could not safely locate the end of cyclePhaseState.\n\n"
        "No changes were made."
    )


jsx_modified = (
    jsx_modified[:cycle_start]
    + jsx_modified[open_all_pos:]
)


# ============================================================
# CSS preparation
# ============================================================

css_marker = (
    "/* Continuity Viewer phase status controls */"
)

# Remove a previously generated version of this exact section
# if one somehow exists in the foundation being processed.
if css_marker in css:
    css_start = css.find(css_marker)

    # This build expects the foundation to not already contain
    # the new controls. Remove through the end of our section.
    css_end_marker = (
        "/* End Continuity Viewer phase status controls */"
    )

    css_end = css.find(
        css_end_marker,
        css_start,
    )

    if css_end == -1:
        fail(
            "A partial Continuity Viewer phase-status CSS "
            "section already exists.\n\n"
            "No changes were made."
        )

    css_end += len(css_end_marker)

    css = (
        css[:css_start]
        + css[css_end:]
    )


new_css = """

/* Continuity Viewer phase status controls */

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
    border-color: var(--theme-border-strong);
    color: var(--theme-text-primary);
}

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
}

.continuity-phase-status-option span {
    white-space: nowrap;
}

/* End Continuity Viewer phase status controls */
"""


css_modified = css.rstrip() + "\n" + new_css


# ============================================================
# Final verification
# ============================================================

# --- JSX structure ---

if "continuity-phase-status-control" in jsx_modified:
    # This singular class is the old control. The new class
    # "continuity-phase-status-controls" intentionally contains
    # that substring, so test the actual class declaration.
    if (
        "className=\"continuity-phase-status-control\""
        in jsx_modified
        or
        "className={'continuity-phase-status-control'"
        in jsx_modified
    ):
        fail(
            "The obsolete clickable phase status control "
            "remains.\n\n"
            "No changes were made."
        )


if "cyclePhaseState" in jsx_modified:
    fail(
        "The obsolete cyclePhaseState helper remains.\n\n"
        "No changes were made."
    )


if "setPhaseState = (" not in jsx_modified:
    fail(
        "The existing setPhaseState function was removed.\n\n"
        "No changes were made."
    )


if "onPhaseStateChange" not in jsx_modified:
    fail(
        "The new phase controls are not connected to the "
        "existing phase-state mechanism.\n\n"
        "No changes were made."
    )


require_exactly(
    jsx_modified,
    "continuity-phase-status-controls",
    1,
    "Expected exactly one phase status controls container.",
)


require_exactly(
    jsx_modified,
    "continuity-phase-status-option",
    2,
    "Expected exactly two phase status options.",
)


require_exactly(
    jsx_modified,
    'type="checkbox"',
    2,
    "Expected exactly two phase status checkboxes.",
)


require_exactly(
    jsx_modified,
    "checked={state.active}",
    1,
    "Expected exactly one Active checkbox binding.",
)


require_exactly(
    jsx_modified,
    "checked={state.complete}",
    1,
    "Expected exactly one Complete checkbox binding.",
)


# The title remains.
if "Phase {index + 1}" not in jsx_modified:
    fail(
        "The phase title was unexpectedly removed.\n\n"
        "No changes were made."
    )


# The redundant standalone number must be gone.
standalone_number_remaining = list(
    standalone_number_pattern.finditer(
        jsx_modified,
        0,
    )
)

if standalone_number_remaining:
    fail(
        "The redundant standalone phase number remains.\n\n"
        "No changes were made."
    )


# Exactly one default export.
require_exactly(
    jsx_modified,
    "export default ContinuityViewer;",
    1,
    "Expected exactly one ContinuityViewer default export.",
)


# --- CSS ---

if ".continuity-phase-status-controls" not in css_modified:
    fail(
        "New phase controls CSS is missing.\n\n"
        "No changes were made."
    )


if ".continuity-phase-status-option" not in css_modified:
    fail(
        "New phase status option CSS is missing.\n\n"
        "No changes were made."
    )


if ".continuity-phase-status-indicator" not in css_modified:
    fail(
        "New phase status indicator CSS is missing.\n\n"
        "No changes were made."
    )


# ============================================================
# Backup
# ============================================================

jsx_backup = backup_file(
    JSX_PATH,
    "phase-status-controls",
)

css_backup = backup_file(
    CSS_PATH,
    "phase-status-controls",
)


# ============================================================
# Write
# ============================================================

try:
    JSX_PATH.write_text(
        jsx_modified,
        encoding="utf-8",
        newline="",
    )

    CSS_PATH.write_text(
        css_modified,
        encoding="utf-8",
        newline="",
    )

except Exception as exc:
    # Restore from backups if writing fails.
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
        "Could not write the modified source safely.\n\n"
        f"{exc}"
    )


# ============================================================
# Success
# ============================================================

print()
print("SUCCESS")
print("-------")
print("Continuity Viewer phase controls implemented.")

print()
print("Phase UI:")
print("  - Status remains at the left-most end of each phase.")
print("  - Standalone phase numbering was removed.")
print("  - Phase titles still display Phase 1, Phase 2, etc.")
print("  - Active checkbox added.")
print("  - Complete checkbox added.")
print("  - Existing phase-state mechanism is used.")
print("  - Existing localStorage persistence is preserved.")
print("  - Existing mutually-exclusive state behavior is preserved.")

print()
print("State architecture:")
print("  - setPhaseState remains authoritative.")
print("  - cyclePhaseState was removed because the new controls")
print("    no longer need the cycling wrapper.")
print("  - Goal completion logic remains unchanged.")
print("  - Goal-level Active Goal behavior remains unchanged.")
print("  - Phase visibility behavior remains unchanged.")

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