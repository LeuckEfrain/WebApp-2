from pathlib import Path
import re
import shutil
import sys


# ============================================================
# Paths
# ============================================================

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "frontend" / "src"

MAIN = SRC / "main.jsx"
BACKUP = SRC / "main.jsx.before-modularization"


# ============================================================
# Safety
# ============================================================

if not BACKUP.exists():
    if not MAIN.exists():
        print("ERROR: frontend/src/main.jsx was not found.")
        sys.exit(1)

    print("Creating original-source backup...")
    shutil.copy2(MAIN, BACKUP)

source = BACKUP.read_text(encoding="utf-8")

print(f"Using clean source:")
print(f"  {BACKUP}")
print()


# ============================================================
# Extract a function declaration
# ============================================================

def extract_function(text, name):
    """
    Extract a top-level JavaScript function declaration.

    Handles destructured parameters, nested braces, strings,
    template literals, and comments.
    """

    match = re.search(
        rf"(?m)^function\s+{re.escape(name)}\s*\(",
        text
    )

    if not match:
        raise RuntimeError(
            f"Could not find function '{name}'."
        )

    start = match.start()

    # --------------------------------------------------------
    # First find the end of the parameter list.
    # This is important because functions such as:
    #
    # function Stat({ title, value, detail }) {
    #
    # contain braces BEFORE the function body.
    # --------------------------------------------------------

    paren_depth = 0
    quote = None
    escaped = False
    line_comment = False
    block_comment = False

    i = match.end() - 1

    while i < len(text):

        char = text[i]
        nxt = text[i + 1] if i + 1 < len(text) else ""

        if line_comment:
            if char == "\n":
                line_comment = False

            i += 1
            continue

        if block_comment:
            if char == "*" and nxt == "/":
                block_comment = False
                i += 2
                continue

            i += 1
            continue

        if quote:
            if escaped:
                escaped = False

            elif char == "\\":
                escaped = True

            elif char == quote:
                quote = None

            i += 1
            continue

        if char == "/" and nxt == "/":
            line_comment = True
            i += 2
            continue

        if char == "/" and nxt == "*":
            block_comment = True
            i += 2
            continue

        if char in ("'", '"', "`"):
            quote = char
            i += 1
            continue

        if char == "(":
            paren_depth += 1

        elif char == ")":
            paren_depth -= 1

            if paren_depth == 0:
                break

        i += 1

    if paren_depth != 0:
        raise RuntimeError(
            f"Could not find the end of the parameter list "
            f"for '{name}'."
        )

    # --------------------------------------------------------
    # Now find the opening brace of the FUNCTION BODY.
    # --------------------------------------------------------

    body_start = text.find("{", i + 1)

    if body_start == -1:
        raise RuntimeError(
            f"Could not find function body for '{name}'."
        )

    # --------------------------------------------------------
    # Find the matching closing brace.
    # --------------------------------------------------------

    brace_depth = 0

    quote = None
    escaped = False
    line_comment = False
    block_comment = False

    i = body_start

    while i < len(text):

        char = text[i]
        nxt = text[i + 1] if i + 1 < len(text) else ""

        if line_comment:
            if char == "\n":
                line_comment = False

            i += 1
            continue

        if block_comment:
            if char == "*" and nxt == "/":
                block_comment = False
                i += 2
                continue

            i += 1
            continue

        if quote:
            if escaped:
                escaped = False

            elif char == "\\":
                escaped = True

            elif char == quote:
                quote = None

            i += 1
            continue

        if char == "/" and nxt == "/":
            line_comment = True
            i += 2
            continue

        if char == "/" and nxt == "*":
            block_comment = True
            i += 2
            continue

        if char in ("'", '"', "`"):
            quote = char
            i += 1
            continue

        if char == "{":
            brace_depth += 1

        elif char == "}":
            brace_depth -= 1

            if brace_depth == 0:
                return text[start:i + 1]

        i += 1

    raise RuntimeError(
        f"Could not find closing brace for '{name}'."
    )

# ============================================================
# Extract
# ============================================================

print("Extracting existing declarations...")

