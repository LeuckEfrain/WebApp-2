from pathlib import Path
import shutil
import subprocess
import sys


# ============================================================
# WebApp-2 — One-Time Modularization Script
#
# Foundation:
# e66cd872b4e507238c52e47da35eff32100f3999
#
# Run from:
# WebApp-2/
#
# Purpose:
# Break the monolithic App.jsx into feature-based components
# without changing the application's overall behavior.
# ============================================================


EXPECTED_COMMIT = "e66cd872b4e507238c52e47da35eff32100f3999"

ROOT = Path.cwd()

APP = ROOT / "frontend/src/components/App.jsx"

HOME_DIR = ROOT / "frontend/src/components/home"
SETTINGS_DIR = ROOT / "frontend/src/components/settings"

HOME = HOME_DIR / "Home.jsx"
LAUNCHER = HOME_DIR / "Launcher.jsx"
LAUNCHER_CARD = HOME_DIR / "LauncherCard.jsx"

SETTINGS = SETTINGS_DIR / "Settings.jsx"
MODULE_SETTINGS = SETTINGS_DIR / "ModuleSettings.jsx"

BACKUP = APP.with_name("App.jsx.pre-modularization")


# ============================================================
# Utility functions
# ============================================================

def fail(message):
    print()
    print("ERROR:")
    print(message)
    print()
    sys.exit(1)


def get_git_commit():
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            cwd=ROOT,
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except Exception:
        return None


def ensure_project():
    if not APP.exists():
        fail(
            "App.jsx was not found.\n\n"
            "Run this script from the root of WebApp-2."
        )


def verify_foundation():
    current_commit = get_git_commit()

    if current_commit:
        print(f"Current Git commit: {current_commit}")

        if current_commit != EXPECTED_COMMIT:
            print()
            print("WARNING:")
            print(
                "The current commit does not match the expected "
                "foundation commit."
            )
            print(f"Expected: {EXPECTED_COMMIT}")
            print(f"Current:  {current_commit}")
            print()

            answer = input(
                "Continue anyway? [y/N]: "
            ).strip().lower()

            if answer != "y":
                print("Aborted.")
                sys.exit(0)

    source = APP.read_text(encoding="utf-8")

    required_markers = [
        "function App(",
        "function Home(",
        "function ModuleSettings(",
        "function Settings(",
    ]

    missing = [
        marker
        for marker in required_markers
        if marker not in source
    ]

    if missing:
        fail(
            "The App.jsx structure does not match the expected "
            "foundation.\n\nMissing:\n"
            + "\n".join(missing)
        )

    if (
        "from './home/Home'" in source
        or "from './settings/Settings'" in source
    ):
        fail(
            "App.jsx already appears to be modularized."
        )


def backup_app():
    if BACKUP.exists():
        fail(
            f"A backup already exists:\n{BACKUP}\n\n"
            "This script will not overwrite an existing backup."
        )

    shutil.copy2(APP, BACKUP)

    print(f"Backup created: {BACKUP}")


def write_file(path, content):
    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    path.write_text(
        content.strip() + "\n",
        encoding="utf-8",
    )

    print(f"Created: {path}")


# ============================================================
# Components
# ============================================================

HOME_CONTENT = """
import Launcher from './Launcher';


function Home({ onSettings, modules }) {
    return (
        <div className="home-shell">

            <header className="home-topbar">

                <div className="home-brand">
                    MODULAR
                </div>


                <button
                    type="button"
                    className="settings-button"
                    onClick={onSettings}
                    aria-label="Open Settings"
                >
                    <span className="settings-icon">
                        ⚙
                    </span>

                    <span>
                        Settings
                    </span>
                </button>

            </header>


            <Launcher
                modules={modules}
            />

        </div>
    );
}


export default Home;
"""


