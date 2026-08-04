from pathlib import Path
import shutil
import sys


# ============================================================
# Paths
# ============================================================

ROOT = Path(__file__).resolve().parent.parent

PACKAGE_DIR = (
    ROOT
    / "frontend"
    / "src"
    / "modules"
    / "package-manager"
)

MAIN_FILE = PACKAGE_DIR / "PackageManager.jsx"
COMPONENT_DIR = PACKAGE_DIR / "components"

BACKUP_FILE = (
    PACKAGE_DIR
    / "PackageManager.jsx.before-v3"
)


# ============================================================
# Safety helpers
# ============================================================

def fail(message):
    print()
    print("ERROR:")
    print(message)
    print()
    print("No source files were modified.")
    sys.exit(1)


def require_once(text, marker, description):
    count = text.count(marker)

    if count != 1:
        fail(
            f"Expected exactly one occurrence of {description}, "
            f"but found {count}."
        )


def replace_once(text, old, new, description):
    count = text.count(old)

    if count != 1:
        fail(
            f"Expected exactly one occurrence of {description}, "
            f"but found {count}."
        )

    return text.replace(old, new, 1)


# ============================================================
# Locate project
# ============================================================

if not MAIN_FILE.exists():
    fail(
        "PackageManager.jsx was not found at:\n"
        f"  {MAIN_FILE}"
    )


source = MAIN_FILE.read_text(encoding="utf-8")


# ============================================================
# Validate v2 structure
# ============================================================

required_markers = [
    "import ManagerSelector from './components/ManagerSelector';",
    "import SoftwareInventory from './components/SoftwareInventory';",
    "function Packages({ managers })",
    "export default Packages;",
]


for marker in required_markers:

    if marker not in source:
        fail(
            "The expected v2 PackageManager structure was not found.\n"
            f"Missing:\n  {marker}"
        )


# ============================================================
# Backup
# ============================================================

if not BACKUP_FILE.exists():

    shutil.copy2(
        MAIN_FILE,
        BACKUP_FILE
    )

    print(
        "Created backup:\n"
        f"  {BACKUP_FILE}"
    )

else:

    print(
        "Existing v3 backup found:\n"
        f"  {BACKUP_FILE}"
    )


# ============================================================
# Structural JSX extraction
# ============================================================

SECTION_MARKER = '<section className="panel">'


def find_matching_section(text, start):
    """
    Find the closing </section> corresponding to a
    <section className="panel">.

    This does not depend on indentation.
    """

    depth = 0
    position = start

    while position < len(text):

        next_open = text.find("<section", position)
        next_close = text.find("</section>", position)

        if next_close == -1:
            fail(
                "Found a package-manager <section> without "
                "a corresponding </section>."
            )

        if (
            next_open != -1
            and next_open < next_close
        ):
            depth += 1
            position = next_open + len("<section")

        else:
            depth -= 1
            position = next_close + len("</section>")

            if depth == 0:
                return position


def find_top_level_panels(text):
    """
    Locate the package manager's panel sections.

    The v2 structure should leave exactly one panel in
    PackageManager.jsx: the package search panel.
    """

    positions = []
    position = 0

    while True:

        index = text.find(
            SECTION_MARKER,
            position
        )

        if index == -1:
            break

        positions.append(index)

        position = (
            index
            + len(SECTION_MARKER)
        )

    return positions


panel_positions = find_top_level_panels(source)


if len(panel_positions) != 1:
    fail(
        "Expected exactly one remaining panel in "
        "PackageManager.jsx after v2.\n"
        f"Found {len(panel_positions)}."
    )


search_start = panel_positions[0]

search_end = find_matching_section(
    source,
    search_start
)

search_section = source[
    search_start:search_end
]


# ============================================================
# Confirm this is actually Package Search
# ============================================================

search_markers = [
    "PACKAGE SEARCH",
    "setSearchOpen",
    "setQuery",
    "selectedPackages",
]


for marker in search_markers:

    if marker not in search_section:
        fail(
            "The remaining panel does not appear to be "
            "the expected Package Search panel.\n"
            f"Missing marker:\n  {marker}"
        )


# ============================================================
# Build PackageSearch.jsx
# ============================================================

package_search = search_section


# Parent state → component callbacks.

package_search = package_search.replace(
    "setSearchOpen(!searchOpen)",
    "onToggleOpen()"
)

package_search = package_search.replace(
    "setSelected(e.target.value)",
    "onSelectManager(e.target.value)"
)

package_search = package_search.replace(
    "setQuery(e.target.value)",
    "onQueryChange(e.target.value)"
)

package_search = package_search.replace(
    "{searchOpen &&",
    "{open &&"
)

package_search = package_search.replace(
    "{searchOpen ? '▼' : '▶'}",
    "{open ? '▼' : '▶'}"
)


# Search actions.

package_search = package_search.replace(
    "search()",
    "onSearch()"
)

package_search = package_search.replace(
    "setResult(null)",
    "onClearResult()"
)

package_search = package_search.replace(
    "setResultsHidden(!resultsHidden)",
    "onToggleResults()"
)

package_search = package_search.replace(
    "setSelectedPackages([])",
    "onClearSelection()"
)


# Selection/download actions.

package_search = package_search.replace(
    "selectAllPackages()",
    "onSelectAll()"
)

