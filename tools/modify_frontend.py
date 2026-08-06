from pathlib import Path
import shutil
import sys


# ============================================================
# Helpers
# ============================================================

def fail(message):
    print()
    print("ERROR")
    print("-----")
    print(message)
    print()
    print("No further changes were made by this script.")
    sys.exit(1)


def ensure_exists(path, description):
    if not path.exists():
        fail(
            f"Expected {description} does not exist:\n"
            f"  {path}"
        )


def is_empty_directory(path):
    return path.exists() and path.is_dir() and not any(path.iterdir())


def backup_file(path, backup_root, project_root):
    if not path.exists() or not path.is_file():
        return

    relative = path.relative_to(project_root)
    destination = backup_root / relative

    if destination.exists():
        return

    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(path, destination)


def safe_move_directory_contents(source, destination):
    """
    Safely move contents from source into destination.

    The destination is allowed to already exist if it is empty.
    Existing files are never overwritten.
    """

    if not source.exists():
        return

    if not source.is_dir():
        fail(
            "Expected directory but found something else:\n"
            f"  {source}"
        )

    destination.mkdir(parents=True, exist_ok=True)

    for item in list(source.iterdir()):
        target = destination / item.name

        if target.exists():
            fail(
                "Destination collision detected:\n"
                f"  Source:      {item}\n"
                f"  Destination: {target}\n\n"
                "The script will not overwrite either file."
            )

        shutil.move(str(item), str(target))


def safe_move_file(source, destination):
    if not source.exists():
        return

    if destination.exists():
        fail(
            "Destination file already exists:\n"
            f"  Source:      {source}\n"
            f"  Destination: {destination}\n\n"
            "The script will not overwrite it."
        )

    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(source), str(destination))


def replace_required(text, old, new, filename):
    if old not in text:
        fail(
            f"Could not find the expected code in:\n"
            f"  {filename}\n\n"
            f"Expected:\n{old}"
        )

    return text.replace(old, new, 1)


# ============================================================
# Main
# ============================================================

