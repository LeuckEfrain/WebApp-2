import React, { useEffect, useState } from 'react';

import Nav from './Nav';
import Dashboard from './Dashboard';
import PackageManager from '../modules/package-manager/PackageManager';

const API = 'http://127.0.0.1:8000';

function App() {
    const [page, setPage] = useState('dashboard');
    const [managers, setManagers] = useState([]);

    const [theme, setTheme] = useState(() => {
        return localStorage.getItem('modular-theme') || 'obsidian';
    });

    const [font, setFont] = useState(() => {
        return localStorage.getItem('modular-font') || 'inter';
    });

    useEffect(() => {
        document.documentElement.dataset.theme = theme;
        localStorage.setItem('modular-theme', theme);
    }, [theme]);

    useEffect(() => {
        document.documentElement.dataset.font = font;
        localStorage.setItem('modular-font', font);
    }, [font]);

    useEffect(() => {
        fetch(API + '/api/package-managers')
            .then(r => r.json())
            .then(setManagers)
            .catch(() => { });
    }, []);

    return (
        <div className="shell">
            <aside className="sidebar">
                <div className="logo">MODULAR</div>

                <div className="label">WORKSPACE</div>

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

                <div className="label lower">SYSTEM</div>

                <Nav>Processes</Nav>
                <Nav>Environment</Nav>

                <div className="label lower">MODULES</div>

                <Nav>Modules</Nav>

                <div className="label lower">APPEARANCE</div>

                <div className="theme-control">
                    <label htmlFor="theme-select">COLOR PALETTE</label>

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
                    <label htmlFor="font-select">FONT</label>

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
                        <div className="eyebrow">LOCAL CONTROL PANEL</div>

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
                ) : (
                    <PackageManager managers={managers} />
                )}
            </main>
        </div>
    );
}
export default App;