import React from 'react';
import { playSound } from '../../../audio/audioManager';

function ManagerSelector({
    managers,
    selected,
    open,
    onSelect,
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
                            <h3>Available package managers</h3>
                            <p>
                                Detection only. Nothing is installed,
                                removed, or upgraded.
                            </p>
                        </div>
                    </div>
                </div>
                {open && (
                    <div className="managergrid">
                        {managers.map(m => (
                            <button
                                className={
                                    'manager ' +
                                    (selected === m.id
                                        ? 'selected'
                                        : '')
                                }
                                key={m.id}
                                onClick={() =>
                                    onSelect(m.id)
                                }
                            >
                                <div className="icon">
                                    {m.name[0]}
                                </div>

                                <div className="mtext">
                                    <b>{m.name}</b>
                                    <span>
                                        {m.description}
                                    </span>
                                </div>

                                <em
                                    className={
                                        m.installed
                                            ? 'good'
                                            : ''
                                    }
                                >
                                    {m.installed
                                        ? 'AVAILABLE'
                                        : 'MISSING'}
                                </em>
                            </button>
                        ))}
                    </div>
                )}
            </section>
    );
}

export default ManagerSelector;
