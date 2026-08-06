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
