from pathlib import Path
import re
import shutil
import subprocess
import sys


# ============================================================
# WebApp-2
# Phase 2 — LauncherCard repair
#
# Repairs the specific state where:
#
#     onClick={onClick}
#
# exists inside LauncherCard, but `onClick` is missing from
# the component's destructured props.
#
# No other carousel behavior is changed.
# ============================================================


ROOT = Path.cwd()

LAUNCHER_CARD = (
    ROOT
    / "frontend"
    / "src"
    / "components"
    / "home"
    / "LauncherCard.jsx"
)


def fail(message):
    print()
    print("ERROR")
    print("-----")
    print(message)
    print()
    sys.exit(1)


def get_commit():
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            cwd=ROOT,
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except Exception:
        return None


def verify_project():
    if not LAUNCHER_CARD.exists():
        fail(
            "LauncherCard.jsx was not found:\n\n"
            f"{LAUNCHER_CARD}\n\n"
            "Run this script from the WebApp-2 repository root."
        )


def create_backup():
    backup = LAUNCHER_CARD.with_name(
        "LauncherCard.jsx.pre-onclick-repair"
    )

    if backup.exists():
        fail(
            "A repair backup already exists:\n\n"
            f"{backup}\n\n"
            "The script will not overwrite it."
        )

    shutil.copy2(
        LAUNCHER_CARD,
        backup
    )

    print("Backup created:")
    print(f"  {backup}")

    return backup


def repair():
    source = LAUNCHER_CARD.read_text(
        encoding="utf-8"
    )


    # --------------------------------------------------------
    # First determine whether the problem actually exists.
    # --------------------------------------------------------

    has_click_handler = (
        "onClick={onClick}" in source
    )

    if not has_click_handler:
        fail(
            "LauncherCard.jsx does not contain "
            "`onClick={onClick}`.\n\n"
            "This repair is therefore not applicable."
        )


    # --------------------------------------------------------
    # Find the LauncherCard function declaration.
    #
    # This deliberately allows whitespace/newlines so that
    # formatting changes don't break the repair.
    # --------------------------------------------------------

    pattern = re.compile(
        r"""
        function
        \s+
        LauncherCard
        \s*
        \(
        \s*
        \{
        (?P<props>.*?)
        \}
        \s*
        \)
        """,
        re.DOTALL | re.VERBOSE,
    )


    match = pattern.search(source)

    if not match:
        fail(
            "Could not safely locate the LauncherCard "
            "function declaration.\n\n"
            "No files were changed."
        )


    props = match.group("props")


    # --------------------------------------------------------
    # If onClick is already declared, the JavaScript source
    # itself is not the problem.
    # --------------------------------------------------------

    if re.search(
        r"\bonClick\b",
        props
    ):
        print()
        print(
            "LauncherCard already declares onClick "
            "in its props."
        )
        print()
        print(
            "The reported browser error may be coming "
            "from a stale Vite/HMR module."
        )
        print()
        return False


    # --------------------------------------------------------
    # Preserve the existing props and append onClick.
    # --------------------------------------------------------

    cleaned_props = props.strip()


    if cleaned_props:
        new_props = (
            cleaned_props.rstrip()
            + ", onClick"
        )
    else:
        new_props = "onClick"


    replacement = (
        "function LauncherCard({ "
        + new_props
        + " })"
    )


    updated = (
        source[:match.start()]
        + replacement
        + source[match.end():]
    )


    # --------------------------------------------------------
    # Verify BEFORE writing.
    # --------------------------------------------------------

    verification = re.search(
        r"""
        function
        \s+
        LauncherCard
        \s*
        \(
        \s*
        \{
        (?P<props>.*?\bonClick\b.*?)
        \}
        \s*
        \)
        """,
        updated,
        re.DOTALL | re.VERBOSE,
    )


    if not verification:
        fail(
            "The repair could not be verified before "
            "writing the file.\n\n"
            "No files were changed."
        )


    # Make sure the click handler still exists too.
    if "onClick={onClick}" not in updated:
        fail(
            "The resulting file does not contain the "
            "expected click handler.\n\n"
            "No files were changed."
        )


    LAUNCHER_CARD.write_text(
        updated,
        encoding="utf-8"
    )

    return True


def main():

    print()
    print("==============================================")
    print(" WebApp-2")
    print(" LauncherCard onClick Repair")
    print("==============================================")
    print()

    verify_project()

    commit = get_commit()

    if commit:
        print(f"Current commit: {commit}")

    print()

    backup = create_backup()

    try:
        changed = repair()

    except Exception as error:

        print()
        print(
            "Repair failed. Restoring backup..."
        )

        shutil.copy2(
            backup,
            LAUNCHER_CARD
        )

        fail(
            f"Repair was rolled back.\n\n{error}"
        )


    if not changed:
        return


    print()
    print("==============================================")
    print(" REPAIR COMPLETE")
    print("==============================================")
    print()
    print(
        "LauncherCard now receives `onClick` "
        "through its component props."
    )
    print()
    print(
        "The specific `onClick is not defined` "
        "ReferenceError has been repaired."
    )
    print()
    print(
        "Refresh the browser and test the homepage."
    )
    print()


if __name__ == "__main__":
    main()