def main():

    project_root = Path(__file__).resolve().parent.parent

    frontend = project_root / "frontend"
    src = frontend / "src"

    if not src.exists():
        fail(
            "Could not locate frontend/src.\n\n"
            f"Expected:\n  {src}"
        )

    print("WebApp-2 Core / Instance Architecture")
    print("======================================")
    print()
    print(f"Project root:")
    print(f"  {project_root}")
    print()

    # --------------------------------------------------------
    # Expected current state
    # --------------------------------------------------------

    core = src / "core"
    core_components = core / "components"
    instance = src / "instance"

    ensure_exists(core / "App.jsx", "core/App.jsx")

    ensure_exists(
        core_components / "home" / "Home.jsx",
        "core/components/home/Home.jsx"
    )

    ensure_exists(
        core_components / "home" / "Launcher.jsx",
        "core/components/home/Launcher.jsx"
    )

    ensure_exists(
        core_components / "home" / "LauncherCard.jsx",
        "core/components/home/LauncherCard.jsx"
    )

    ensure_exists(
        core_components / "settings" / "Settings.jsx",
        "core/components/settings/Settings.jsx"
    )

    ensure_exists(
        core_components / "settings" / "ModuleSettings.jsx",
        "core/components/settings/ModuleSettings.jsx"
    )

    ensure_exists(
        src / "audio" / "audioManager.js",
        "src/audio/audioManager.js"
    )

    ensure_exists(
        src / "modules" / "package-manager",
        "src/modules/package-manager"
    )

    ensure_exists(
        src / "styles.css",
        "src/styles.css"
    )

    ensure_exists(
        src / "main.jsx",
        "src/main.jsx"
    )

    instance.mkdir(parents=True, exist_ok=True)

    # --------------------------------------------------------
    # Backup current files that will be changed
    # --------------------------------------------------------

    backup_root = (
        project_root
        / "backups"
        / "core-instance-architecture"
    )

    backup_root.mkdir(parents=True, exist_ok=True)

    print("Creating safety backups...")

    files_to_backup = [
        core / "App.jsx",
        core_components / "home" / "Home.jsx",
        core_components / "home" / "Launcher.jsx",
        core_components / "home" / "LauncherCard.jsx",
        core_components / "settings" / "Settings.jsx",
        core_components / "settings" / "ModuleSettings.jsx",
        src / "main.jsx",
        src / "styles.css",
        src / "audio" / "audioManager.js",
    ]

    for path in files_to_backup:
        backup_file(
            path,
            backup_root,
            project_root
        )

    print(f"Backup location:")
    print(f"  {backup_root}")
    print()

    # --------------------------------------------------------
    # Move Audio into Core
    # --------------------------------------------------------

    print("Moving generic audio infrastructure...")

    core_audio = core / "audio"
    core_audio.mkdir(parents=True, exist_ok=True)

    safe_move_directory_contents(
        src / "audio",
        core_audio
    )

    # --------------------------------------------------------
    # Move Package Manager into Core
    # --------------------------------------------------------

    print("Moving generic package-manager infrastructure...")

    core_modules = core / "modules"
    core_modules.mkdir(parents=True, exist_ok=True)

    package_manager_destination = (
        core_modules / "package-manager"
    )

    if package_manager_destination.exists():
        if not is_empty_directory(package_manager_destination):
            fail(
                "Core package-manager destination already contains "
                "files:\n"
                f"  {package_manager_destination}\n\n"
                "Refusing to overwrite it."
            )

    safe_move_directory_contents(
        src / "modules" / "package-manager",
        package_manager_destination
    )

    # Remove empty old module directory if possible.
    old_package_manager = src / "modules" / "package-manager"

    try:
        old_package_manager.rmdir()
    except OSError:
        pass

    try:
        (src / "modules").rmdir()
    except OSError:
        pass

    # --------------------------------------------------------
    # Move stylesheet into Core
    # --------------------------------------------------------

    print("Moving generic stylesheet...")

    safe_move_file(
        src / "styles.css",
        core / "styles.css"
    )

    # --------------------------------------------------------
    # Create instance-local module registry
    # --------------------------------------------------------

    registry = instance / "moduleRegistry.js"

    if registry.exists():
        print("Preserving existing instance/moduleRegistry.js")
    else:
        print("Creating instance/moduleRegistry.js")

        registry.write_text(
            """/*
 * WebApp-2 Instance Module Registry
 *
 * This file represents the installed/configured software
 * belonging to this particular WebApp-2 instance.
 *
 * It is NOT part of WebApp-2 core.
 */

const STORAGE_KEY = 'webapp2-instance-modules';

export function loadInstalledModules() {
    try {
        const saved = localStorage.getItem(STORAGE_KEY);

        if (!saved) {
            return [];
        }

        const parsed = JSON.parse(saved);

        return Array.isArray(parsed)
            ? parsed
            : [];
    } catch {
        return [];
    }
}

export function saveInstalledModules(modules) {
    localStorage.setItem(
        STORAGE_KEY,
        JSON.stringify(modules)
    );
}
""",
            encoding="utf-8"
        )

    # --------------------------------------------------------
    # Create instance-local preferences
    # --------------------------------------------------------

    preferences = instance / "preferences.js"

    if preferences.exists():
        print("Preserving existing instance/preferences.js")
    else:
        print("Creating instance/preferences.js")

        preferences.write_text(
            """/*
 * WebApp-2 Instance Preferences
 *
 * Preferences belong to the individual WebApp-2 instance.
 */

const PREFIX = 'webapp2-instance:';

export function loadPreference(key, fallback = null) {
    const value = localStorage.getItem(
        PREFIX + key
    );

    return value === null
        ? fallback
        : value;
}

export function savePreference(key, value) {
    localStorage.setItem(
        PREFIX + key,
        String(value)
    );
}
""",
            encoding="utf-8"
        )

    # --------------------------------------------------------
    # Update main.jsx
    # --------------------------------------------------------

    print("Updating main.jsx...")

    main = src / "main.jsx"
    main_text = main.read_text(encoding="utf-8")

    if "from './core/App'" not in main_text:
        main_text = main_text.replace(
            "from './components/App'",
            "from './core/App'"
        )

    if "from './core/styles.css'" not in main_text:
        main_text = main_text.replace(
            "import './styles.css'",
            "import './core/styles.css'"
        )

    main.write_text(
        main_text,
        encoding="utf-8"
    )

    # --------------------------------------------------------
    # Update App.jsx path references
    # --------------------------------------------------------

    print("Checking core/App.jsx imports...")

    app = core / "App.jsx"
    app_text = app.read_text(encoding="utf-8")

    # Because App.jsx now lives in core/, paths to the core
    # component tree should be ./components/...
    replacements = {
        "./home/Home": "./components/home/Home",
        "./settings/Settings": "./components/settings/Settings",
        "./audio/audioManager": "./audio/audioManager",
        "./modules/package-manager": "./modules/package-manager",
    }

    for old, new in replacements.items():
        app_text = app_text.replace(old, new)

    app.write_text(
        app_text,
        encoding="utf-8"
    )

    # --------------------------------------------------------
    # Update imports inside moved components
    # --------------------------------------------------------

    moved_files = list(core_components.rglob("*.jsx"))

    for file in moved_files:
        text = file.read_text(encoding="utf-8")

        # These are conservative path corrections only.
        # We do not rewrite arbitrary imports.

        text = text.replace(
            "../home/",
            "../home/"
        )

        text = text.replace(
            "../settings/",
            "../settings/"
        )

        file.write_text(
            text,
            encoding="utf-8"
        )

    # --------------------------------------------------------
    # Verify resulting structure
    # --------------------------------------------------------

    print()
    print("Verifying architecture...")
    print()

    expected_paths = [
        core / "App.jsx",
        core / "styles.css",
        core / "audio" / "audioManager.js",
        core / "modules" / "package-manager",
        core_components / "home" / "Home.jsx",
        core_components / "home" / "Launcher.jsx",
        core_components / "home" / "LauncherCard.jsx",
        core_components / "settings" / "Settings.jsx",
        core_components / "settings" / "ModuleSettings.jsx",
        instance / "moduleRegistry.js",
        instance / "preferences.js",
        src / "main.jsx",
    ]

    for path in expected_paths:
        if not path.exists():
            fail(
                "Architecture verification failed.\n\n"
                f"Missing:\n  {path}"
            )

    # Verify old application directories are gone.
    old_audio = src / "audio"
    old_modules = src / "modules"

    if old_audio.exists() and any(old_audio.iterdir()):
        fail(
            "Old audio directory still contains files:\n"
            f"  {old_audio}"
        )

    if old_modules.exists() and any(old_modules.iterdir()):
        fail(
            "Old modules directory still contains files:\n"
            f"  {old_modules}"
        )

    # --------------------------------------------------------
    # Final report
    # --------------------------------------------------------

    print("SUCCESS")
    print("=======")
    print()
    print("Core / Instance architecture has been established.")
    print()
    print("CORE")
    print("----")
    print("frontend/src/core/")
    print("  App.jsx")
    print("  styles.css")
    print("  audio/")
    print("  components/")
    print("  modules/")
    print()
    print("INSTANCE")
    print("--------")
    print("frontend/src/instance/")
    print("  moduleRegistry.js")
    print("  preferences.js")
    print()
    print("INSTANCE SOFTWARE")
    print("-----------------")
    print(
        "Future user-installed modules belong to the "
        "instance layer."
    )
    print()
    print("PACKAGE MANAGER")
    print("---------------")
    print(
        "The package-manager capability remains Core; "
        "future installed software remains instance-local."
    )
    print()
    print("IMPORTANT:")
    print("Test the application before committing.")
    print("Do not commit yet.")


if __name__ == "__main__":
    main()