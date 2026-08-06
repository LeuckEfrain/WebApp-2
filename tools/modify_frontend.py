from pathlib import Path
import shutil
import subprocess
import sys
from datetime import datetime


EXPECTED_COMMIT = "660f2015a58b1914a42ff30202d54d05dbabca80"
APP_RELATIVE = Path("frontend/src/core/App.jsx")


def fail(message):
    print("ERROR")
    print("-----")
    print(message)
    print()
    print("No changes were made.")
    sys.exit(1)


def find_repo():
    script_dir = Path(__file__).resolve().parent

    for directory in [script_dir, *script_dir.parents]:
        if (directory / ".git").is_dir():
            return directory

    fail("Could not locate the WebApp-2 Git repository.")


def get_commit(repo):
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=repo,
            capture_output=True,
            text=True,
            check=True,
        )
    except Exception as exc:
        fail(
            "Could not determine the current Git commit:\n"
            f"{exc}"
        )

    return result.stdout.strip()


def make_backup(path):
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")

    backup = path.with_name(
        f"{path.name}.pre-continuity-launcher-fix-{timestamp}"
    )

    if backup.exists():
        fail(
            "Refusing to overwrite an existing backup:\n"
            f"{backup}"
        )

    shutil.copy2(path, backup)
    return backup


def main():
    repo = find_repo()

    actual_commit = get_commit(repo)

    if actual_commit != EXPECTED_COMMIT:
        fail(
            "Git foundation mismatch.\n\n"
            f"Expected:\n  {EXPECTED_COMMIT}\n\n"
            f"Found:\n  {actual_commit}\n\n"
            "Refusing to guess the correct foundation."
        )

    app = repo / APP_RELATIVE

    if not app.exists():
        fail(
            "Required file does not exist:\n"
            f"{app}"
        )

    source = app.read_text(encoding="utf-8")

    start_marker = "const [modules, setModules] = useState(() => {"

    start = source.find(start_marker)

    if start == -1:
        fail(
            "Could not locate the modules state initializer in App.jsx."
        )

    # The initializer is immediately followed by the theme state.
    # Use that as the structural endpoint instead of depending
    # on whitespace or exact indentation.
    end_marker = "const [theme, setTheme] = useState(() => ("

    end = source.find(end_marker, start)

    if end == -1:
        fail(
            "Could not locate the end boundary of the modules "
            "state initializer."
        )

    original_block = source[start:end]

    if "localStorage.getItem('home-modules')" not in original_block:
        fail(
            "The located modules initializer does not contain the "
            "expected home-modules localStorage state."
        )

    if "return DEFAULT_HOME_MODULES;" not in original_block:
        fail(
            "The located modules initializer does not contain the "
            "expected DEFAULT_HOME_MODULES fallback."
        )

    if "registeredModules" in original_block:
        fail(
            "Instance-module integration already appears to exist "
            "inside the modules initializer."
        )

    replacement = """const [modules, setModules] = useState(() => {

        const registeredModules =
            getInstanceModuleDefinitions().map(module => ({
                id: module.id,
                name: module.name,
                icon: module.icon,
                enabled: true
            }));

        try {
            const saved =
                localStorage.getItem('home-modules');

            if (saved) {

                const savedModules =
                    JSON.parse(saved);

                if (Array.isArray(savedModules)) {

                    const mergedModules =
                        [...savedModules];

                    registeredModules.forEach(
                        instanceModule => {

                            const exists =
                                mergedModules.some(
                                    module =>
                                        module.id ===
                                        instanceModule.id
                                );

                            if (!exists) {
                                mergedModules.push(
                                    instanceModule
                                );
                            }
                        }
                    );

                    return mergedModules;
                }
            }

        } catch {
            // Fall back to defaults plus
            // registered instance modules.
        }

        const mergedDefaults =
            [...DEFAULT_HOME_MODULES];

        registeredModules.forEach(
            instanceModule => {

                const exists =
                    mergedDefaults.some(
                        module =>
                            module.id ===
                            instanceModule.id
                    );

                if (!exists) {
                    mergedDefaults.push(
                        instanceModule
                    );
                }
            }
        );

        return mergedDefaults;

    });


    """

    updated = source[:start] + replacement + source[end:]

    if updated == source:
        fail("The modification produced no changes.")

    backup = make_backup(app)

    try:
        app.write_text(updated, encoding="utf-8")

        verification = app.read_text(encoding="utf-8")

        required_after_write = [
            "const registeredModules =",
            "getInstanceModuleDefinitions().map",
            "const mergedModules =",
            "return mergedModules;",
            "const mergedDefaults =",
        ]

        missing = [
            marker
            for marker in required_after_write
            if marker not in verification
        ]

        if missing:
            raise RuntimeError(
                "Missing expected post-change structures:\n"
                + "\n".join(f"  - {item}" for item in missing)
            )

    except Exception as exc:
        shutil.copy2(backup, app)

        fail(
            "Post-write verification failed.\n"
            f"Reason: {exc}\n\n"
            "The original App.jsx was restored from backup."
        )

    print("SUCCESS")
    print("-------")
    print("Continuity Viewer launcher integration repaired.")
    print()
    print("Foundation verified:")
    print(f"  {EXPECTED_COMMIT}")
    print()
    print("Modified:")
    print(f"  {app}")
    print()
    print("Behavior:")
    print("  - Registered instance modules are discovered.")
    print("  - Registered modules are merged into Home modules.")
    print("  - Existing localStorage modules are preserved.")
    print("  - Existing modules are not duplicated.")
    print("  - Continuity Viewer should now appear in the launcher.")
    print("  - Future instance modules can use the same mechanism.")
    print()
    print("Backup:")
    print(f"  {backup}")
    print()
    print("WebApp-2 source code was modified successfully.")


if __name__ == "__main__":
    main()