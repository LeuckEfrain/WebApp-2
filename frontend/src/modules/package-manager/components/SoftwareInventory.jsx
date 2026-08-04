import React from 'react';

function SoftwareInventory({
    inventory,
    open,
    onToggleOpen
}) {
    return (
<section className="panel">

                <div
                    className="panelhead collapsible-header"
                    onClick={() => onToggleOpen()}
                >
                    <div className="collapsible-title">
                        <button
                            className="collapse-button"
                            onClick={e => {
                                e.stopPropagation();
                                onToggleOpen();
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
