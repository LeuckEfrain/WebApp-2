import React, { useEffect, useState } from 'react';
import { playSound } from '../../audio/audioManager'

import {
    normalizePackageResults,
    rankPackageResults,
    determineBestSource
} from './packageUtils';

import ManagerSelector from './components/ManagerSelector';
import SoftwareInventory from './components/SoftwareInventory';
import PackageSearch from './components/PackageSearch';

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

            playSound('downloadComplete')

            setDownloadState(previous => ({
                ...previous,
                stage: 'complete',
                progress: 100,
                completed: data.successful,
                results: data.results || [],
                error: null
            }))

        } catch (error) {
            playSound('error')

            setDownloadState(previous => ({
                ...previous,
                stage: 'error',
                error: error.message || String(error)
            }))
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

            <ManagerSelector
                managers={managers}
                selected={selected}
                open={managersOpen}
                onSelect={setSelected}
                onToggleOpen={() =>
                    setManagersOpen(!managersOpen)
                }
            />


            <PackageSearch
                managers={managers}

                selected={selected}
                query={query}

                result={result}
                resultsHidden={resultsHidden}

                selectedPackages={selectedPackages}

                downloadState={downloadState}

                searchProgress={searchProgress}
                searchElapsed={searchElapsed}

                open={searchOpen}

                onToggleOpen={() =>
                    setSearchOpen(!searchOpen)
                }

                onSelectManager={setSelected}
                onQueryChange={setQuery}
                onSearch={search}

                onClearResult={() =>
                    setResult(null)
                }

                onToggleResults={() =>
                    setResultsHidden(!resultsHidden)
                }

                onSelectAll={selectAllPackages}
                onClearSelection={clearPackageSelection}
                onDownloadSelected={downloadSelectedPackages}
                onTogglePackageSelection={
                    togglePackageSelection
                }

                onClearDownload={() =>
                    setDownloadState(null)
                }

                onConfirmDownload={confirmDownload}
                packageKey={packageKey}
            />


            <SoftwareInventory
                inventory={inventory}
                open={inventoryOpen}
                onToggleOpen={() =>
                    setInventoryOpen(!inventoryOpen)
                }
            />

        </div>
    );
}
export default Packages;