from pathlib import Path
import shutil
import sys
from datetime import datetime


EXPECTED_COMMIT = "5c21bf934d84ae3badf380d4c9bc4955ab9b796b"

SCROLLABLE_CSS = r'''
/* =========================================================
   UNIVERSAL SCROLLABLE COLLECTIONS

   Any UI collection that may contain an indefinite number
   of items should use .indefinite-list.

   The collection remains visually bounded while all items
   remain accessible through internal scrolling.
   ========================================================= */

.indefinite-list {
    max-height: 420px;
    overflow-y: auto;
    overflow-x: hidden;
    min-height: 0;
    scrollbar-width: thin;
    scrollbar-color: var(--theme-border-strong) transparent;
}

.indefinite-list::-webkit-scrollbar {
    width: 7px;
}

.indefinite-list::-webkit-scrollbar-track {
    background: transparent;
}

.indefinite-list::-webkit-scrollbar-thumb {
    background: var(--theme-border-strong);
    border-radius: 999px;
}

.indefinite-list::-webkit-scrollbar-thumb:hover {
    background: var(--theme-text-muted);
}

/*
 * Lists that are nested inside a bounded panel should not
 * cause the panel itself to grow indefinitely.
 */
.panel .indefinite-list {
    min-height: 0;
}

/*
 * Existing Software Inventory already uses a bounded
 * <pre>. Keep its established behavior intact.
 */
pre {
    max-height: 480px;
    overflow: auto;
}
'''


def fail(message):
    print("\nERROR")
    print("-----")
    print(message)
    print("\nNo changes were made.")
    sys.exit(1)


def find_repo_root():
    """
    Locate the WebApp-2 repository from this script's location.

    This intentionally does not depend on the process's current
    working directory. The script can therefore be launched from
    another directory as long as the script itself is inside the
    repository.
    """
    script_path = Path(__file__).resolve()

    for candidate in [script_path.parent, *script_path.parents]:
        if (
            (candidate / ".git").exists()
            and (candidate / "frontend" / "src" / "core").is_dir()
            and (candidate / "frontend" / "src" / "instance").is_dir()
        ):
            return candidate

    fail(
        "Could not locate the WebApp-2 repository from the script location.\n"
        "\n"
        "Place modify_frontend.py somewhere inside:\n"
        "D:\\Projects\\WebApps\\webapp_2\n"
        "\n"
        "The repository must contain frontend\\src\\core and "
        "frontend\\src\\instance."
    )


def read_text(path):
    try:
        return path.read_text(encoding="utf-8")
    except Exception as exc:
        fail(f"Could not read:\n{path}\n\n{exc}")


def backup(path, tag):
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup_path = path.with_name(
        f"{path.name}.pre-{tag}-{timestamp}"
    )

    if backup_path.exists():
        fail(
            "Backup already exists and will not be overwritten:\n"
            f"{backup_path}"
        )

    shutil.copy2(path, backup_path)
    return backup_path


def write_verified(path, original, updated):
    if original == updated:
        fail(f"No change was produced for:\n{path}")

    path.write_text(updated, encoding="utf-8")

    written = read_text(path)

    if written != updated:
        fail(
            "Verification failed after writing:\n"
            f"{path}"
        )


def add_css_once(css_path):
    original = read_text(css_path)

    marker = "UNIVERSAL SCROLLABLE COLLECTIONS"

    if marker in original:
        return False, None

    updated = original.rstrip() + "\n\n" + SCROLLABLE_CSS.strip() + "\n"

    backup_path = backup(css_path, "indefinite-scroll")
    write_verified(css_path, original, updated)

    return True, backup_path


def add_class_once(path, old, new, description):
    original = read_text(path)

    count = original.count(old)

    if count == 0:
        fail(
            f"Could not locate the expected foundation for {description}.\n"
            f"File: {path}\n"
            f"Expected text: {old!r}"
        )

    if count > 1:
        fail(
            f"Expected exactly one foundation occurrence for {description}, "
            f"but found {count}.\n"
            f"File: {path}"
        )

    if new in original:
        return False, None

    updated = original.replace(old, new, 1)

    backup_path = backup(path, "indefinite-scroll")
    write_verified(path, original, updated)

    return True, backup_path


def verify_git_foundation(repo):
    """
    Verify the repository is actually on the requested foundation when
    Git is available. This is deliberately conservative.
    """
    import subprocess

    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=repo,
            capture_output=True,
            text=True,
            check=True,
        )
    except Exception:
        # Git verification is useful but shouldn't make the script
        # impossible to run in a repository where Git is unavailable.
        return None

    head = result.stdout.strip()

    if head != EXPECTED_COMMIT:
        fail(
            "The repository HEAD does not match the supplied foundation.\n\n"
            f"Expected:\n{EXPECTED_COMMIT}\n\n"
            f"Found:\n{head}\n\n"
            "The repository may have changed since the verified "
            "foundation.\n"
            "No changes were made."
        )

    return head


