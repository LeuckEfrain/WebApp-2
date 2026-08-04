import React, { useEffect, useState } from 'react';

import {
    normalizePackageResults,
    rankPackageResults,
    determineBestSource
} from './packageUtils';

const API = 'http://127.0.0.1:8000';

function Packages({ managers }) {
    const [selected, setSelected] = useState('all');
    const [query, setQuery] = useState('');
    const [result, setResult] = useState(null);
    const [resultsHidden, setResultsHidden] = useState(false);
    const [inventory, setInventory] = useState(null);
    const [selectedPackages, setSelectedPackages] = useState([]);
    const [downloadState, setDownloadState] = useState(null);
    const [searchProgress, setSearchProgress] = useState(null);
    const [searchElapsed, setSearchElapsed] = useState(0);
    const [searchStartTime, setSearchStartTime] = useState(null);
    const [managersOpen, setManagersOpen] = useState(true);
    const [searchOpen, setSearchOpen] = useState(true);
    const [inventoryOpen, setInventoryOpen] = useState(true);

    function packageKey(pkg) {
        return `${pkg.manager}:${pkg.package}`;
    }

    function togglePackageSelection(pkg) {
        const key = packageKey(pkg);

        setSelectedPackages(previous => {
            if (previous.includes(key)) {
                return previous.filter(item => item !== key);
            }

            return [...previous, key];
        });
    }

    function selectAllPackages() {
        if (!result?.results) {
            return;
        }

        setSelectedPackages(
            result.results.map(pkg => packageKey(pkg))
        );
    }

    function clearPackageSelection() {
        setSelectedPackages([]);
    }

    async function downloadSelectedPackages() {
        if (
            !result?.results ||
            selectedPackages.length === 0
        ) {
            return;
        }

        const packagesToDownload = result.results
            .filter(pkg =>
                selectedPackages.includes(packageKey(pkg))
            )
            .map(pkg => ({
                manager: pkg.manager,
                package: pkg.package,
                name: pkg.name,
                version: pkg.version || ''
            }));

        setDownloadState({
            stage: 'confirm',
            total: packagesToDownload.length,
            completed: 0,
            progress: 0,
            results: [],
            packages: packagesToDownload,
            directory: null,
            error: null
        });

        try {
            const response = await fetch(
                API + '/api/download/destination'
            );

            const data = await response.json();

            if (!response.ok) {
                throw new Error(
                    data.detail ||
                    data.error ||
                    'Unable to determine download destination.'
                );
            }

            setDownloadState(previous => ({
                ...previous,
                directory: data.destination
            }));

        } catch (error) {
            setDownloadState(previous => ({
                ...previous,
                directory: null,
                error: error.message || String(error)
            }));
        }
    }

    async function confirmDownload() {
        if (!downloadState?.packages?.length) {
            return;
        }

        setDownloadState(previous => ({
            ...previous,
            stage: 'downloading',
            completed: 0,
            progress: 0,
            error: null
        }));

        try {
            const response = await fetch(
                API + '/api/package-managers/download',
                {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        packages: downloadState.packages
                    })
                }
            );

            const data = await response.json();

            if (!response.ok) {
                throw new Error(
                    data.detail ||
                    data.error ||
                    'Download failed.'
                );
            }

            setDownloadState(previous => ({
                ...previous,
                stage: 'complete',
                progress: 100,
                completed: data.successful,
                results: data.results || [],
                error: null
            }));

        } catch (error) {
            setDownloadState(previous => ({
                ...previous,
                stage: 'error',
                error: error.message || String(error)
            }));
        }
    }

    useEffect(() => {
        if (!searchStartTime || !searchProgress) {
            return;
        }

        if (searchProgress.completed >= searchProgress.total) {
            return;
        }

        const timer = setInterval(() => {
            setSearchElapsed(
                (Date.now() - searchStartTime) / 1000
            );
        }, 100);

        return () => clearInterval(timer);
    }, [searchStartTime, searchProgress]);

    useEffect(() => {
        fetch(API + '/api/software')
            .then(r => r.json())
            .then(setInventory)
            .catch(() => { });
    }, []);

    async function search() {
        if (!query.trim()) {
            return;
        }

        const availableManagers = managers.filter(
            manager => manager.installed
        );

        const managersToSearch =
            selected === 'all'
                ? availableManagers
                : availableManagers.filter(
                    manager => manager.id === selected
                );

        const completedCount = searchProgress?.completed || 0;

        if (managersToSearch.length === 0) {
            setResult({
                loading: false,
                error: 'No available package managers selected.',
                results: []
            });
            return;
        }

        setResultsHidden(false);
        setSelectedPackages([]);

        const startTime = Date.now();

        setSearchStartTime(startTime);
        setSearchElapsed(0);

        setSearchProgress({
            total: managersToSearch.length,
            completed: 0,
            statuses: Object.fromEntries(
                managersToSearch.map(manager => [
                    manager.id,
                    'waiting'
                ])
            )
        });

        setResult({
            loading: true
        });

        const searches = managersToSearch.map(manager => {
            setSearchProgress(previous => ({
                ...previous,
                statuses: {
                    ...previous.statuses,
                    [manager.id]: 'searching'
                }
            }));

            return fetch(
                `${API}/api/package-managers/${manager.id}/search?q=${encodeURIComponent(query)}`
            )
                .then(async response => {
                    const data = await response.json();

                    setSearchProgress(previous => ({
                        ...previous,
                        completed: previous.completed + 1,
                        statuses: {
                            ...previous.statuses,
                            [manager.id]: 'complete'
                        }
                    }));

                    return {
                        manager: manager.id,
                        data
                    };
                })
                .catch(error => {
                    setSearchProgress(previous => ({
                        ...previous,
                        completed: previous.completed + 1,
                        statuses: {
                            ...previous.statuses,
                            [manager.id]: 'error'
                        }
                    }));

                    return {
                        manager: manager.id,
                        data: {
                            error: String(error),
                            results: []
                        }
                    };
                });
        });

        try {
            const responses = await Promise.all(searches);

            let combined = [];

            for (const response of responses) {
                const normalized = normalizePackageResults(
                    response.data,
                    response.manager
                );

                combined = combined.concat(normalized);
            }

            const ranked = rankPackageResults(
                combined,
                query
            );

            const bestSource = determineBestSource(ranked);

            setResult({
                loading: false,
                query,
                results: ranked,
                bestSource,
                searchedManagers: managersToSearch.map(
                    manager => manager.id
                )
            });

            setSearchProgress(previous => ({
                ...previous,
                completed: previous.total
            }));
        } catch (error) {
            setResult({
                loading: false,
                error: String(error),
                results: []
            });
        }
    }

    return (
        <div className="stack">

            <section className="panel">
                <div
                    className="panelhead collapsible-header"
                    onClick={() => setManagersOpen(!managersOpen)}
                >
                    <div className="collapsible-title">
                        <button
                            className="collapse-button"
                            onClick={e => {
                                e.stopPropagation();
                                setManagersOpen(!managersOpen);
                            }}
                        >
                            {managersOpen ? '▼' : '▶'}
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
                {managersOpen && (
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
                                    setSelected(m.id)
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


            <section className="panel">

                <div
                    className="collapsible-header search-header"
                    onClick={() => setSearchOpen(!searchOpen)}
                >
                    <div className="collapsible-title">
                        <button
                            className="collapse-button"
                            onClick={e => {
                                e.stopPropagation();
                                setSearchOpen(!searchOpen);
                            }}
                        >
                            {searchOpen ? '▼' : '▶'}
                        </button>

                        <div className="eyebrow">
                            PACKAGE SEARCH
                        </div>
                    </div>
                </div>

                {searchOpen && (
                    <>
                        <div className="searchrow">

                            <select
                                value={selected}
                                onChange={e =>
                                    setSelected(e.target.value)
                                }
                            >
                                <option value="all">
                                    All available managers
                                </option>

                                {managers.map(m => (
                                    <option
                                        value={m.id}
                                        key={m.id}
                                    >
                                        {m.name}
                                    </option>
                                ))}
                            </select>

                            <input
                                value={query}
                                onChange={e =>
                                    setQuery(e.target.value)
                                }
                                onKeyDown={e =>
                                    e.key === 'Enter' && search()
                                }
                                placeholder="Search for a package..."
                            />

                            <button
                                className="primary"
                                onClick={search}
                            >
                                Search
                            </button>

                        </div>
                        {downloadState && (
                            <div className="download-panel">

                                {downloadState.stage === 'confirm' && (
                                    <>
                                        <div className="download-panel-header">
                                            <div>
                                                <div className="eyebrow">
                                                    DOWNLOAD
                                                </div>

                                                <h3>
                                                    Confirm download
                                                </h3>

                                                <p>
                                                    You are about to download{' '}
                                                    {downloadState.total}{' '}
                                                    {downloadState.total === 1
                                                        ? 'package'
                                                        : 'packages'}.
                                                </p>
                                            </div>
                                        </div>

                                        <div className="download-destination">
                                            <span>DESTINATION</span>

                                            <strong>
                                                {downloadState.directory ||
                                                    'Determining destination…'}
                                            </strong>
                                        </div>

                                        <div className="download-package-list">
                                            {downloadState.packages.map(pkg => (
                                                <div
                                                    className="download-package"
                                                    key={packageKey(pkg)}
                                                >
                                                    <span>
                                                        {pkg.name || pkg.package}
                                                    </span>

                                                    <em>
                                                        {pkg.manager}
                                                    </em>
                                                </div>
                                            ))}
                                        </div>

                                        {downloadState.error && (
                                            <div className="download-error">
                                                {downloadState.error}
                                            </div>
                                        )}

                                        <div className="download-actions">

                                            <button
                                                className="secondary"
                                                onClick={() =>
                                                    setDownloadState(null)
                                                }
                                            >
                                                Cancel
                                            </button>

                                            <button
                                                className="primary"
                                                disabled={
                                                    !downloadState.directory ||
                                                    !!downloadState.error
                                                }
                                                onClick={confirmDownload}
                                            >
                                                Confirm Download
                                            </button>

                                        </div>
                                    </>
                                )}

                                {downloadState.stage === 'downloading' && (
                                    <>
                                        <div className="download-panel-header">
                                            <div>
                                                <div className="eyebrow">
                                                    DOWNLOAD
                                                </div>

                                                <h3>
                                                    Downloading
                                                </h3>

                                                <p>
                                                    Download operation in progress.
                                                </p>
                                            </div>
                                        </div>

                                        <div className="progress-track">
                                            <div
                                                className="progress-fill"
                                                style={{
                                                    width: `${downloadState.total
                                                        ? (
                                                            downloadState.completed /
                                                            downloadState.total
                                                        ) * 100
                                                        : 0
                                                        }%`
                                                }}
                                            />
                                        </div>

                                        <div className="progress-details">
                                            <span>
                                                {downloadState.completed} of{' '}
                                                {downloadState.total} complete
                                            </span>

                                            <strong>
                                                {downloadState.total
                                                    ? Math.round(
                                                        (
                                                            downloadState.completed /
                                                            downloadState.total
                                                        ) * 100
                                                    )
                                                    : 0}%
                                            </strong>
                                        </div>
                                    </>
                                )}

                                {downloadState.stage === 'complete' && (
                                    <>
                                        <div className="download-panel-header">
                                            <div>
                                                <div className="eyebrow">
                                                    DOWNLOAD
                                                </div>

                                                <h3>
                                                    Download complete
                                                </h3>

                                                <p>
                                                    The download operation has finished.
                                                </p>
                                            </div>
                                        </div>

                                        <div className="download-destination">
                                            <span>DESTINATION</span>

                                            <strong>
                                                {downloadState.directory}
                                            </strong>
                                        </div>

                                        <div className="download-complete">
                                            <strong>
                                                {downloadState.completed}
                                            </strong>

                                            <span>
                                                {downloadState.completed === 1
                                                    ? 'package downloaded successfully'
                                                    : 'packages downloaded successfully'}
                                            </span>
                                        </div>

                                        <div className="download-actions">
                                            <button
                                                className="primary"
                                                onClick={() =>
                                                    setDownloadState(null)
                                                }
                                            >
                                                Done
                                            </button>
                                        </div>
                                    </>
                                )}

                                {downloadState.stage === 'error' && (
                                    <>
                                        <div className="download-panel-header">
                                            <div>
                                                <div className="eyebrow">
                                                    DOWNLOAD
                                                </div>

                                                <h3>
                                                    Download failed
                                                </h3>
                                            </div>
                                        </div>

                                        <div className="download-error">
                                            {downloadState.error}
                                        </div>

                                        <div className="download-actions">
                                            <button
                                                className="secondary"
                                                onClick={() =>
                                                    setDownloadState(null)
                                                }
                                            >
                                                Close
                                            </button>
                                        </div>
                                    </>
                                )}

                            </div>
                        )}


                        {result?.loading && searchProgress ? (
                            <div className="search-progress">

                                <div className="progress-header">
                                    <span>
                                        SEARCHING PACKAGE MANAGERS
                                    </span>

                                    <strong>
                                        {Math.round(
                                            (searchProgress.completed /
                                                searchProgress.total) *
                                            100
                                        )}%
                                    </strong>
                                </div>

                                <div className="progress-track">
                                    <div
                                        className="progress-fill"
                                        style={{
                                            width: `${(searchProgress.completed /
                                                searchProgress.total) *
                                                100
                                                }%`
                                        }}
                                    />
                                </div>

                                <div className="progress-details">
                                    <span>
                                        {searchProgress.completed} of{' '}
                                        {searchProgress.total} managers searched
                                    </span>

                                    <div className="progress-times">
                                        <span>
                                            Elapsed {searchElapsed.toFixed(1)}s
                                        </span>

                                        {searchProgress.completed > 0 &&
                                            searchProgress.completed < searchProgress.total ? (
                                            <span>
                                                ETA ~
                                                {(
                                                    (searchElapsed /
                                                        searchProgress.completed) *
                                                    (searchProgress.total -
                                                        searchProgress.completed)
                                                ).toFixed(1)}
                                                s
                                            </span>
                                        ) : searchProgress.completed >=
                                            searchProgress.total ? (
                                            <span>Complete</span>
                                        ) : (
                                            <span>ETA calculating…</span>
                                        )}
                                    </div>
                                </div>

                                <div className="manager-progress">
                                    {Object.entries(searchProgress.statuses).map(
                                        ([managerId, status]) => {

                                            const manager = managers.find(
                                                item => item.id === managerId
                                            );

                                            return (
                                                <div
                                                    className="manager-progress-item"
                                                    key={managerId}
                                                >
                                                    <i
                                                        className={
                                                            'status-dot ' + status
                                                        }
                                                    />

                                                    <span>
                                                        {manager?.name ||
                                                            managerId}
                                                    </span>

                                                    <em>
                                                        {status === 'complete'
                                                            ? 'Complete'
                                                            : status === 'searching'
                                                                ? 'Searching…'
                                                                : status === 'error'
                                                                    ? 'Error'
                                                                    : 'Waiting'}
                                                    </em>
                                                </div>
                                            );
                                        }
                                    )}
                                </div>

                            </div>
                        ) : (
                            <div className="notice">

                                {!result &&
                                    'No search performed'}

                                {result &&
                                    !result.loading &&
                                    !result.error &&
                                    `${result.results.length} results found`}

                                {result?.error &&
                                    result.error}

                            </div>
                        )}

                        <div className="result">

                            <div className="result-toolbar">

                                <div className="result-selection-info">
                                    <strong>
                                        {selectedPackages.length}
                                    </strong>

                                    <span>
                                        {selectedPackages.length === 1
                                            ? 'item selected'
                                            : 'items selected'}
                                    </span>
                                </div>

                                <div className="result-actions">

                                    <button
                                        className="secondary"
                                        disabled={
                                            !result ||
                                            result.loading ||
                                            !result.results?.length
                                        }
                                        onClick={selectAllPackages}
                                    >
                                        Select All
                                    </button>

                                    <button
                                        className="secondary"
                                        disabled={
                                            selectedPackages.length === 0
                                        }
                                        onClick={clearPackageSelection}
                                    >
                                        Clear Selection
                                    </button>

                                    <button
                                        className="secondary"
                                        disabled={
                                            selectedPackages.length === 0 ||
                                            downloadState?.loading
                                        }
                                        onClick={downloadSelectedPackages}
                                    >
                                        {downloadState?.loading
                                            ? 'Downloading…'
                                            : 'Download Selected'}
                                    </button>

                                    <button
                                        className="secondary"
                                        disabled={
                                            !result ||
                                            result.loading
                                        }
                                        onClick={() =>
                                            setResultsHidden(
                                                !resultsHidden
                                            )
                                        }
                                    >
                                        {resultsHidden
                                            ? 'Show Results'
                                            : 'Hide Results'}
                                    </button>

                                    <button
                                        className="secondary"
                                        disabled={
                                            !result ||
                                            result.loading
                                        }
                                        onClick={() => {
                                            setResult(null);
                                            setResultsHidden(false);
                                            setSelectedPackages([]);
                                        }}
                                    >
                                        Clear
                                    </button>

                                </div>

                            </div>


                            {!resultsHidden &&
                                result &&
                                !result.loading &&
                                !result.error && (

                                    <>

                                        {result.bestSource && (
                                            <div className="source-summary">

                                                <div>
                                                    <span>
                                                        BEST SOURCE
                                                    </span>

                                                    <strong>
                                                        {result.bestSource.manager}
                                                    </strong>
                                                </div>

                                                <div>
                                                    <span>
                                                        RELEVANCE
                                                    </span>

                                                    <strong>
                                                        {Math.round(
                                                            result.bestSource.score /
                                                            Math.max(
                                                                result.bestSource.count,
                                                                1
                                                            )
                                                        )}
                                                    </strong>
                                                </div>

                                                <div>
                                                    <span>
                                                        SEARCHED
                                                    </span>

                                                    <strong>
                                                        {result.searchedManagers.length}
                                                        {' '}
                                                        managers
                                                    </strong>
                                                </div>

                                            </div>
                                        )}


                                        {result.results.length > 0 && (

                                            <div className="package-results">

                                                {result.results.map(
                                                    (pkg, index) => (

                                                        <div
                                                            className={
                                                                'package-result ' +
                                                                (selectedPackages.includes(packageKey(pkg))
                                                                    ? 'selected'
                                                                    : '')
                                                            }
                                                            key={
                                                                pkg.manager +
                                                                '-' +
                                                                pkg.package +
                                                                '-' +
                                                                index
                                                            }
                                                            onClick={e => {
                                                                if (e.target.closest('input')) {
                                                                    return;
                                                                }

                                                                togglePackageSelection(pkg);
                                                            }}

                                                        >
                                                            <label
                                                                className="package-checkbox"
                                                                onClick={e => e.stopPropagation()}
                                                            >
                                                                <input
                                                                    type="checkbox"
                                                                    checked={selectedPackages.includes(
                                                                        packageKey(pkg)
                                                                    )}
                                                                    onChange={() =>
                                                                        togglePackageSelection(pkg)
                                                                    }
                                                                />

                                                                <span className="checkbox-box" />
                                                            </label>
                                                            <div className="package-result-main">

                                                                <b>
                                                                    {pkg.name}
                                                                </b>

                                                                <span>
                                                                    {pkg.description ||
                                                                        'No description available.'}
                                                                </span>

                                                            </div>


                                                            <div className="package-result-meta">

                                                                <span>
                                                                    {pkg.manager}
                                                                </span>

                                                                {pkg.version && (
                                                                    <span>
                                                                        {pkg.version}
                                                                    </span>
                                                                )}

                                                            </div>

                                                        </div>

                                                    )
                                                )}

                                            </div>

                                        )}


                                        {result.results.length === 0 && (

                                            <div className="empty">
                                                No packages found.
                                            </div>

                                        )}

                                    </>

                                )}

                        </div>
                    </>
                )}

            </section>


            <section className="panel">

                <div
                    className="panelhead collapsible-header"
                    onClick={() => setInventoryOpen(!inventoryOpen)}
                >
                    <div className="collapsible-title">
                        <button
                            className="collapse-button"
                            onClick={e => {
                                e.stopPropagation();
                                setInventoryOpen(!inventoryOpen);
                            }}
                        >
                            {inventoryOpen ? '▼' : '▶'}
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

                {inventoryOpen && (
                    <pre>
                        {inventory?.output ||
                            'No supported inventory source is available.'}
                    </pre>
                )}
            </section>

        </div>
    );
}
export default Packages;