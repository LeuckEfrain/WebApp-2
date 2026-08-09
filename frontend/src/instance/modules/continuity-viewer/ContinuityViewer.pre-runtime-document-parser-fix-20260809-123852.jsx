import { useMemo, useState, useEffect} from 'react';


const CONTINUITY_RUNTIME_URL = '/__webapp2_continuity__';

function parseContinuityDocument(content) {
    const lines = String(content || '')
        .replace(/\r\n/g, '\n')
        .split('\n');

    const sections = [];
    let currentSection = null;

    const clean = value =>
        String(value || '')
            .replace(/\*\*/g, '')
            .replace(/^\s*[-*•]\s*/, '')
            .trim();

    const normalizeTitle = value =>
        clean(value)
            .replace(/^#+\s*/, '')
            .replace(/[:：]\s*$/, '')
            .trim();

    const classify = title => {
        const value = title.toLowerCase();

        if (
            value.includes('vision') ||
            value.includes('purpose') ||
            value.includes('intended vision')
        ) {
            return 'vision';
        }

        if (
            value.includes('protocol') ||
            value.includes('rule') ||
            value.includes('development protocol')
        ) {
            return 'protocols';
        }

        if (
            value === 'goal' ||
            value === 'goals' ||
            value.includes('goal')
        ) {
            return 'goals';
        }

        if (
            value.includes('architecture') ||
            value.includes('architectural state')
        ) {
            return 'architecture';
        }

        if (
            value.includes('phase') ||
            value.includes('roadmap') ||
            value.includes('development phase')
        ) {
            return 'phases';
        }

        return 'detail';
    };

    const createSection = (title) => {
        const type = classify(title);

        const section = {
            id: type === 'detail'
                ? `section-${sections.length + 1}`
                : type,

            title,

            description: '',

            content: [],

            items: [],

            goals: [],

            phases: []
        };

        sections.push(section);
        currentSection = section;

        return section;
    };

    const addDescription = text => {
        const value = clean(text);

        if (!currentSection || !value) {
            return;
        }

        if (!currentSection.description) {
            currentSection.description = value;
        } else {
            currentSection.content.push(value);
        }
    };

    const addItem = (title, body = '') => {
        if (!currentSection) {
            return;
        }

        currentSection.items.push({
            title: clean(title),
            body: clean(body)
        });
    };

    const normalizeStatus = status => {
        const value = clean(status).toLowerCase();

        if (
            value === 'active' ||
            value === 'current' ||
            value === 'in progress'
        ) {
            return 'Active';
        }

        if (
            value === 'complete' ||
            value === 'completed' ||
            value === 'done'
        ) {
            return 'Complete';
        }

        if (
            value === 'continuing'
        ) {
            return 'Continuing';
        }

        if (
            value === 'next'
        ) {
            return 'Next';
        }

        return 'Planned';
    };

    const addGoal = (title, status = 'Active', phases = []) => {
        if (!currentSection) {
            return;
        }

        const cleanTitle = clean(title);

        if (!cleanTitle) {
            return;
        }

        const id =
            cleanTitle
                .toLowerCase()
                .replace(/[^a-z0-9]+/g, '-')
                .replace(/^-+|-+$/g, '') ||
            `goal-${currentSection.goals.length + 1}`;

        currentSection.goals.push({
            id,
            title: cleanTitle,
            status: normalizeStatus(status),
            phases: Array.isArray(phases)
                ? phases
                : []
        });
    };

    const addPhase = (
        title,
        status = 'Planned',
        body = ''
    ) => {
        if (!currentSection) {
            return;
        }

        currentSection.phases.push({
            title: clean(title),
            status: normalizeStatus(status),
            body: clean(body)
        });
    };

    let pendingGoal = null;

    const flushGoal = () => {
        if (!pendingGoal) {
            return;
        }

        addGoal(
            pendingGoal.title,
            pendingGoal.status,
            pendingGoal.phases
        );

        pendingGoal = null;
    };

    for (const rawLine of lines) {
        const line = rawLine.trim();

        if (!line) {
            continue;
        }

        const heading = line.match(
            /^(#{1,4})\s+(.+)$/
        );

        if (heading) {
            flushGoal();

            createSection(
                normalizeTitle(heading[2])
            );

            continue;
        }

        if (!currentSection) {
            continue;
        }

        const bullet = line.match(
            /^[-*•]\s+(.+)$/
        );

        if (bullet) {
            const rawValue = bullet[1].trim();

            const colon = rawValue.indexOf(':');

            let title = rawValue;
            let body = '';

            if (colon > 0) {
                title = rawValue.slice(0, colon);
                body = rawValue.slice(colon + 1);
            }

            if (currentSection.id === 'goals') {
                flushGoal();

                const statusMatch = body.match(
                    /(?:status|state)\s*[:=-]\s*(.+)$/i
                );

                pendingGoal = {
                    title: clean(title),
                    status: statusMatch
                        ? normalizeStatus(statusMatch[1])
                        : 'Active',
                    phases: []
                };

                continue;
            }

            if (currentSection.id === 'phases') {
                const statusMatch = body.match(
                    /(?:status|state)\s*[:=-]\s*(.+)$/i
                );

                addPhase(
                    title,
                    statusMatch
                        ? statusMatch[1]
                        : 'Planned',
                    statusMatch
                        ? body
                            .replace(
                                statusMatch[0],
                                ''
                            )
                            .trim()
                        : body
                );

                continue;
            }

            if (
                currentSection.id === 'protocols' ||
                currentSection.id === 'architecture'
            ) {
                addItem(title, body);
                continue;
            }

            addDescription(
                body
                    ? `${clean(title)}: ${clean(body)}`
                    : clean(title)
            );

            continue;
        }

        if (
            currentSection.id === 'goals' &&
            pendingGoal
        ) {
            const phaseMatch = line.match(
                /^(?:phase|step)\s*(?:\d+)?\s*[:=-]\s*(.+)$/i
            );

            if (phaseMatch) {
                pendingGoal.phases.push(
                    clean(phaseMatch[1])
                );

                continue;
            }

            const numberedMatch = line.match(
                /^\d+[\.)]\s+(.+)$/
            );

            if (numberedMatch) {
                pendingGoal.phases.push(
                    clean(numberedMatch[1])
                );

                continue;
            }

            const statusMatch = line.match(
                /^(?:status|state)\s*[:=-]\s*(.+)$/i
            );

            if (statusMatch) {
                pendingGoal.status =
                    normalizeStatus(
                        statusMatch[1]
                    );

                continue;
            }

            continue;
        }

        if (currentSection.id === 'phases') {
            const numbered = line.match(
                /^\d+[\.)]\s+(.+)$/
            );

            if (numbered) {
                addPhase(
                    numbered[1],
                    'Planned',
                    ''
                );

                continue;
            }
        }

        const keyValue = line.match(
            /^([^:：]+)[:：]\s*(.+)$/
        );

        if (
            keyValue &&
            (
                currentSection.id === 'protocols' ||
                currentSection.id === 'architecture'
            )
        ) {
            addItem(
                keyValue[1],
                keyValue[2]
            );

            continue;
        }

        addDescription(line);
    }

    flushGoal();

    const preferredOrder = [
        'vision',
        'protocols',
        'goals',
        'architecture',
        'phases'
    ];

    sections.sort((a, b) => {
        const ai = preferredOrder.indexOf(a.id);
        const bi = preferredOrder.indexOf(b.id);

        if (ai === -1 && bi === -1) {
            return 0;
        }

        if (ai === -1) {
            return 1;
        }

        if (bi === -1) {
            return -1;
        }

        return ai - bi;
    });

    return sections;
}

