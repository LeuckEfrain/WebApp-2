import React from 'react';

import Stat from './Stat';

function Dashboard({ managers, open }) {
    let count = managers.filter(x => x.installed).length;

    return (
        <div className="stack">
            <section className="hero">
                <div>
                    <div className="eyebrow">SYSTEM OVERVIEW</div>

                    <h2>Your local workspace</h2>

                    <p>
                        Inspect development tools and search package
                        repositories from one place.
                    </p>
                </div>
            </section>

            <div className="stats">
                <Stat
                    title="Package managers"
                    value={`${count}/${managers.length}`}
                    detail="available on PATH"
                />

                <Stat
                    title="Operations"
                    value="READ-ONLY"
                    detail="no software changes"
                />

                <Stat
                    title="Automation"
                    value="OFF"
                    detail="user remains in control"
                />
            </div>

            <section className="panel">
                <div className="panelhead">
                    <div>
                        <h3>Package management</h3>

                        <p>
                            Search repositories and inspect installed
                            software.
                        </p>
                    </div>

                    <button className="primary" onClick={open}>
                        Open
                    </button>
                </div>
            </section>
        </div>
    );
}
