import React, { useEffect, useState } from 'react';

import Nav from './Nav';
import Dashboard from './Dashboard';
import PackageManager from '../modules/package-manager/PackageManager';

const API = 'http://127.0.0.1:8000';

const DEFAULT_HOME_MODULES = [
    {
        id: 'gmail-analyzer',
        name: 'Gmail Analyzer',
        icon: 'G'
    },
    {
        id: 'git-tools',
        name: 'Git Tools',
        icon: 'G'
    },
    {
        id: 'future-1',
        name: 'Future Module',
        icon: '+',
        placeholder: true
    },
    {
        id: 'future-2',
        name: 'Future Module',
        icon: '+',
        placeholder: true
    }
];

function Home({ onSettings, modules }) {
    return (
        <div className="home-shell">
            <header className="home-topbar">
                <div className="home-brand">MODULAR</div>

                <button
                    type="button"
                    className="settings-button"
                    onClick={onSettings}
                    aria-label="Open Settings"
                >
                    <span className="settings-icon">⚙</span>
                    <span>Settings</span>
                </button>
            </header>

            <main className="launcher">
                <div className="launcher-row-area">

                    {/* Vertical navigation — Phase 3 */}
                    <button
                        type="button"
                        className="launcher-axis-arrow"
                        disabled
                        aria-label="Previous row"
                    >
                        ▲
                    </button>

                    <div className="launcher-row">

                        {/* Horizontal navigation — Phase 2 */}
                        <button
                            type="button"
                            className="launcher-arrow"
                            disabled
                            aria-label="Previous module"
                        >
                            ‹
                        </button>

                        {modules.map((module, index) => (
                            <div
                                key={module.id}
                                className={`launcher-card ${index === 0 ? 'launcher-card-selected' : ''
                                    } ${module.placeholder
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
                        ))}

                        <button
                            type="button"
                            className="launcher-arrow"
                            disabled
                            aria-label="Next module"
                        >
                            ›
                        </button>
                    </div>

                    {/* Vertical navigation — Phase 3 */}
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
                    <span>{modules[0]?.name}</span>
                </div>
            </main>
        </div>
    );
}

function ModuleSettings({ modules, setModules }) {

    const renameModule = (id, name) => {

        setModules(current =>
            current.map(module =>
                module.id === id
                    ? { ...module, name }
                    : module
            )
        );

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

                {modules
                    .filter(module => !module.placeholder)
                    .map(module => (

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
                                        onChange={e =>
                                            renameModule(
                                                module.id,
                                                e.target.value
                                            )
                                        }
                                    />
                                </label>

                            </div>

                        </div>

                    ))}

            </div>

        </section>
    );
}

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
                    onClick={() => setPage('dashboard')}
                >
                    Dashboard
                </Nav>

                <Nav
                    active={page === 'packages'}
                    onClick={() => setPage('packages')}
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
                    onClick={() => setPage('modules')}
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
                        onChange={e => setTheme(e.target.value)}
                    >
                        <option value="obsidian">Obsidian</option>
                        <option value="slate">Slate</option>
                        <option value="forest">Forest</option>
                        <option value="copper">Copper</option>
                    </select>
                </div>

                <div className="theme-control">
                    <label htmlFor="font-select">
                        FONT
                    </label>

                    <select
                        id="font-select"
                        value={font}
                        onChange={e => setFont(e.target.value)}
                    >
                        <option value="inter">Inter</option>
                        <option value="plex">IBM Plex Sans</option>
                        <option value="jetbrains">JetBrains Mono</option>
                        <option value="source">Source Sans 3</option>
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
                                : 'Dashboard'}
                        </h1>
                    </div>

                    <div className="online">
                        <i /> BACKEND ONLINE
                    </div>
                </header>

                {page === 'dashboard' ? (
                    <Dashboard
                        managers={managers}
                        open={() => setPage('packages')}
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

    const [theme, setTheme] = useState(() => {
        return localStorage.getItem('modular-theme') || 'obsidian';
    });

    const [font, setFont] = useState(() => {
        return localStorage.getItem('modular-font') || 'inter';
    });


    useEffect(() => {

        document.documentElement.dataset.theme = theme;

        localStorage.setItem(
            'modular-theme',
            theme
        );

    }, [theme]);


    useEffect(() => {

        document.documentElement.dataset.font = font;

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
            .then(r => r.json())
            .then(setManagers)
            .catch(() => { });

    }, []);


    if (view === 'home') {

        return (
            <Home
                onSettings={() => setView('settings')}
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
            onHome={() => setView('home')}
            modules={modules}
            setModules={setModules}
        />
    );
}


export default App;