async function loadContinuityDocument() {
    const response = await fetch(
        `${CONTINUITY_RUNTIME_URL}?t=${Date.now()}`
    );

    if (!response.ok) {
        throw new Error(
            `Continuity document request failed: ${response.status}`
        );
    }

    const content = await response.text();

    if (!content.trim()) {
        throw new Error(
            'The runtime continuity document is empty.'
        );
    }

    return parseContinuityDocument(content);
}


const FOUNDATION_CONTINUITY_SECTIONS = [
    {
        id: 'vision',
        title: 'Project Vision',
        description:
            'The overall purpose and intended interaction model of WebApp-2.',
        content: [
            'WebApp-2 is a modular personal web application environment with a PlayStation-inspired launcher/home-screen experience.',
            'The Home environment is separate from the Settings/system interface.',
            'The launcher is intended to scale in two dimensions and support context-specific applications.'
        ]
    },
    {
        id: 'protocols',
        title: 'Protocols',
        items: [
            {
                title: 'modify_frontend.py',
                body:
                    'Codebase changes should normally be implemented through an automated modify_frontend.py script rather than manual source editing.'
            },
            {
                title: 'Modularization',
                body:
                    'The project should be checked for architectural monoliths and modularized proactively when appropriate.'
            },
            {
                title: 'Resource Efficiency',
                body:
                    'Avoid unnecessary tool use, processing, data analysis, or other resource-heavy work.'
            },
            {
                title: 'Git / Repository',
                body:
                    'Development should be anchored to explicit Git commits and the actual repository foundation.'
            },
            {
                title: 'Backup',
                body:
                    'Automated source modifications should create safe backups before overwriting existing files.'
            },
            {
                title: 'Continuity',
                body:
                    'The project-state document must remain portable and current so development can resume in another conversation.'
            }
        ]
    },
    {
        id: 'goals',
        title: 'Goals',
        goals: [
            {
                id: 'launcher',
                title: 'Home Launcher',
                status: 'Active',
                phases: [
                    'Home shell',
                    'Horizontal carousel',
                    'Vertical row navigation',
                    'Data-driven launcher'
                ]
            },
            {
                id: 'module-architecture',
                title: 'Instance-Local Module Architecture',
                status: 'Active',
                phases: [
                    'Separate core environment from installed modules',
                    'Maintain instance registry',
                    'Preserve modules through core updates',
                    'Support independently installed module software'
                ]
            },
            {
                id: 'settings',
                title: 'Settings / System Environment',
                status: 'Active',
                phases: [
                    'Package manager',
                    'Module management',
                    'Appearance configuration',
                    'Additional system functionality'
                ]
            }
        ]
    },
    {
        id: 'architecture',
        title: 'Architecture',
        items: [
            {
                title: 'WebApp-2 Core',
                body:
                    'The universal environment: Home, Launcher, Settings, Module Manager, and core interfaces.'
            },
            {
                title: 'Instance-Level Software',
                body:
                    'Installed and user-created modules belong to the individual WebApp-2 instance and should not be hard-coded into the universal core.'
            },
            {
                title: 'Instance Registry',
                body:
                    'Stores installed/configured module state belonging to the current WebApp-2 instance.'
            }
        ]
    },
    {
        id: 'phases',
        title: 'Development Phases',
        phases: [
            {
                title: 'Phase 1 — Home Shell',
                status: 'Complete',
                body:
                    'Separate Home from Settings, establish the top bar, Settings control, and launcher area.'
            },
            {
                title: 'Phase 2 — Horizontal Carousel',
                status: 'Next',
                body:
                    'Implement horizontal movement, fixed selection reference, animation, keyboard navigation, mouse navigation, and sound.'
            },
            {
                title: 'Phase 3 — Vertical Row Navigation',
                status: 'Planned',
                body:
                    'Add vertically stacked launcher rows with hidden rows above and below the active row.'
            },
            {
                title: 'Phase 4 — Data-Driven Launcher',
                status: 'Planned',
                body:
                    'Allow launcher applications to be represented and configured through module data.'
            },
            {
                title: 'Phase 5 — Existing System Behind Settings',
                status: 'Continuing',
                body:
                    'Keep package management, module management, appearance, and related system functionality behind Settings.'
            }
        ]
    }
];