try:

    nav = extract_function(source, "Nav")
    app = extract_function(source, "App")

    normalize = extract_function(
        source,
        "normalizePackageResults"
    )

    parse = extract_function(
        source,
        "parseCommandLineResults"
    )

    relevance = extract_function(
        source,
        "relevanceScore"
    )

    rank = extract_function(
        source,
        "rankPackageResults"
    )

    best_source = extract_function(
        source,
        "determineBestSource"
    )

    dashboard = extract_function(
        source,
        "Dashboard"
    )

    stat = extract_function(
        source,
        "Stat"
    )

    packages = extract_function(
        source,
        "Packages"
    )

except RuntimeError as error:

    print()
    print("ERROR:")
    print(error)
    print()
    print("Nothing was modified.")
    sys.exit(1)


print("All declarations found.")
print()


# ============================================================
# Create directories
# ============================================================

components = SRC / "components"

package_module = (
    SRC /
    "modules" /
    "package-manager"
)

components.mkdir(
    parents=True,
    exist_ok=True
)

package_module.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# Nav.jsx
# ============================================================

(components / "Nav.jsx").write_text(
    """import React from 'react';

{body}
""".format(body=nav),
    encoding="utf-8"
)


# ============================================================
# Stat.jsx
# ============================================================

(components / "Stat.jsx").write_text(
    """import React from 'react';

{body}
""".format(body=stat),
    encoding="utf-8"
)


# ============================================================
# Dashboard.jsx
# ============================================================

(components / "Dashboard.jsx").write_text(
    """import React from 'react';

import Stat from './Stat';

{body}
""".format(body=dashboard),
    encoding="utf-8"
)


# ============================================================
# packageUtils.js
# ============================================================

(package_module / "packageUtils.js").write_text(
    """{normalize}

{parse}

{relevance}

{rank}

{best_source}

export {{
    normalizePackageResults,
    parseCommandLineResults,
    relevanceScore,
    rankPackageResults,
    determineBestSource
}};
""".format(
        normalize=normalize,
        parse=parse,
        relevance=relevance,
        rank=rank,
        best_source=best_source
    ),
    encoding="utf-8"
)


# ============================================================
# PackageManager.jsx
# ============================================================

(package_module / "PackageManager.jsx").write_text(
    """import React, {{ useEffect, useState }} from 'react';

import {{
    normalizePackageResults,
    rankPackageResults,
    determineBestSource
}} from './packageUtils';

const API = 'http://127.0.0.1:8000';

{body}
""".format(body=packages),
    encoding="utf-8"
)


# ============================================================
# App.jsx
# ============================================================

(components / "App.jsx").write_text(
    """import React, {{ useEffect, useState }} from 'react';

import Nav from './Nav';
import Dashboard from './Dashboard';
import PackageManager from '../modules/package-manager/PackageManager';

const API = 'http://127.0.0.1:8000';

{body}
""".format(
        body=app.replace(
            "<Packages managers={managers} />",
            "<PackageManager managers={managers} />"
        )
    ),
    encoding="utf-8"
)


# ============================================================
# main.jsx
# ============================================================

MAIN.write_text(
    """import React from 'react';
import {{ createRoot }} from 'react-dom/client';

import App from './components/App';

import './styles.css';

createRoot(document.getElementById('root')).render(
    <React.StrictMode>
        <App />
    </React.StrictMode>
);
""".replace("{{", "{").replace("}}", "}"),
    encoding="utf-8"
)


# ============================================================
# Verification
# ============================================================

files = [
    components / "App.jsx",
    components / "Nav.jsx",
    components / "Dashboard.jsx",
    components / "Stat.jsx",
    package_module / "PackageManager.jsx",
    package_module / "packageUtils.js",
    MAIN,
]

print()
print("Created files:")
print()

for file in files:

    size = file.stat().st_size

    print(
        f"  {file.relative_to(ROOT)}"
        f"  ({size:,} bytes)"
    )


print()
print("Original source:")
print(
    f"  {BACKUP.relative_to(ROOT)}"
)

print()
print("Modularization complete.")
print()
print("No npm packages were added.")
print("No backend files were changed.")
print("No external APIs were used.")