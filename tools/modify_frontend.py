from pathlib import Path
import shutil
import subprocess
from datetime import datetime


# ============================================================
# Continuity Viewer — phase controls refinement
# ============================================================

TOOLS_DIR = Path(__file__).resolve().parent
REPO_ROOT = TOOLS_DIR.parent

EXPECTED_COMMIT = "44f893b63f6339ed03d7138c410b9ba379a66f2f"

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


def fail(message):
    print()
    print("ERROR")
    print("-----")
    print(message)
    print()
    print("No changes were made.")
    raise SystemExit(1)


def backup(path, label):
    destination = path.with_name(
        f"{path.name}.pre-{label}-{STAMP}"
    )

    if destination.exists():
        fail(
            "Backup already exists:\n"
            f"  {destination}\n\n"
            "Refusing to overwrite it."
        )

    shutil.copy2(path, destination)
    return destination


def find_unique(text, marker, description):
    count = text.count(marker)

    if count != 1:
        fail(
            f"Could not safely locate {description}.\n\n"
            f"Expected exactly 1 occurrence, found: {count}\n\n"
            "No changes were made."
        )

    return text.index(marker)


# ============================================================
# Repository verification
# ============================================================

if not (REPO_ROOT / ".git").exists():
    fail(
        "This script must be placed in the WebApp-2 repository "
        "tools directory.\n\n"
        f"Expected .git directory:\n  {REPO_ROOT / '.git'}"
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


current_commit = subprocess.run(
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


if current_commit != EXPECTED_COMMIT:
    fail(
        "Repository foundation does not match the verified foundation.\n\n"
        f"Expected:\n  {EXPECTED_COMMIT}\n\n"
        f"Found:\n  {current_commit}\n\n"
        "If you have committed the current working version, "
        "provide that new commit hash before building again."
    )


jsx = JSX_PATH.read_text(encoding="utf-8")
css = CSS_PATH.read_text(encoding="utf-8")


print("Foundation verified:")
print(f"  {EXPECTED_COMMIT}")


# ============================================================
# Verify the successful UI-cleanup working state
# ============================================================

for marker, description in [
    (
        "continuity-phase-status-control",
        "the existing phase status control",
    ),
    (
        "continuity-phase-title",
        "the phase title",
    ),
    (
        "const cyclePhaseState =",
        "the existing phase status helper",
    ),
]:
    if marker not in jsx:
        fail(
            f"Could not locate {description}.\n\n"
            f"Expected marker:\n  {marker}\n\n"
            "No changes were made."
        )


if jsx.count("continuity-phase-status-control") != 1:
    fail(
        "Expected exactly one existing phase status control."
    )


if jsx.count("const cyclePhaseState =") != 1:
    fail(
        "Expected exactly one cyclePhaseState helper."
    )


# ============================================================
# 1. Locate the existing status button
#
# We find the class marker, then walk backward to the button
# opening and forward to that button's closing tag.
#
# This intentionally does NOT depend on whitespace or the
# precise formatting of the JSX expression.
# ============================================================

status_marker = "continuity-phase-status-control"

status_marker_pos = find_unique(
    jsx,
    status_marker,
    "the existing phase status indicator",
)

button_start = jsx.rfind(
    "<button",
    0,
    status_marker_pos,
)

if button_start == -1:
    fail(
        "Found the phase status class, but could not locate "
        "its containing <button>."
    )


button_end = jsx.find(
    "</button>",
    status_marker_pos,
)

if button_end == -1:
    fail(
        "Found the phase status button opening, but could not "
        "locate its closing </button>."
    )

button_end += len("</button>")


existing_status_button = jsx[
    button_start:button_end
]


# Make absolutely sure we're replacing the intended element.
if "continuity-phase-status-control" not in existing_status_button:
    fail(
        "The located button does not contain the expected "
        "Continuity phase status class."
    )


# ============================================================
# 2. Replace the status button with a passive indicator
# ============================================================

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


jsx = (
    jsx[:button_start]
    + status_indicator
    + jsx[button_end:]
)


# ============================================================
# 3. Locate the phase title block
#
# This block has no nested <div>, so its first closing </div>
# is its own closing tag.
# ============================================================

title_marker = '<div className="continuity-phase-title">'

title_start = find_unique(
    jsx,
    title_marker,
    "the phase title block",
)

title_end = jsx.find(
    "</div>",
    title_start,
)

if title_end == -1:
    fail(
        "Found the phase title block but could not locate "
        "its closing </div>."
    )

title_end += len("</div>")


# ============================================================
# 4. Add separate Active / Complete controls
# ============================================================

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


jsx = (
    jsx[:title_end]
    + controls
    + jsx[title_end:]
)


# ============================================================
# 5. Verify the redundant numeric indicator is absent
#
# The previous successful cleanup should already have removed
# the standalone {index + 1} phase number.
# ============================================================

if "{index + 1}" in jsx:
    fail(
        "The redundant standalone phase number is still present.\n\n"
        "No changes were made."
    )


# ============================================================
# 6. CSS
# ============================================================

css_marker = "/* CONTINUITY PHASE CONTROLS REFINEMENT */"

if css_marker in css:
    fail(
        "The phase-controls refinement CSS already exists.\n\n"
        "Refusing to add it twice."
    )


css_addition = r"""

/* ============================================================
   CONTINUITY PHASE CONTROLS REFINEMENT
   ============================================================ */

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

.continuity-phase-status-controls {
    display: flex;
    align-items: center;
    gap: 7px;
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
"""

css += css_addition


# ============================================================
# PRE-WRITE SAFETY CHECKS
# ============================================================

if "continuity-phase-status-control" in jsx:
    fail(
        "The old clickable phase status control remains."
    )

if "continuity-phase-status-indicator" not in jsx:
    fail(
        "The new passive phase status indicator was not created."
    )

if jsx.count("continuity-phase-status-controls") != 1:
    fail(
        "Expected exactly one Active/Complete controls container."
    )

if jsx.count('type="checkbox"') != 2:
    fail(
        "Expected exactly two phase status checkboxes."
    )

if jsx.count("onPhaseStateChange") < 2:
    fail(
        "Expected both Active and Complete controls to use "
        "the existing phase-state handler."
    )

if "{index + 1}" in jsx:
    fail(
        "The redundant standalone phase number remains."
    )

if jsx.count("export default ContinuityViewer;") != 1:
    fail(
        "Expected exactly one ContinuityViewer default export."
    )


# ============================================================
# Backups
# ============================================================

jsx_backup = backup(
    JSX_PATH,
    "phase-controls-refinement",
)

css_backup = backup(
    CSS_PATH,
    "phase-controls-refinement",
)


# ============================================================
# Write
# ============================================================

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


# ============================================================
# Final verification
# ============================================================

final_jsx = JSX_PATH.read_text(encoding="utf-8")
final_css = CSS_PATH.read_text(encoding="utf-8")

if "continuity-phase-status-indicator" not in final_jsx:
    fail(
        "Final verification failed: status indicator missing."
    )

if "continuity-phase-status-control" in final_jsx:
    fail(
        "Final verification failed: old status button remains."
    )

if final_jsx.count("continuity-phase-status-controls") != 1:
    fail(
        "Final verification failed: controls container count "
        "is incorrect."
    )

if final_jsx.count('type="checkbox"') != 2:
    fail(
        "Final verification failed: expected two checkboxes."
    )

if "{index + 1}" in final_jsx:
    fail(
        "Final verification failed: redundant phase number remains."
    )

if final_jsx.count("export default ContinuityViewer;") != 1:
    fail(
        "Final verification failed: default export count is incorrect."
    )

if css_marker not in final_css:
    fail(
        "Final verification failed: CSS refinement is missing."
    )


print()
print("SUCCESS")
print("-------")
print("Continuity Viewer phase controls refined.")

print()
print("Implemented:")
print("  - Leftmost status indicator is now informational.")
print("  - Separate Active control restored.")
print("  - Separate Complete control restored.")
print("  - Neither is represented by both controls being unchecked.")
print("  - Existing phase-state handler remains in use.")
print("  - Existing persistence remains in use.")
print("  - Existing mutual exclusion remains in use.")
print("  - Redundant standalone phase numbering removed.")
print("  - Phase titles still display Phase 1, Phase 2, etc.")

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