function Section({
    section,
    open,
    onToggle,
    activeGoal,
    onGoalSelect,
    openGoalPhases,
    onGoalPhaseToggle,
    getPhaseState,
    onPhaseStateChange
}) {
    return (
        <section className="continuity-section">
            <button
                type="button"
                className="continuity-section-header"
                onClick={onToggle}
                aria-expanded={open}
            >
                <span className="continuity-section-title">
                    {section.title}
                </span>

                <span className="continuity-section-toggle">
                    {open ? '−' : '+'}
                </span>
            </button>

            {open && (
                <div className="continuity-section-body indefinite-list">

                    {section.description && (
                        <p className="continuity-description">
                            {section.description}
                        </p>
                    )}

                    {section.content?.map(item => (
                        <div
                            className="continuity-detail"
                            key={item}
                        >
                            {item}
                        </div>
                    ))}

                    {section.items?.map(item => (
                        <article
                            className="continuity-item"
                            key={item.title}
                        >
                            <strong>{item.title}</strong>
                            <p>{item.body}</p>
                        </article>
                    ))}

                    {section.goals?.map(goal => {
                        const selected =
                            activeGoal === goal.id;

                        const phasesOpen =
                            openGoalPhases.has(goal.id);

                        const allPhasesComplete =
                            goal.phases.length > 0 &&
                            goal.phases.every(
                                (_, index) =>
                                    getPhaseState(
                                        goal.id,
                                        index
                                    ).complete
                            );

                        const goalStatus =
                            allPhasesComplete
                                ? 'Complete'
                                : goal.status;

                        return (
                            <article
                                className={
                                    'continuity-goal' +
                                    (selected
                                        ? ' active'
                                        : '') +
                                    (allPhasesComplete
                                        ? ' complete'
                                        : '')
                                }
                                key={goal.id}
                            >
                                <div className="continuity-goal-header">
                                    <div>
                                        <strong>{goal.title}</strong>

                                        <span className="continuity-status">
                                            {goalStatus}
                                        </span>
                                    </div>

                                    <div className="continuity-goal-actions">
                                        <button
                                            type="button"
                                            className="secondary"
                                            onClick={() =>
                                                onGoalPhaseToggle(
                                                    goal.id
                                                )
                                            }
                                            aria-expanded={phasesOpen}
                                        >
                                            {phasesOpen
                                                ? 'Hide Phases'
                                                : 'Show Phases'}
                                        </button>

                                        <button
                                            type="button"
                                            className={
                                                selected
                                                    ? 'secondary'
                                                    : 'primary'
                                            }
                                            onClick={() =>
                                                onGoalSelect(
                                                    selected
                                                        ? null
                                                        : goal.id
                                                )
                                            }
                                        >
                                            {selected
                                                ? 'Active Goal'
                                                : 'Set Active'}
                                        </button>
                                    </div>
                                </div>

                                {phasesOpen && (
                                    <div className="continuity-phase-list indefinite-list">
                                        {goal.phases.map(
                                            (phase, index) => {
                                                const state =
                                                    getPhaseState(
                                                        goal.id,
                                                        index
                                                    );

                                                const neither =
                                                    !state.active &&
                                                    !state.complete;

                                                return (
                                                    <div
                                                        className={
                                                            'continuity-phase' +
                                                            (state.active
                                                                ? ' active'
                                                                : '') +
                                                            (state.complete
                                                                ? ' complete'
                                                                : '')
                                                        }
                                                        key={`${goal.id}-${index}`}
                                                    >
                                                        

                                                        <span
                                                            className={
                                                                'continuity-phase-status-indicator' +
                                                                (state.active
                                                                    ? ' active'
                                                                    : state.complete
                                                                        ? ' complete'
                                                                        : '')
                                                            }
                                                        >
                                                            {state.active
                                                                ? 'Active'
                                                                : state.complete
                                                                    ? 'Complete'
                                                                    : 'Pending'}
                                                        </span>

                                                        <div className="continuity-phase-main">
                                                            <div className="continuity-phase-title">
                                                                <span>
                                                                    Phase {index + 1}
                                                                </span>
                                                                <strong>
                                                                    {phase}
                                                                </strong>
                                                            </div>


                                                             <div className="continuity-phase-status-controls">
                                                                 <label className="continuity-phase-status-option">
                                                                     <input
                                                                         type="checkbox"
                                                                         checked={state.active}
                                                                         onChange={() =>
                                                                             onPhaseStateChange(
                                                                                 goal.id,
                                                                                 index,
                                                                                 'active'
                                                                             )
                                                                         }
                                                                     />
                                                                     <span>Active</span>
                                                                 </label>

                                                                 <label className="continuity-phase-status-option">
                                                                     <input
                                                                         type="checkbox"
                                                                         checked={state.complete}
                                                                         onChange={() =>
                                                                             onPhaseStateChange(
                                                                                 goal.id,
                                                                                 index,
                                                                                 'complete'
                                                                             )
                                                                         }
                                                                     />
                                                                     <span>Complete</span>
                                                                 </label>
                                                             </div>
                                                        </div>
                                                    </div>
                                                );
                                            }
                                        )}
                                    </div>
                                )}
                            </article>
                        );
                    })}

                    {section.phases?.map(phase => (
                        <article
                            className="continuity-phase-card"
                            key={phase.title}
                        >
                            <div className="continuity-phase-card-head">
                                <strong>{phase.title}</strong>

                                <span className="continuity-status">
                                    {phase.status}
                                </span>
                            </div>

                            <p>{phase.body}</p>
                        </article>
                    ))}

                </div>
            )}
        </section>
    );
}

