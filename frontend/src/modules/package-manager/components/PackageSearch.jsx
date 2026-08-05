import React from 'react';
import { playSound } from '../../../audio/audioManager';

function PackageSearch({
    managers,
    packageKey,

    selected,
    query,

    result,
    resultsHidden,

    selectedPackages,

    downloadState,

    searchProgress,
    searchElapsed,

    open,

    onToggleOpen,
    onSelectManager,
    onQueryChange,
    onSearch,

    onClearResult,
    onToggleResults,

    onSelectAll,
    onClearSelection,
    onDownloadSelected,
    onTogglePackageSelection,

    onClearDownload,
    onConfirmDownload
}) {
    return (
        <section className="panel">

            <div
                className="collapsible-header search-header"
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

                    <div className="eyebrow">
                        PACKAGE SEARCH
                    </div>
                </div>
            </div>

            {open && (
                <>
                    <div className="searchrow">

                        <select
                            value={selected}
                            onChange={e =>
                                onSelectManager(e.target.value)
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
                                onQueryChange(e.target.value)
                            }
                            onKeyDown={e =>
                                e.key === 'Enter' && onSearch()
                            }
                            placeholder="Search for a package..."
                        />

                        <button
                            className="primary"
                            onClick={onSearch}
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
                                                onClearDownload()
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
                                            onClick={onConfirmDownload}
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
                                                onClearDownload()
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
                                                onClearDownload()
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
                                    onClick={onSelectAll}
                                >
                                    Select All
                                </button>

                                <button
                                    className="secondary"
                                    disabled={
                                        selectedPackages.length === 0
                                    }
                                    onClick={onClearSelection}
                                >
                                    Clear Selection
                                </button>

                                <button
                                    className="secondary"
                                    disabled={
                                        selectedPackages.length === 0 ||
                                        downloadState?.loading
                                    }
                                    onClick={onDownloadSelected}
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
                                        onClearResult();
                                        setResultsHidden(false);
                                        onClearSelection();
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

                                                            onTogglePackageSelection(pkg);
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
                                                                    onTogglePackageSelection(pkg)
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
    );
}

export default PackageSearch;
