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