LAUNCHER_CONTENT = """
import LauncherCard from './LauncherCard';


function Launcher({ modules }) {

    const enabledModules = modules.filter(
        module => module.enabled
    );


    return (
        <main className="launcher">

            <div className="launcher-row-area">

                <button
                    type="button"
                    className="launcher-axis-arrow"
                    disabled
                    aria-label="Previous row"
                >
                    ▲
                </button>


                <div className="launcher-row">

                    <button
                        type="button"
                        className="launcher-arrow"
                        disabled
                        aria-label="Previous module"
                    >
                        ‹
                    </button>


                    {enabledModules.map(
                        (module, index) => (

                            <LauncherCard
                                key={module.id}
                                module={module}
                                selected={index === 1}
                            />

                        )
                    )}


                    <button
                        type="button"
                        className="launcher-arrow"
                        disabled
                        aria-label="Next module"
                    >
                        ›
                    </button>

                </div>


                <button
                    type="button"
                    className="launcher-axis-arrow"
                    disabled
                    aria-label="Next row"
                >
                    ▼
                </button>

            </div>


            <div className="launcher-selection">

                <span className="launcher-selection-marker" />

                <span>
                    {enabledModules[1]?.name}
                </span>

            </div>

        </main>
    );
}


export default Launcher;
"""


LAUNCHER_CARD_CONTENT = """
function LauncherCard({
    module,
    selected
}) {

    return (
        <div
            className={`launcher-card ${
                selected
                    ? 'launcher-card-selected'
                    : ''
            } ${
                module.placeholder
                    ? 'launcher-card-placeholder'
                    : ''
            }`}
        >

            <div className="launcher-card-icon">
                {module.icon}
            </div>


            <div className="launcher-card-title">
                {module.name}
            </div>


            {!module.placeholder && (

                <div className="launcher-card-subtitle">

                    {module.id === 'gmail-analyzer'
                        ? 'Analyzer'
                        : 'Tools'}

                </div>

            )}

        </div>
    );
}


export default LauncherCard;
"""


# ============================================================
# App.jsx
#
# This intentionally keeps application-wide state here.
# ============================================================

APP_CONTENT = """
import React, {
    useEffect,
    useState
} from 'react';

import Home from './home/Home';
import Settings from './settings/Settings';


const API = 'http://127.0.0.1:8000';


const DEFAULT_HOME_MODULES = [
    {
        id: 'gmail-analyzer',
        name: 'Gmail Analyzer',
        icon: 'G',
        enabled: true
    },
    {
        id: 'git-tools',
        name: 'Git Tools',
        icon: 'G',
        enabled: true
    }
];


function App() {

    const [view, setView] = useState('home');

    const [page, setPage] = useState('dashboard');

    const [managers, setManagers] = useState([]);


    const [modules, setModules] = useState(() => {

        try {

            const saved =
                localStorage.getItem('home-modules');

            if (saved) {
                return JSON.parse(saved);
            }

        } catch {
            // Fall back to defaults.
        }

        return DEFAULT_HOME_MODULES;

    });


    const [theme, setTheme] = useState(() => (
        localStorage.getItem('modular-theme')
        || 'obsidian'
    ));


    const [font, setFont] = useState(() => (
        localStorage.getItem('modular-font')
        || 'inter'
    ));


    useEffect(() => {

        document.documentElement.dataset.theme =
            theme;

        localStorage.setItem(
            'modular-theme',
            theme
        );

    }, [theme]);


    useEffect(() => {

        document.documentElement.dataset.font =
            font;

        localStorage.setItem(
            'modular-font',
            font
        );

    }, [font]);


    useEffect(() => {

        localStorage.setItem(
            'home-modules',
            JSON.stringify(modules)
        );

    }, [modules]);


    useEffect(() => {

        fetch(API + '/api/package-managers')
            .then(response => response.json())
            .then(setManagers)
            .catch(() => {});

    }, []);


    if (view === 'home') {

        return (
            <Home
                onSettings={() =>
                    setView('settings')
                }
                modules={modules}
            />
        );

    }


    return (
        <Settings

            page={page}
            setPage={setPage}

            managers={managers}

            theme={theme}
            setTheme={setTheme}

            font={font}
            setFont={setFont}

            onHome={() =>
                setView('home')
            }

            modules={modules}
            setModules={setModules}

        />
    );
}


export default App;
"""


