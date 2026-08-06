import React from 'react';
import { playSound } from '../../../audio/audioManager';

function SoftwareInventory({
    inventory,
    open,
    onToggleOpen
}) {

    const handleToggleOpen = () => {
        playSound(open ? 'menuClose' : 'menuOpen')
        onToggleOpen()
    }

    return (
        <section className="panel">

            <div
                className="panelhead collapsible-header"
                onClick={handleToggleOpen}
            >
                <div className="collapsible-title">
                    <button
                        className="collapse-button"
                        onClick={e => {
                            e.stopPropagation();
                            handleToggleOpen();
                        }}
                    >
                        {open ? '▼' : '▶'}
                    </button>

                    <div>
                        <h3>Installed software</h3>

                        <p>
                            Read-only inventory from the
                            available system source.
                        </p>
                    </div>
                </div>

                {inventory?.source && (
                    <span className="source">
                        SOURCE · {inventory.source}
                    </span>
                )}
            </div>

            {open && (
                <pre>
                    {inventory?.output ||
                        'No supported inventory source is available.'}
                </pre>
            )}
        </section>
    );
}

export default SoftwareInventory;
