from pathlib import Path
from datetime import datetime
import shutil
import sys


ROOT = Path(__file__).resolve().parent

# Allow the script to be copied into either:
#   D:\Projects\WebApps\webapp_2\modify_frontend.py
# or:
#   D:\Projects\WebApps\webapp_2\tools\modify_frontend.py
if ROOT.name == "tools":
    PROJECT_ROOT = ROOT.parent
else:
    PROJECT_ROOT = ROOT

FRONTEND = PROJECT_ROOT / "frontend"
SRC = FRONTEND / "src"

CORE = SRC / "core"
INSTANCE = SRC / "instance"

APP = CORE / "App.jsx"
LAUNCHER = CORE / "components" / "home" / "Launcher.jsx"
STYLES = CORE / "styles.css"
REGISTRY = INSTANCE / "moduleRegistry.js"

MODULE_DIR = INSTANCE / "modules" / "continuity-viewer"
MODULE = MODULE_DIR / "ContinuityViewer.jsx"


EXPECTED_COMMIT = "2b366065537a9a29ff4ef7d4ceaa4ea9f4c5acbe"


def fail(message):
    print("\nERROR")
    print("-----")
    print(message)
    print("\nNo changes were made.")
    sys.exit(1)


def require_file(path):
    if not path.exists():
        fail(f"Required file does not exist:\n{path}")


def backup(path):
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup_path = path.with_name(
        f"{path.name}.pre-continuity-viewer-{timestamp}"
    )

    if backup_path.exists():
        fail(
            "Refusing to overwrite an existing backup:\n"
            f"{backup_path}"
        )

    shutil.copy2(path, backup_path)
    return backup_path


def read(path):
    return path.read_text(encoding="utf-8")