# ============================================================
# ModuleSettings
#
# IMPORTANT:
# This component is intentionally extracted from the existing
# App.jsx implementation rather than introducing a new data
# model.
# ============================================================

MODULE_SETTINGS_CONTENT = """
function ModuleSettings({
    modules,
    setModules
}) {

    const renameModule = (
        id,
        name
    ) => {

        setModules(current =>
            current.map(module =>
                module.id === id
                    ? {
                        ...module,
                        name
                    }
                    : module
            )
        );

    };


    const toggleModule = (id) => {

        setModules(current =>
            current.map(module =>
                module.id === id
                    ? {
                        ...module,
                        enabled: !module.enabled
                    }
                    : module
            )
        );

    };


    const addModule = () => {

        const id =
            `module-${Date.now()}`;


        const newModule = {

            id,

            name:
                'New Module',

            icon:
                '+',

            enabled:
                true

        };


        setModules(current => [
            ...current,
            newModule
        ]);

    };


    return (
        <section className="module-settings">

            <div className="settings-section-header">

                <div>

                    <div className="eyebrow">
                        HOME
                    </div>

                    <h2>
                        Home Modules
                    </h2>

                </div>


                <p>
                    Rename the applications displayed
                    on the Home screen.
                </p>

            </div>


            <div className="module-settings-list">

                {modules.map(module => (

                    <div
                        className="module-setting"
                        key={module.id}
                    >

                        <div className="module-setting-icon">
                            {module.icon}
                        </div>


                        <div className="module-setting-info">

                            <div className="module-setting-id">
                                {module.id}
                            </div>


                            <label>

                                DISPLAY NAME

                                <input
                                    type="text"
                                    value={module.name}
                                    onChange={event =>
                                        renameModule(
                                            module.id,
                                            event.target.value
                                        )
                                    }
                                />

                            </label>


                            <label className="module-enabled">

                                <input
                                    type="checkbox"
                                    checked={module.enabled}
                                    onChange={() =>
                                        toggleModule(
                                            module.id
                                        )
                                    }
                                />

                                SHOW ON HOME

                            </label>

                        </div>

                    </div>

                ))}

            </div>


            <button
                type="button"
                className="add-module-button"
                onClick={addModule}
            >
                + Add Module
            </button>

        </section>
    );
}


export default ModuleSettings;
"""


# ============================================================
# Settings
# ============================================================

