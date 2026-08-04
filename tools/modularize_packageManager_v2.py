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
BACKUP_FILE = PACKAGE_DIR / "PackageManager.jsx.before-v2"


# ============================================================
# Safety
# ============================================================

if not MAIN_FILE.exists():
    print("ERROR: PackageManager.jsx was not found.")
    sys.exit(1)


source = MAIN_FILE.read_text(encoding="utf-8")


required = [
    "function Packages({ managers })",
    "const [managersOpen",
    "const [inventoryOpen",
    "export default Packages;",
]

for marker in required:
    if marker not in source:
        print()
        print("ERROR: Expected source marker was not found:")
        print(f"  {marker}")
        print()
        print("No files were modified.")
        sys.exit(1)


# ============================================================
# Backup
# ============================================================

if not BACKUP_FILE.exists():
    shutil.copy2(MAIN_FILE, BACKUP_FILE)
    print(f"Created backup: {BACKUP_FILE}")
else:
    print(f"Backup already exists: {BACKUP_FILE}")


# ============================================================
# JSX section extraction
# ============================================================

def find_panel_sections(text):
    """
    Find top-level <section className="panel"> blocks.

    This intentionally does NOT depend on indentation or exact
    whitespace.
    """

    marker = '<section className="panel">'

    starts = []
    position = 0

    while True:
        index = text.find(marker, position)

        if index == -1:
            break

        starts.append(index)
        position = index + len(marker)

    if len(starts) != 3:
        raise RuntimeError(
            f"Expected exactly 3 package-manager panels, "
            f"found {len(starts)}."
        )

    sections = []

    for start in starts:

        depth = 0
        position = start

        while position < len(text):

            next_open = text.find("<section", position)
            next_close = text.find("</section>", position)

            if next_close == -1:
                raise RuntimeError(
                    "A package-manager panel has no closing "
                    "</section> tag."
                )

            if next_open != -1 and next_open < next_close:
                depth += 1
                position = next_open + len("<section")
            else:
                depth -= 1
                position = next_close + len("</section>")

                if depth == 0:
                    sections.append(
                        (
                            start,
                            position,
                            text[start:position]
                        )
                    )
                    break

    return sections


sections = find_panel_sections(source)

manager_start, manager_end, manager_section = sections[0]
search_start, search_end, search_section = sections[1]
inventory_start, inventory_end, inventory_section = sections[2]


# ============================================================
# Verify ordering
# ============================================================

if not (
    manager_start
    < manager_end
    <= search_start
    < search_end
    <= inventory_start
    < inventory_end
):
    raise RuntimeError(
        "Panel ordering did not match the expected "
        "PackageManager structure."
    )


# ============================================================
# Component helpers
# ============================================================

def replace_once(text, old, new, description):
    count = text.count(old)

    if count != 1:
        raise RuntimeError(
            f"Expected exactly one occurrence of {description}, "
            f"found {count}."
        )

    return text.replace(old, new, 1)


# ============================================================
# ManagerSelector
# ============================================================

manager_component = manager_section

manager_component = manager_component.replace(
    "setManagersOpen(!managersOpen)",
    "onToggleOpen()"
)

manager_component = manager_component.replace(
    "setSelected(m.id)",
    "onSelect(m.id)"
)

manager_component = manager_component.replace(
    "{managersOpen &&",
    "{open &&"
)

manager_component = manager_component.replace(
    "{managersOpen ? '▼' : '▶'}",
    "{open ? '▼' : '▶'}"
)


manager_component = f"""import React from 'react';

function ManagerSelector({{
    managers,
    selected,
    open,
    onSelect,
    onToggleOpen
}}) {{
    return (
{manager_component}
    );
}}

export default ManagerSelector;
"""


# ============================================================
# SoftwareInventory
# ============================================================

inventory_component = inventory_section

inventory_component = inventory_component.replace(
    "setInventoryOpen(!inventoryOpen)",
    "onToggleOpen()"
)

inventory_component = inventory_component.replace(
    "{inventoryOpen &&",
    "{open &&"
)

inventory_component = inventory_component.replace(
    "{inventoryOpen ? '▼' : '▶'}",
    "{open ? '▼' : '▶'}"
)