def write(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


# ------------------------------------------------------------
# FOUNDATION CHECK
# ------------------------------------------------------------

required = [
    APP,
    LAUNCHER,
    STYLES,
    REGISTRY,
]

for path in required:
    require_file(path)


app = read(APP)
launcher = read(LAUNCHER)
styles = read(STYLES)
registry = read(REGISTRY)


# ------------------------------------------------------------
# SAFETY CHECKS
# ------------------------------------------------------------

if "function App()" not in app:
    fail("Unexpected App.jsx foundation.")

if "function Launcher({ modules })" not in launcher:
    fail("Unexpected Launcher.jsx foundation.")

if "webapp2-instance-modules" not in registry:
    fail("Unexpected moduleRegistry.js foundation.")

if ".launcher-card-track" not in styles:
    fail("Expected launcher styling was not found.")

if "ContinuityViewer" in app or "continuity-viewer" in app:
    fail(
        "Continuity Viewer appears to already be integrated into App.jsx.\n"
        "Refusing to apply the change twice."
    )

if "continuity-viewer" in registry:
    fail(
        "Continuity Viewer appears to already exist in moduleRegistry.js.\n"
        "Refusing to apply the change twice."
    )


# ------------------------------------------------------------
# BACKUPS
# ------------------------------------------------------------

backups = [
    backup(APP),
    backup(LAUNCHER),
    backup(STYLES),
    backup(REGISTRY),
]


# ------------------------------------------------------------
# CREATE INSTANCE MODULE
# ------------------------------------------------------------

MODULE_CONTENT = r"""import { useMemo, useState } from 'react';

const CONTINUITY_SECTIONS = [
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


function Section({ section, open, onToggle, activeGoal, onGoalSelect }) {
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
                <div className="continuity-section-body">
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

                        return (
                            <article
                                className={
                                    'continuity-goal' +
                                    (selected
                                        ? ' active'
                                        : '')
                                }
                                key={goal.id}
                            >
                                <div className="continuity-goal-header">
                                    <div>
                                        <strong>{goal.title}</strong>
                                        <span className="continuity-status">
                                            {goal.status}
                                        </span>
                                    </div>

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

                                <div className="continuity-phase-list">
                                    {goal.phases.map(
                                        (phase, index) => (
                                            <div
                                                className="continuity-phase"
                                                key={phase}
                                            >
                                                <span>
                                                    {index + 1}
                                                </span>
                                                <div>
                                                    Phase {index + 1}
                                                    <strong>
                                                        {phase}
                                                    </strong>
                                                </div>
                                            </div>
                                        )
                                    )}
                                </div>
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
    const [openSections, setOpenSections] = useState(
        () => new Set(['goals'])
    );

    const [activeGoal, setActiveGoal] = useState(
        () =>
            localStorage.getItem(
                'webapp2-continuity-active-goal'
            ) || null
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

    const openAll = () => {
        setOpenSections(
            new Set(
                CONTINUITY_SECTIONS.map(
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
                {CONTINUITY_SECTIONS.map(section => (
                    <Section
                        key={section.id}
                        section={section}
                        open={openSections.has(section.id)}
                        onToggle={() =>
                            toggleSection(section.id)
                        }
                        activeGoal={activeGoal}
                        onGoalSelect={selectGoal}
                    />
                ))}
            </div>
        </div>
    );
}


export default ContinuityViewer;
"""


write(MODULE, MODULE_CONTENT)


# ------------------------------------------------------------
# UPDATE MODULE REGISTRY
# ------------------------------------------------------------

registry_import = (
    "import ContinuityViewer "
    "from './modules/continuity-viewer/ContinuityViewer';\n"
)

registry_export = r"""
export const INSTANCE_MODULE_DEFINITIONS = [
    {
        id: 'continuity-viewer',
        name: 'Continuity',
        icon: 'C',
        component: ContinuityViewer
    }
];

export function getInstanceModuleDefinitions() {
    return INSTANCE_MODULE_DEFINITIONS;
}
"""

registry = registry_import + "\n" + registry + "\n" + registry_export
write(REGISTRY, registry)


# ------------------------------------------------------------
# UPDATE APP
# ------------------------------------------------------------

old_app_imports = (
    "import Settings from './components/settings/Settings';"
)

new_app_imports = (
    "import Settings from './components/settings/Settings';\n"
    "import { getInstanceModuleDefinitions } "
    "from '../instance/moduleRegistry';"
)

if old_app_imports not in app:
    fail("Could not locate the expected Settings import in App.jsx.")

app = app.replace(
    old_app_imports,
    new_app_imports,
    1
)


old_return = """        return (
            <Home
                onSettings={() =>
                    setView('settings')
                }
                modules={modules}
            />
        );"""

new_return = """        return (
            <Home
                onSettings={() =>
                    setView('settings')
                }
                modules={modules}
                onOpenModule={moduleId => {
                    if (moduleId === 'continuity-viewer') {
                        setView('module');
                    }
                }}
            />
        );"""

if old_return not in app:
    fail("Could not locate the expected Home render in App.jsx.")

app = app.replace(
    old_return,
    new_return,
    1
)


old_settings_return = """    return (
        <Settings

            page={page}"""

new_settings_return = """    if (view === 'module') {
        const definitions =
            getInstanceModuleDefinitions();

        const continuity =
            definitions.find(
                module =>
                    module.id === 'continuity-viewer'
            );

        if (!continuity) {
            return null;
        }

        const ModuleComponent =
            continuity.component;

        return (
            <div className="shell">
                <main className="main">
                    <button
                        type="button"
                        className="settings-home-button"
                        onClick={() =>
                            setView('home')
                        }
                    >
                        ← Home
                    </button>

                    <ModuleComponent />
                </main>
            </div>
        );
    }

    return (
        <Settings

            page={page}"""

if old_settings_return not in app:
    fail("Could not locate the expected Settings return in App.jsx.")

app = app.replace(
    old_settings_return,
    new_settings_return,
    1
)

write(APP, app)


# ------------------------------------------------------------
# UPDATE HOME / LAUNCHER OPENING BEHAVIOR
# ------------------------------------------------------------

home_path = CORE / "components" / "home" / "Home.jsx"
require_file(home_path)

home = read(home_path)

if "function Home({ onSettings, modules })" not in home:
    fail("Unexpected Home.jsx foundation.")

home = home.replace(
    "function Home({ onSettings, modules })",
    "function Home({ onSettings, modules, onOpenModule })",
    1
)

home = home.replace(
    """            <Launcher
                modules={modules}
            />""",
    """            <Launcher
                modules={modules}
                onOpenModule={onOpenModule}
            />""",
    1
)

backup(home_path)
write(home_path, home)


# ------------------------------------------------------------
# UPDATE LAUNCHER
# ------------------------------------------------------------

if "function Launcher({ modules })" not in launcher:
    fail("Unexpected Launcher.jsx function signature.")

launcher = launcher.replace(
    "function Launcher({ modules })",
    "function Launcher({ modules, onOpenModule })",
    1
)


old_keydown = """            if (
                key === 'arrowright' ||
                key === 'd'
            ) {
                event.preventDefault();
            }"""

new_keydown = """            if (
                key === 'arrowright' ||
                key === 'd'
            ) {
                event.preventDefault();
                moveHorizontal(1);
                return;
            }

            if (
                key === 'enter' ||
                key === ' '
            ) {
                event.preventDefault();

                if (selectedModule && onOpenModule) {
                    onOpenModule(selectedModule.id);
                }
            }"""

if old_keydown not in launcher:
    fail(
        "Could not locate the expected keyboard-navigation "
        "section in Launcher.jsx."
    )

launcher = launcher.replace(
    old_keydown,
    new_keydown,
    1
)


old_card_click = """    const handleCardClick = index => {
        if (index < selectedIndex) {
            moveHorizontal(-1);
            return;
        }

        if (index > selectedIndex) {
            moveHorizontal(1);
        }
    };"""

new_card_click = """    const handleCardClick = index => {
        if (index < selectedIndex) {
            moveHorizontal(-1);
            return;
        }

        if (index > selectedIndex) {
            moveHorizontal(1);
            return;
        }

        const module = enabledModules[index];

        if (module && onOpenModule) {
            onOpenModule(module.id);
        }
    };"""

if old_card_click not in launcher:
    fail(
        "Could not locate the expected card-click behavior "
        "in Launcher.jsx."
    )

launcher = launcher.replace(
    old_card_click,
    new_card_click,
    1
)

write(LAUNCHER, launcher)


# ------------------------------------------------------------
# UPDATE CSS
# ------------------------------------------------------------

CSS_APPEND = r"""

/* ========================================
   CONTINUITY VIEWER INSTANCE MODULE
   ======================================== */

.continuity-viewer {
    display: flex;
    flex-direction: column;
    gap: 14px;
    padding-top: 28px;
}

.continuity-toolbar {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    gap: 20px;
}

.continuity-toolbar-actions {
    display: flex;
    gap: 7px;
}

.continuity-summary {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 8px;
}

.continuity-summary > div {
    border: 1px solid var(--theme-border);
    border-radius: 7px;
    background: var(--theme-bg-control);
    padding: 11px 13px;
}

.continuity-summary span {
    display: block;
    color: var(--theme-text-muted);
    font-size: 8px;
    letter-spacing: 0.12em;
    font-weight: 600;
}

.continuity-summary strong {
    display: block;
    margin-top: 5px;
    color: var(--theme-text-primary);
    font-size: 12px;
    font-weight: 600;
}

.continuity-sections {
    display: flex;
    flex-direction: column;
    gap: 8px;
}

.continuity-section {
    border: 1px solid var(--theme-border);
    border-radius: 9px;
    background: var(--theme-bg-panel);
    overflow: hidden;
}

.continuity-section-header {
    width: 100%;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 15px;
    border: 0;
    padding: 16px 18px;
    background: transparent;
    color: var(--theme-text-primary);
    text-align: left;
    cursor: pointer;
}

.continuity-section-header:hover {
    background: var(--theme-bg-control);
}

.continuity-section-title {
    font-size: 13px;
    font-weight: 600;
}

.continuity-section-toggle {
    color: var(--theme-text-muted);
    font-size: 18px;
    line-height: 1;
}

.continuity-section-body {
    border-top: 1px solid var(--theme-border);
    padding: 14px;
    display: flex;
    flex-direction: column;
    gap: 8px;
}

.continuity-description {
    margin: 0 3px 5px;
}

.continuity-detail,
.continuity-item,
.continuity-phase-card,
.continuity-goal {
    border: 1px solid var(--theme-border);
    border-radius: 7px;
    background: var(--theme-bg-control);
    padding: 13px 15px;
}

.continuity-item p,
.continuity-phase-card p,
.continuity-goal p {
    margin-top: 5px;
}

.continuity-goal.active {
    border-color: var(--theme-border-strong);
}

.continuity-goal-header,
.continuity-phase-card-head {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 15px;
}

.continuity-goal-header > div {
    display: flex;
    align-items: center;
    gap: 9px;
}

.continuity-status {
    display: inline-block;
    padding: 4px 7px;
    border: 1px solid var(--theme-border);
    border-radius: 4px;
    color: var(--theme-text-muted);
    font-size: 8px;
    letter-spacing: 0.08em;
    text-transform: uppercase;
}

.continuity-phase-list {
    display: flex;
    flex-direction: column;
    gap: 5px;
    margin-top: 12px;
}

.continuity-phase {
    display: flex;
    align-items: center;
    gap: 10px;
    border-top: 1px solid var(--theme-border);
    padding-top: 9px;
    color: var(--theme-text-secondary);
    font-size: 10px;
}

.continuity-phase > span {
    width: 22px;
    height: 22px;
    flex: 0 0 auto;
    display: grid;
    place-items: center;
    border: 1px solid var(--theme-border);
    border-radius: 5px;
    color: var(--theme-text-muted);
}

.continuity-phase strong {
    display: block;
    margin-top: 2px;
    color: var(--theme-text-primary);
    font-size: 11px;
}

.continuity-phase-card p {
    margin-bottom: 0;
}
"""

if ".continuity-viewer" in styles:
    fail("Continuity Viewer styles already exist.")

styles += CSS_APPEND
write(STYLES, styles)


# ------------------------------------------------------------
# VERIFY
# ------------------------------------------------------------

checks = {
    "Continuity module exists": MODULE.exists(),
    "Registry imports module": "ContinuityViewer" in read(REGISTRY),
    "Registry defines module": "continuity-viewer" in read(REGISTRY),
    "App imports registry": "getInstanceModuleDefinitions" in read(APP),
    "App supports module view": "view === 'module'" in read(APP),
    "Home forwards module opener": "onOpenModule" in read(home_path),
    "Launcher opens selected module": "onOpenModule(module.id)" in read(LAUNCHER),
    "Enter launches selected module": "key === 'enter'" in read(LAUNCHER),
    "Continuity styles exist": ".continuity-viewer" in read(STYLES),
}

failed = [name for name, ok in checks.items() if not ok]

if failed:
    print("\nERROR")
    print("-----")
    print("Post-modification verification failed:")
    for item in failed:
        print(f"  - {item}")
    print("\nBackups were created before modification.")
    sys.exit(1)


print("\nSUCCESS")
print("-------")
print("Continuity Viewer instance module created and integrated.")

print("\nCreated:")
print(f"  {MODULE}")

print("\nModified:")
print(f"  {REGISTRY}")
print(f"  {APP}")
print(f"  {home_path}")
print(f"  {LAUNCHER}")
print(f"  {STYLES}")

print("\nBackups:")
for item in backups:
    print(f"  {item}")

print("\nBehavior:")
print("  - Continuity is an instance-level module.")
print("  - Launcher cards still navigate horizontally.")
print("  - Clicking the selected card opens the module.")
print("  - Enter/Space opens the selected module.")
print("  - Sections can be individually opened/closed.")
print("  - Open All / Close All controls are available.")
print("  - Goals contain nested phases.")
print("  - A goal can be marked as the active goal.")
print("  - Active goal selection persists in localStorage.")

print("\nThe WebApp-2 core does not contain the continuity document itself.")