SETTINGS_CONTENT = """
import Nav from '../Nav';
import Dashboard from '../Dashboard';
import PackageManager from '../../modules/package-manager/PackageManager';
import ModuleSettings from './ModuleSettings';


function Settings({
    page,
    setPage,
    managers,
    theme,
    setTheme,
    font,
    setFont,
    onHome,
    modules,
    setModules
}) {

    return (
        <div className="shell">

            <aside className="sidebar">

                <div className="logo">
                    MODULAR
                </div>


                <button
                    type="button"
                    className="settings-home-button"
                    onClick={onHome}
                >
                    ← Home
                </button>


                <div className="label">
                    WORKSPACE
                </div>


                <Nav
                    active={page === 'dashboard'}
                    onClick={() =>
                        setPage('dashboard')
                    }
                >
                    Dashboard
                </Nav>


                <Nav
                    active={page === 'packages'}
                    onClick={() =>
                        setPage('packages')
                    }
                >
                    Package Managers
                </Nav>


                <div className="label lower">
                    SYSTEM
                </div>


                <Nav>
                    Processes
                </Nav>


                <Nav>
                    Environment
                </Nav>


                <div className="label lower">
                    MODULES
                </div>


                <Nav
                    active={page === 'modules'}
                    onClick={() =>
                        setPage('modules')
                    }
                >
                    Modules
                </Nav>


                <div className="label lower">
                    APPEARANCE
                </div>


                <div className="theme-control">

                    <label htmlFor="theme-select">
                        COLOR PALETTE
                    </label>


                    <select
                        id="theme-select"
                        value={theme}
                        onChange={event =>
                            setTheme(
                                event.target.value
                            )
                        }
                    >

                        <option value="obsidian">
                            Obsidian
                        </option>

                        <option value="slate">
                            Slate
                        </option>

                        <option value="forest">
                            Forest
                        </option>

                        <option value="copper">
                            Copper
                        </option>

                    </select>

                </div>


                <div className="theme-control">

                    <label htmlFor="font-select">
                        FONT
                    </label>


                    <select
                        id="font-select"
                        value={font}
                        onChange={event =>
                            setFont(
                                event.target.value
                            )
                        }
                    >

                        <option value="inter">
                            Inter
                        </option>

                        <option value="plex">
                            IBM Plex Sans
                        </option>

                        <option value="jetbrains">
                            JetBrains Mono
                        </option>

                        <option value="source">
                            Source Sans 3
                        </option>

                    </select>

                </div>

            </aside>


            <main className="main">

                <header>

                    <div>

                        <div className="eyebrow">
                            SETTINGS
                        </div>


                        <h1>

                            {page === 'packages'
                                ? 'Package Managers'
                                : page === 'modules'
                                    ? 'Modules'
                                    : 'Dashboard'}

                        </h1>

                    </div>


                    <div className="online">
                        <i />
                        BACKEND ONLINE
                    </div>

                </header>


                {page === 'dashboard' ? (

                    <Dashboard
                        managers={managers}
                        open={() =>
                            setPage('packages')
                        }
                    />

                ) : page === 'packages' ? (

                    <PackageManager
                        managers={managers}
                    />

                ) : (

                    <ModuleSettings
                        modules={modules}
                        setModules={setModules}
                    />

                )}

            </main>

        </div>
    );
}


export default Settings;
"""


# ============================================================
# Main
# ============================================================

def main():

    print()
    print("==============================================")
    print(" WebApp-2 Modularization")
    print("==============================================")
    print()

    ensure_project()
    verify_foundation()

    print()
    print("Creating backup...")
    backup_app()

    print()
    print("Creating component directories...")

    HOME_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    SETTINGS_DIR.mkdir(
        parents=True,
        exist_ok=True
    )


    print()
    print("Writing components...")

    write_file(
        HOME,
        HOME_CONTENT
    )

    write_file(
        LAUNCHER,
        LAUNCHER_CONTENT
    )

    write_file(
        LAUNCHER_CARD,
        LAUNCHER_CARD_CONTENT
    )

    write_file(
        SETTINGS,
        SETTINGS_CONTENT
    )

    write_file(
        MODULE_SETTINGS,
        MODULE_SETTINGS_CONTENT
    )


    print()
    print("Replacing App.jsx...")

    APP.write_text(
        APP_CONTENT.strip() + "\n",
        encoding="utf-8"
    )

    print(f"Updated: {APP}")


    print()
    print("==============================================")
    print(" MODULARIZATION COMPLETE")
    print("==============================================")
    print()
    print("Created:")
    print("  components/home/Home.jsx")
    print("  components/home/Launcher.jsx")
    print("  components/home/LauncherCard.jsx")
    print("  components/settings/Settings.jsx")
    print("  components/settings/ModuleSettings.jsx")
    print()
    print("Updated:")
    print("  components/App.jsx")
    print()
    print("Backup:")
    print("  components/App.jsx.pre-modularization")
    print()
    print("No CSS files were modified.")
    print("No package files were modified.")
    print()
    print("Now run the application and test it before committing.")
    print()


if __name__ == "__main__":
    main()