function ContinuityViewer() {
    const [continuitySections, setContinuitySections] =
        useState(FOUNDATION_CONTINUITY_SECTIONS);

    useEffect(() => {
        let cancelled = false;

        loadContinuityDocument()
            .then(parsedSections => {
                if (cancelled) {
                    return;
                }

                if (
                    Array.isArray(parsedSections) &&
                    parsedSections.length > 0
                ) {
                    setContinuitySections(
                        parsedSections
                    );
                }
            })
            .catch(error => {
                console.error(
                    'Unable to load continuity document:',
                    error
                );
            });

        return () => {
            cancelled = true;
        };
    }, []);

    const [openSections, setOpenSections] = useState(
        () => new Set(['goals'])
    );

    const [activeGoal, setActiveGoal] = useState(
        () =>
            localStorage.getItem(
                'webapp2-continuity-active-goal'
            ) || null
    );

    const [openGoalPhases, setOpenGoalPhases] = useState(
        () => {
            try {
                const stored = localStorage.getItem(
                    'webapp2-continuity-open-goal-phases'
                );

                if (stored) {
                    return new Set(JSON.parse(stored));
                }
            } catch {
                // Use defaults if persisted state is invalid.
            }

            return new Set(
                continuitySections
                    .find(section => section.id === 'goals')
                    ?.goals
                    ?.map(goal => goal.id) || []
            );
        }
    );

    const [phaseStatuses, setPhaseStatuses] = useState(
        () => {
            try {
                const stored = localStorage.getItem(
                    'webapp2-continuity-phase-statuses'
                );

                return stored
                    ? JSON.parse(stored)
                    : {};
            } catch {
                return {};
            }
        }
    );

    const visibleCount = useMemo(
        () => openSections.size,
        [openSections]
    );

    const toggleSection = id => {
        setOpenSections(current => {
            const next = new Set(current);

            if (next.has(id)) {
                next.delete(id);
            } else {
                next.add(id);
            }

            return next;
        });
    };

    const selectGoal = id => {
        setActiveGoal(id);

        if (id) {
            localStorage.setItem(
                'webapp2-continuity-active-goal',
                id
            );
        } else {
            localStorage.removeItem(
                'webapp2-continuity-active-goal'
            );
        }
    };

    const toggleGoalPhases = goalId => {
        setOpenGoalPhases(current => {
            const next = new Set(current);

            if (next.has(goalId)) {
                next.delete(goalId);
            } else {
                next.add(goalId);
            }

            localStorage.setItem(
                'webapp2-continuity-open-goal-phases',
                JSON.stringify([...next])
            );

            return next;
        });
    };

    const getPhaseState = (goalId, phaseIndex) => {
        const stored =
            phaseStatuses?.[goalId]?.[phaseIndex];

        return {
            active: stored?.active === true,
            complete: stored?.complete === true
        };
    };

    const setPhaseState = (
        goalId,
        phaseIndex,
        requestedState
    ) => {
        setPhaseStatuses(current => {
            const currentGoal =
                current?.[goalId] || {};

            const currentPhase =
                currentGoal?.[phaseIndex] || {
                    active: false,
                    complete: false
                };

            let nextPhase;

            if (requestedState === 'active') {
                nextPhase = {
                    active: !currentPhase.active,
                    complete: false
                };
            } else {
                nextPhase = {
                    active: false,
                    complete: !currentPhase.complete
                };
            }

            const next = {
                ...current,
                [goalId]: {
                    ...currentGoal,
                    [phaseIndex]: nextPhase
                }
            };

            localStorage.setItem(
                'webapp2-continuity-phase-statuses',
                JSON.stringify(next)
            );

            return next;
        });
    };

    const openAll = () => {
        setOpenSections(
            new Set(
                continuitySections.map(
                    section => section.id
                )
            )
        );
    };

    const closeAll = () => {
        setOpenSections(new Set());
    };

    return (
        <div className="continuity-viewer">
            <div className="continuity-toolbar">
                <div>
                    <div className="eyebrow">
                        INSTANCE MODULE
                    </div>

                    <h2>Continuity</h2>

                    <p>
                        Navigate the active WebApp-2 project
                        state without reading the raw document.
                    </p>
                </div>

                <div className="continuity-toolbar-actions">
                    <button
                        type="button"
                        className="secondary"
                        onClick={openAll}
                    >
                        Open All
                    </button>

                    <button
                        type="button"
                        className="secondary"
                        onClick={closeAll}
                    >
                        Close All
                    </button>
                </div>
            </div>

            <div className="continuity-summary">
                <div>
                    <span>OPEN SECTIONS</span>
                    <strong>{visibleCount}</strong>
                </div>

                <div>
                    <span>ACTIVE GOAL</span>
                    <strong>
                        {activeGoal
                            ? 'Selected'
                            : 'None'}
                    </strong>
                </div>

                <div>
                    <span>MODULE TYPE</span>
                    <strong>INSTANCE</strong>
                </div>
            </div>

            <div className="continuity-sections">
                {continuitySections.map(section => (
                    <Section
                        key={section.id}
                        section={section}
                        open={openSections.has(section.id)}
                        onToggle={() =>
                            toggleSection(section.id)
                        }
                        activeGoal={activeGoal}
                        onGoalSelect={selectGoal}
                        openGoalPhases={openGoalPhases}
                        onGoalPhaseToggle={
                            toggleGoalPhases
                        }
                        getPhaseState={getPhaseState}
                        onPhaseStateChange={
                            setPhaseState
                        }
                    />
                ))}
            </div>
        </div>
    );
}

export default ContinuityViewer;