def main():
    print("WebApp-2 indefinite-list scrolling update")
    print("------------------------------------------")

    repo = find_repo_root()

    print(f"Repository:\n  {repo}")

    verified_commit = verify_git_foundation(repo)

    if verified_commit:
        print(f"Foundation:\n  {verified_commit}")
    else:
        print("Foundation:\n  Git verification unavailable")

    frontend = repo / "frontend" / "src"

    styles = frontend / "core" / "styles.css"
    package_search = (
        frontend
        / "core"
        / "modules"
        / "package-manager"
        / "components"
        / "PackageSearch.jsx"
    )
    continuity = (
        frontend
        / "instance"
        / "modules"
        / "continuity-viewer"
        / "ContinuityViewer.jsx"
    )

    required = [
        styles,
        package_search,
        continuity,
    ]

    for path in required:
        if not path.exists():
            fail(f"Required file does not exist:\n{path}")

    backups = []
    changes = []

    # ---------------------------------------------------------
    # 1. Add universal scrollable-list styling.
    # ---------------------------------------------------------

    changed, backup_path = add_css_once(styles)

    if changed:
        changes.append(str(styles))
        backups.append(str(backup_path))

    # ---------------------------------------------------------
    # 2. Package search results.
    #
    # Search results can contain an arbitrarily large number
    # of packages. The results collection should scroll inside
    # the Package Search panel rather than growing the panel.
    # ---------------------------------------------------------

    changed, backup_path = add_class_once(
        package_search,
        '<div className="package-results">',
        '<div className="package-results indefinite-list">',
        "Package Search result collection",
    )

    if changed:
        changes.append(str(package_search))
        backups.append(str(backup_path))

    # ---------------------------------------------------------
    # 3. Continuity Viewer.
    #
    # The Continuity document will grow over time. Each section
    # should remain bounded when its collection becomes large.
    # ---------------------------------------------------------

    original = read_text(continuity)

    replacements = [
        (
            '<div className="continuity-section-body">',
            '<div className="continuity-section-body indefinite-list">',
            "Continuity section body",
        ),
        (
            '<div className="continuity-phase-list">',
            '<div className="continuity-phase-list indefinite-list">',
            "Continuity phase list",
        ),
    ]

    continuity_updated = original
    replacement_count = 0

    for old, new, description in replacements:
        count = continuity_updated.count(old)

        if count == 0:
            # A section may not exist in a future foundation. Since
            # this foundation is verified, treat this as a safety
            # failure rather than guessing.
            fail(
                f"Could not locate the expected foundation for "
                f"{description}.\n"
                f"File: {continuity}"
            )

        if count > 1:
            fail(
                f"Expected exactly one occurrence for {description}, "
                f"but found {count}.\n"
                f"File: {continuity}"
            )

        if new not in continuity_updated:
            continuity_updated = continuity_updated.replace(
                old,
                new,
                1,
            )
            replacement_count += 1

    if replacement_count:
        backup_path = backup(continuity, "indefinite-scroll")
        write_verified(
            continuity,
            original,
            continuity_updated,
        )
        changes.append(str(continuity))
        backups.append(str(backup_path))

    # ---------------------------------------------------------
    # Final verification.
    # ---------------------------------------------------------

    css_final = read_text(styles)

    if "UNIVERSAL SCROLLABLE COLLECTIONS" not in css_final:
        fail("Universal scrollable-list CSS could not be verified.")

    package_final = read_text(package_search)

    if '<div className="package-results indefinite-list">' not in package_final:
        fail("Package Search scroll container could not be verified.")

    continuity_final = read_text(continuity)

    if (
        '<div className="continuity-section-body indefinite-list">'
        not in continuity_final
    ):
        fail("Continuity section scrolling could not be verified.")

    if (
        '<div className="continuity-phase-list indefinite-list">'
        not in continuity_final
    ):
        fail("Continuity phase-list scrolling could not be verified.")

    print("\nSUCCESS")
    print("-------")
    print("Universal indefinite-list scrolling support added.")

    print("\nBehavior:")
    print("  - Potentially unbounded collections remain fixed-height.")
    print("  - Items are accessed through internal scrolling.")
    print("  - Package Search results now scroll instead of expanding.")
    print("  - Continuity collections now use the same behavior.")
    print("  - Existing Software Inventory scrolling is preserved.")
    print("  - Future indefinite collections can use:")
    print("      className=\"indefinite-list\"")
    print("  - No items are discarded or artificially limited.")
    print("  - The surrounding panel does not grow indefinitely.")

    if changes:
        print("\nModified:")
        for item in changes:
            print(f"  {item}")

    if backups:
        print("\nBackups:")
        for item in backups:
            print(f"  {item}")

    print("\nWebApp-2 source code was modified successfully.")


if __name__ == "__main__":
    main()