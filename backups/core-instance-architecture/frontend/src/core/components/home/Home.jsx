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
