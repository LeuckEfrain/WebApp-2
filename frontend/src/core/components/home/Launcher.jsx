import { useEffect, useState } from 'react';
import LauncherCard from './LauncherCard';
import { playSound } from '../../audio/audioManager';

const INITIAL_SELECTED_POSITION = 1;

function Launcher({ modules }) {
    const enabledModules = modules.filter(
        module => module.enabled
    );

    const [selectedIndex, setSelectedIndex] = useState(
        () =>
            Math.min(
                INITIAL_SELECTED_POSITION,
                Math.max(enabledModules.length - 1, 0)
            )
    );

    useEffect(() => {
        setSelectedIndex(current =>
            Math.min(
                current,
                Math.max(enabledModules.length - 1, 0)
            )
        );
    }, [enabledModules.length]);

    const moveHorizontal = direction => {
        if (enabledModules.length <= 1) {
            return;
        }

        const nextIndex = selectedIndex + direction;

        if (
            nextIndex < 0 ||
            nextIndex >= enabledModules.length
        ) {
            return;
        }

        setSelectedIndex(nextIndex);

        playSound('click', 0.35);
    };

    useEffect(() => {
        const handleKeyDown = event => {
            const key = event.key.toLowerCase();

            if (
                key === 'arrowleft' ||
                key === 'a'
            ) {
                event.preventDefault();
                moveHorizontal(-1);
                return;
            }

            if (
                key === 'arrowright' ||
                key === 'd'
            ) {
                event.preventDefault();
            }
        };

        window.addEventListener(
            'keydown',
            handleKeyDown
        );

        return () => {
            window.removeEventListener(
                'keydown',
                handleKeyDown
            );
        };
    }, [
        selectedIndex,
        enabledModules.length
    ]);

    const handleCardClick = index => {
        if (index < selectedIndex) {
            moveHorizontal(-1);
            return;
        }

        if (index > selectedIndex) {
            moveHorizontal(1);
        }
    };

    const selectedModule =
        enabledModules[selectedIndex];

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
                        onClick={() =>
                            moveHorizontal(-1)
                        }
                        disabled={
                            selectedIndex <= 0
                        }
                        aria-label="Previous module"
                    >
                        ‹
                    </button>

                    <div className="launcher-card-viewport">

                        <div
                            className="launcher-card-track"
                            style={{
                                '--launcher-index':
                                    selectedIndex
                            }}
                        >
                            {enabledModules.map(
                                (module, index) => (
                                    <LauncherCard
                                        key={module.id}
                                        module={module}
                                        selected={
                                            index ===
                                            selectedIndex
                                        }
                                        onClick={() =>
                                            handleCardClick(
                                                index
                                            )
                                        }
                                    />
                                )
                            )}
                        </div>

                    </div>

                    <button
                        type="button"
                        className="launcher-arrow"
                        onClick={() =>
                            moveHorizontal(1)
                        }
                        disabled={
                            selectedIndex >=
                            enabledModules.length - 1
                        }
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
                    {selectedModule?.name}
                </span>

            </div>

        </main>
    );
}

export default Launcher;