inventory_component = f"""import React from 'react';

function SoftwareInventory({{
    inventory,
    open,
    onToggleOpen
}}) {{
    return (
{inventory_component}
    );
}}

export default SoftwareInventory;
"""


# ============================================================
# Validate generated components
# ============================================================

if "export default ManagerSelector;" not in manager_component:
    raise RuntimeError(
        "ManagerSelector.jsx failed export validation."
    )

if "export default SoftwareInventory;" not in inventory_component:
    raise RuntimeError(
        "SoftwareInventory.jsx failed export validation."
    )

if "setManagersOpen" in manager_component:
    raise RuntimeError(
        "ManagerSelector.jsx still contains parent state setter."
    )

if "setInventoryOpen" in inventory_component:
    raise RuntimeError(
        "SoftwareInventory.jsx still contains parent state setter."
    )


# ============================================================
# Build parent replacements
# ============================================================

manager_import = (
    "import ManagerSelector "
    "from './components/ManagerSelector';\n"
)

inventory_import = (
    "import SoftwareInventory "
    "from './components/SoftwareInventory';\n"
)


manager_usage = """            <ManagerSelector
                managers={managers}
                selected={selected}
                open={managersOpen}
                onSelect={setSelected}
                onToggleOpen={() =>
                    setManagersOpen(!managersOpen)
                }
            />"""


inventory_usage = """            <SoftwareInventory
                inventory={inventory}
                open={inventoryOpen}
                onToggleOpen={() =>
                    setInventoryOpen(!inventoryOpen)
                }
            />"""


new_source = source


# Add imports after packageUtils import block.

import_anchor = """} from './packageUtils';

"""

if new_source.count(import_anchor) != 1:
    raise RuntimeError(
        "Could not safely locate packageUtils import block."
    )

new_source = new_source.replace(
    import_anchor,
    import_anchor
    + manager_import
    + inventory_import
    + "\n",
    1
)


# Replace manager panel.

new_source = new_source.replace(
    manager_section,
    manager_usage,
    1
)


# Replace inventory panel.

new_source = new_source.replace(
    inventory_section,
    inventory_usage,
    1
)


# ============================================================
# Validate parent
# ============================================================

required_parent_markers = [
    "import ManagerSelector from './components/ManagerSelector';",
    "import SoftwareInventory from './components/SoftwareInventory';",
    "<ManagerSelector",
    "<SoftwareInventory",
    "function Packages({ managers })",
    "const [managersOpen",
    "const [inventoryOpen",
    "export default Packages;",
]

for marker in required_parent_markers:
    if marker not in new_source:
        raise RuntimeError(
            "Parent validation failed. Missing:"
            f"\n  {marker}"
        )


# The old panels should no longer exist in the parent.

if new_source.count('<section className="panel">') != 1:
    raise RuntimeError(
        "Expected exactly one remaining panel in "
        "PackageManager.jsx after extraction."
    )


# ============================================================
# Ensure only expected files will be written
# ============================================================

COMPONENT_DIR.mkdir(
    parents=True,
    exist_ok=True
)

files_to_write = {
    COMPONENT_DIR / "ManagerSelector.jsx": manager_component,
    COMPONENT_DIR / "SoftwareInventory.jsx": inventory_component,
    MAIN_FILE: new_source,
}


for path, content in files_to_write.items():

    if not content.strip():
        raise RuntimeError(
            f"Refusing to write empty file: {path}"
        )


# ============================================================
# Write
# ============================================================

for path, content in files_to_write.items():

    path.write_text(
        content,
        encoding="utf-8"
    )


# ============================================================
# Report
# ============================================================

print()
print("=" * 60)
print("PACKAGE MANAGER MODULARIZATION V2 COMPLETE")
print("=" * 60)
print()

print("Created:")
print("  frontend/src/modules/package-manager/components/")
print("    ManagerSelector.jsx")
print("    SoftwareInventory.jsx")
print()

print("Updated:")
print("  frontend/src/modules/package-manager/PackageManager.jsx")
print()

print("Unchanged:")
print("  frontend/src/modules/package-manager/packageUtils.js")
print()

print("Backup:")
print("  PackageManager.jsx.before-v2")
print()

print("The package-search panel was intentionally left intact.")
print()

print("No packages installed.")
print("No backend files changed.")
print("No external services contacted.")
print()

print("Next:")
print("  cd frontend")
print("  npm run build")
print()