package_search = package_search.replace(
    "clearPackageSelection()",
    "onClearSelection()"
)

package_search = package_search.replace(
    "downloadSelectedPackages()",
    "onDownloadSelected()"
)


# Package-specific selection.

package_search = package_search.replace(
    "togglePackageSelection(pkg)",
    "onTogglePackageSelection(pkg)"
)


# Download state.

package_search = package_search.replace(
    "setDownloadState(null)",
    "onClearDownload()"
)

package_search = package_search.replace(
    "confirmDownload()",
    "onConfirmDownload()"
)


# ============================================================
# Component wrapper
# ============================================================

package_search_component = f"""import React from 'react';

function PackageSearch({{
    managers,

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
}}) {{
    return (
{package_search}
    );
}}

export default PackageSearch;
"""


# ============================================================
# Validate generated component
# ============================================================

component_markers = [
    "function PackageSearch({",
    "export default PackageSearch;",
    "onSearch",
    "onSelectManager",
    "onQueryChange",
    "onToggleResults",
    "onSelectAll",
    "onClearSelection",
    "onDownloadSelected",
    "onTogglePackageSelection",
]


for marker in component_markers:

    if marker not in package_search_component:
        fail(
            "Generated PackageSearch.jsx failed validation.\n"
            f"Missing:\n  {marker}"
        )


# These parent setters should not remain inside the new component.

for forbidden in [
    "setSearchOpen",
    "setSelected(",
    "setQuery(",
    "setSelectedPackages(",
]:

    if forbidden in package_search_component:

        fail(
            "Generated PackageSearch.jsx still contains "
            f"parent state operation:\n  {forbidden}"
        )


# ============================================================
# Build parent replacement
# ============================================================

package_search_import = (
    "import PackageSearch "
    "from './components/PackageSearch';\n"
)


package_search_usage = """            <PackageSearch
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
            />"""


# ============================================================
# Modify parent in memory
# ============================================================

new_source = source


# Add import.

import_anchor = (
    "import SoftwareInventory "
    "from './components/SoftwareInventory';"
)


require_once(
    new_source,
    import_anchor,
    "SoftwareInventory import"
)


new_source = new_source.replace(
    import_anchor,
    import_anchor
    + "\n"
    + package_search_import.rstrip(),
    1
)


# Replace search panel.

new_source = replace_once(
    new_source,
    search_section,
    package_search_usage,
    "package search panel"
)


# ============================================================
# Validate resulting parent
# ============================================================

parent_markers = [
    "import ManagerSelector from './components/ManagerSelector';",
    "import SoftwareInventory from './components/SoftwareInventory';",
    "import PackageSearch from './components/PackageSearch';",

    "<ManagerSelector",
    "<PackageSearch",
    "<SoftwareInventory",

    "function Packages({ managers })",

    "async function search()",
    "async function confirmDownload",
    "async function downloadSelectedPackages",

    "setSearchOpen",
    "setSelectedPackages",
    "setDownloadState",

    "export default Packages;",
]


for marker in parent_markers:

    if marker not in new_source:
        fail(
            "Resulting PackageManager.jsx failed validation.\n"
            f"Missing:\n  {marker}"
        )


# ============================================================
# Ensure exactly three modular components are referenced
# ============================================================

expected_imports = [
    "import ManagerSelector",
    "import SoftwareInventory",
    "import PackageSearch",
]


for marker in expected_imports:

    if new_source.count(marker) != 1:

        fail(
            "Expected exactly one import for:\n"
            f"  {marker}"
        )


# ============================================================
# Ensure no package-search panel remains inline
# ============================================================

if new_source.count(
    '<section className="panel">'
) != 0:

    fail(
        "A <section className=\"panel\"> remains in "
        "PackageManager.jsx after extraction."
    )


# ============================================================
# Ensure generated file isn't empty
# ============================================================

if not package_search_component.strip():

    fail(
        "Generated PackageSearch.jsx is empty."
    )


# ============================================================
# Write
# ============================================================

COMPONENT_DIR.mkdir(
    parents=True,
    exist_ok=True
)


PACKAGE_SEARCH_FILE = (
    COMPONENT_DIR
    / "PackageSearch.jsx"
)


PACKAGE_SEARCH_FILE.write_text(
    package_search_component,
    encoding="utf-8"
)


MAIN_FILE.write_text(
    new_source,
    encoding="utf-8"
)


# ============================================================
# Report
# ============================================================

print()
print("=" * 60)
print("PACKAGE MANAGER MODULARIZATION V3 COMPLETE")
print("=" * 60)
print()

print("Created:")
print(
    "  frontend/src/modules/package-manager/"
    "components/PackageSearch.jsx"
)
print()

print("Updated:")
print(
    "  frontend/src/modules/package-manager/"
    "PackageManager.jsx"
)
print()

print("Backup:")
print(
    "  frontend/src/modules/package-manager/"
    "PackageManager.jsx.before-v3"
)
print()

print("The parent retains:")
print("  - package-manager state")
print("  - search()")
print("  - downloadSelectedPackages()")
print("  - confirmDownload()")
print("  - API interaction")
print()

print("The search UI is now isolated in:")
print("  PackageSearch.jsx")
print()

print("No packages installed.")
print("No backend files changed.")
print("No external services contacted.")
print()

print("Next:")
print("  cd frontend")
print("  npm run build")
print()