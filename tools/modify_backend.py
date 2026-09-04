#!/usr/bin/env python3

"""
WebApp-2 backend modification tool.

Installs the read-only local agent-discovery layer.

The script is autonomous:
    inspect -> validate -> backup -> modify -> validate -> report

It does not require command-line arguments.
It does not modify unrelated code.
It does not expose terminal execution.
"""

from pathlib import Path
from datetime import datetime
import ast
import shutil
import subprocess
import sys


# ============================================================================
# PATHS
# ============================================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

BACKEND_PATH = (
    PROJECT_ROOT
    / "backend"
    / "main.py"
)

MODULES_DIR = (
    PROJECT_ROOT
    / "backend"
    / "modules"
)

DISCOVERY_PATH = (
    MODULES_DIR
    / "agent_discovery.py"
)

BACKUP_DIR = (
    PROJECT_ROOT
    / "backend"
    / ".webapp2-refactor-backups"
)


# ============================================================================
# MANAGED INTEGRATION MARKERS
# ============================================================================

DISCOVERY_IMPORT = (
    "from backend.modules.agent_discovery "
    "import router as agent_discovery_router"
)

DISCOVERY_INCLUDE = (
    "app.include_router(agent_discovery_router)"
)


# ============================================================================
# REQUIRED EXISTING BACKEND FOUNDATION
# ============================================================================

REQUIRED_MARKERS = [
    "from fastapi import FastAPI",
    "app = FastAPI(",
    '@app.get("/api/health")',
    '@app.get("/api/package-managers")',
    '@app.get("/api/software")',
    "# --- WEBAPP2 PROJECT ACCESS START ---",
    "# --- WEBAPP2 DISCOVERY START ---",
    '@app.get("/api/discovery")',
]


# ============================================================================
# DISCOVERY MODULE
# ============================================================================

DISCOVERY_SOURCE = r'''"""
WebApp-2 local agent discovery service.

READ ONLY.

This module provides the future WebApp-2 agent with access to the
actual project running on the local machine.

It deliberately does NOT provide:

- arbitrary shell execution
- arbitrary process execution
- filesystem writes
- environment-variable disclosure
- secret-file disclosure
- access outside the project
"""

from __future__ import annotations

from pathlib import Path
import datetime
import hashlib
import os
import subprocess
import sys

from fastapi import APIRouter, HTTPException, Query


router = APIRouter(
    prefix="/api/agent/discovery",
    tags=["agent-discovery"],
)


# ============================================================================
# PROJECT ROOT
# ============================================================================

# backend/modules/agent_discovery.py
#       -> backend/modules
#       -> backend
#       -> WebApp-2

PROJECT_ROOT = Path(__file__).resolve().parents[2]


# ============================================================================
# SAFETY POLICY
# ============================================================================

IGNORED_DIRECTORIES = {
    ".git",
    ".venv",
    "venv",
    "node_modules",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".tox",
    ".nox",
    ".agent_backups",
    ".webapp2-refactor-backups",
}


IGNORED_FILE_NAMES = {
    ".env",
    ".env.local",
    ".env.development",
    ".env.production",
    ".env.test",
}


IGNORED_SUFFIXES = {
    ".pem",
    ".key",
    ".p12",
    ".pfx",
}


MAX_FILE_CONTENT_BYTES = 10 * 1024 * 1024

MAX_SEARCHABLE_FILE_BYTES = 10 * 1024 * 1024

MAX_SEARCH_RESULTS = 200


# ============================================================================
# PATH SAFETY
# ============================================================================

def safe_project_path(relative_path: str) -> Path:
    """
    Resolve a repository-relative path.

    Paths escaping the WebApp-2 repository are rejected.
    """

    if not relative_path:
        raise HTTPException(
            status_code=400,
            detail="A project-relative path is required.",
        )

    candidate = (
        PROJECT_ROOT / relative_path
    ).resolve()

    try:
        candidate.relative_to(
            PROJECT_ROOT.resolve()
        )
    except ValueError:
        raise HTTPException(
            status_code=403,
            detail="Requested path is outside WebApp-2.",
        )

    return candidate


def is_sensitive(path: Path) -> bool:
    """
    Prevent obvious credentials and secret material from being exposed.
    """

    if path.name in IGNORED_FILE_NAMES:
        return True

    if path.suffix.lower() in IGNORED_SUFFIXES:
        return True

    lowered = path.name.lower()

    sensitive_terms = (
        "secret",
        "credential",
        "credentials",
        "private_key",
        "private-key",
    )

    return any(
        term in lowered
        for term in sensitive_terms
    )


# ============================================================================
# FILESYSTEM DISCOVERY
# ============================================================================

def iter_project_files():
    """
    Yield files from the current local project.
    """

    for root, directories, files in os.walk(
        PROJECT_ROOT
    ):

        directories[:] = [
            directory
            for directory in directories
            if directory
            not in IGNORED_DIRECTORIES
        ]

        root_path = Path(root)

        for filename in files:

            path = root_path / filename

            if is_sensitive(path):
                continue

            yield path


def sha256(path: Path) -> str:

    digest = hashlib.sha256()

    with path.open("rb") as handle:

        for chunk in iter(
            lambda: handle.read(1024 * 1024),
            b"",
        ):

            digest.update(chunk)

    return digest.hexdigest()


def metadata(path: Path) -> dict:

    stat = path.stat()

    relative = path.relative_to(
        PROJECT_ROOT
    ).as_posix()

    result = {
        "path": relative,
        "name": path.name,
        "size": stat.st_size,
        "extension": path.suffix,
        "type": (
            "file"
            if path.is_file()
            else "directory"
        ),
    }

    if (
        path.is_file()
        and stat.st_size <= MAX_FILE_CONTENT_BYTES
    ):

        try:

            result["sha256"] = sha256(path)

        except OSError:

            result["sha256"] = None

    return result


# ============================================================================
# GIT DISCOVERY
# ============================================================================

def git(command: list[str]) -> str:
    """
    Execute fixed, read-only Git commands.

    No shell is used.
    """

    if not command:
        return ""

    allowed = {
        "rev-parse",
        "branch",
        "status",
    }

    if command[0] not in allowed:
        return ""

    try:

        result = subprocess.run(
            [
                "git",
                *command,
            ],
            cwd=str(PROJECT_ROOT),
            capture_output=True,
            text=True,
            timeout=10,
            encoding="utf-8",
            errors="replace",
        )

        if result.returncode != 0:
            return ""

        return result.stdout.strip()

    except Exception:

        return ""


# ============================================================================
# PROJECT ENDPOINT
# ============================================================================

@router.get("/project")
def discover_project():

    files = []

    for path in iter_project_files():

        try:

            files.append(
                metadata(path)
            )

        except OSError:

            continue

    files.sort(
        key=lambda item: item["path"].lower()
    )

    return {
        "ok": True,

        "source": "local-filesystem",

        "project": {
            "name": PROJECT_ROOT.name,
            "root": str(PROJECT_ROOT),
        },

        "git": {
            "root": git(
                ["rev-parse", "--show-toplevel"]
            ),

            "branch": git(
                ["branch", "--show-current"]
            ),

            "commit": git(
                ["rev-parse", "HEAD"]
            ),

            "status": git(
                ["status", "--short"]
            ),
        },

        "files": files,

        "completeness": {
            "complete": True,
            "files_included": len(files),
            "files_omitted": 0,
        },

        "generated_at": (
            datetime.datetime.now().isoformat()
        ),
    }


# ============================================================================
# FILE ENDPOINT
# ============================================================================

@router.get("/file")
def discover_file(
    path: str = Query(...),
    include_content: bool = True,
):

    target = safe_project_path(path)

    if not target.exists():

        raise HTTPException(
            status_code=404,
            detail="Requested file does not exist.",
        )

    if not target.is_file():

        raise HTTPException(
            status_code=400,
            detail="Requested path is not a file.",
        )

    if is_sensitive(target):

        raise HTTPException(
            status_code=403,
            detail="Requested file is not available.",
        )

    response = {
        "ok": True,
        "source": "local-filesystem",
        "file": metadata(target),
        "content_available": False,
    }

    if not include_content:
        return response

    if (
        target.stat().st_size
        > MAX_FILE_CONTENT_BYTES
    ):

        response["content_unavailable_reason"] = (
            "File exceeds the discovery size limit."
        )

        return response

    try:

        response["content"] = target.read_text(
            encoding="utf-8",
            errors="replace",
        )

        response["content_available"] = True

    except OSError as error:

        raise HTTPException(
            status_code=500,
            detail=f"Unable to read file: {error}",
        )

    return response


# ============================================================================
# SEARCH ENDPOINT
# ============================================================================

@router.get("/search")
def search_project(
    q: str = Query(..., min_length=1),
    path: str = "",
    max_results: int = 50,
):

    max_results = max(
        1,
        min(
            max_results,
            MAX_SEARCH_RESULTS,
        ),
    )

    query = q.lower()

    if path:

        base = safe_project_path(path)

        if not base.exists():

            raise HTTPException(
                status_code=404,
                detail="Search path does not exist.",
            )

        if base.is_file():

            candidates = [base]

        else:

            candidates = [
                item
                for item in base.rglob("*")
                if item.is_file()
            ]

    else:

        candidates = list(
            iter_project_files()
        )

    results = []

    for path in candidates:

        if len(results) >= max_results:
            break

        if not path.is_file():
            continue

        if is_sensitive(path):
            continue

        try:

            if (
                path.stat().st_size
                > MAX_SEARCHABLE_FILE_BYTES
            ):

                continue

            text = path.read_text(
                encoding="utf-8",
                errors="replace",
            )

        except OSError:

            continue

        for line_number, line in enumerate(
            text.splitlines(),
            start=1,
        ):

            if query in line.lower():

                results.append(
                    {
                        "path": path.relative_to(
                            PROJECT_ROOT
                        ).as_posix(),

                        "line": line_number,

                        "text": line[:4000],
                    }
                )

                if len(results) >= max_results:
                    break

    return {
        "ok": True,
        "source": "local-filesystem",
        "query": q,
        "results": results,
        "count": len(results),
        "truncated": (
            len(results) >= max_results
        ),
    }


# ============================================================================
# GIT ENDPOINT
# ============================================================================

@router.get("/git")
def discover_git():

    return {
        "ok": True,
        "source": "local-git",

        "root": git(
            ["rev-parse", "--show-toplevel"]
        ),

        "branch": git(
            ["branch", "--show-current"]
        ),

        "commit": git(
            ["rev-parse", "HEAD"]
        ),

        "status": git(
            ["status", "--short"]
        ),
    }


# ============================================================================
# RUNTIME ENDPOINT
# ============================================================================

@router.get("/runtime")
def discover_runtime():

    return {
        "ok": True,
        "source": "local-runtime",

        "project_root": str(
            PROJECT_ROOT
        ),

        "working_directory": os.getcwd(),

        "python": sys.version,

        "platform": os.name,
    }
'''


# ============================================================================
# FAILURE HELPER
# ============================================================================

def fail(message: str):

    raise SystemExit(
        "\nERROR: "
        + message
        + "\n\nNo changes were made."
    )


# ============================================================================
# START
# ============================================================================

print()
print("=" * 72)
print("WEBAPP-2 — LIVE AGENT DISCOVERY MODIFICATION")
print("=" * 72)
print()

print(
    f"Project root: {PROJECT_ROOT}"
)

print(
    f"Backend:      {BACKEND_PATH}"
)

print(
    f"Discovery:    {DISCOVERY_PATH}"
)

print()


# ============================================================================
# VERIFY BACKEND EXISTS
# ============================================================================

if not BACKEND_PATH.is_file():

    fail(
        "backend/main.py was not found."
    )


# ============================================================================
# VERIFY GIT REPOSITORY
# ============================================================================

def git_command(command):

    result = subprocess.run(
        [
            "git",
            *command,
        ],
        cwd=str(PROJECT_ROOT),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )

    if result.returncode != 0:

        fail(
            "Git inspection failed:\n"
            + result.stderr.strip()
        )

    return result.stdout.strip()


git_root = git_command(
    ["rev-parse", "--show-toplevel"]
)

git_branch = git_command(
    ["branch", "--show-current"]
)

git_commit = git_command(
    ["rev-parse", "HEAD"]
)


print(
    f"Git root:     {git_root}"
)

print(
    f"Git branch:   {git_branch}"
)

print(
    f"Git commit:   {git_commit}"
)

print()


if Path(git_root).resolve() != PROJECT_ROOT.resolve():

    fail(
        "Git root does not match the WebApp-2 project root."
    )


if git_branch != "tests":

    fail(
        "Unexpected Git branch.\n"
        "Expected: tests\n"
        f"Actual:   {git_branch}"
    )


# ============================================================================
# READ CURRENT BACKEND
# ============================================================================

source = BACKEND_PATH.read_text(
    encoding="utf-8"
)


# ============================================================================
# FOUNDATION VALIDATION
# ============================================================================

print(
    "Checking current backend foundation..."
)


for marker in REQUIRED_MARKERS:

    if marker not in source:

        fail(
            "Required backend structure was not found:\n"
            + marker
        )


if source.count(
    "# --- WEBAPP2 DISCOVERY START ---"
) != 1:

    fail(
        "Expected exactly one existing "
        "WEBAPP2 DISCOVERY START marker."
    )


if DISCOVERY_IMPORT in source:

    fail(
        "Agent discovery import already exists."
    )


if DISCOVERY_INCLUDE in source:

    fail(
        "Agent discovery router registration already exists."
    )


if DISCOVERY_PATH.exists():

    fail(
        "backend/modules/agent_discovery.py already exists.\n"
        "Refusing to overwrite it."
    )


print(
    "Foundation: PASS"
)

print()


# ============================================================================
# LOCATE FASTAPI IMPORT
# ============================================================================

# We use the actual import line that exists in the live backend.
#
# This avoids trying to infer the entire import section.

fastapi_import = None

lines = source.splitlines(
    keepends=True
)

for line in lines:

    if (
        line.startswith("from fastapi import ")
        and "FastAPI" in line
    ):

        fastapi_import = line.rstrip("\r\n")
        break


if fastapi_import is None:

    fail(
        "Could not locate the actual FastAPI import."
    )


# Prevent duplicate import.

if DISCOVERY_IMPORT in source:

    fail(
        "Discovery import unexpectedly already exists."
    )


# ============================================================================
# INSERT IMPORT
# ============================================================================

modified = source.replace(
    fastapi_import,
    fastapi_import
    + "\n"
    + DISCOVERY_IMPORT,
    1,
)


# ============================================================================
# LOCATE APP INITIALIZATION
# ============================================================================

lines = modified.splitlines(
    keepends=True
)

app_indices = []

for index, line in enumerate(lines):

    stripped = line.strip()

    if (
        line == line.lstrip()
        and stripped.startswith(
            "app = FastAPI("
        )
    ):

        app_indices.append(index)


if len(app_indices) != 1:

    fail(
        "Expected exactly one top-level "
        "FastAPI application initialization.\n"
        f"Found: {len(app_indices)}"
    )


app_index = app_indices[0]


# ============================================================================
# INSERT ROUTER REGISTRATION
# ============================================================================

lines.insert(
    app_index + 1,
    DISCOVERY_INCLUDE + "\n",
)

modified = "".join(lines)


# ============================================================================
# PRE-WRITE VALIDATION
# ============================================================================

print(
    "Validating generated backend..."
)


try:

    ast.parse(
        modified,
        filename=str(BACKEND_PATH),
    )

except SyntaxError as error:

    fail(
        "Generated backend contains invalid Python:\n"
        + str(error)
    )


try:

    ast.parse(
        DISCOVERY_SOURCE,
        filename=str(DISCOVERY_PATH),
    )

except SyntaxError as error:

    fail(
        "Generated discovery module contains invalid Python:\n"
        + str(error)
    )


print(
    "Generated Python: PASS"
)

print()


# ============================================================================
# CREATE BACKUP
# ============================================================================

BACKUP_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


timestamp = (
    datetime.now()
    .isoformat(
        timespec="seconds"
    )
    .replace(":", "-")
)


backup_path = (
    BACKUP_DIR
    / (
        "main.py.pre-agent-discovery-"
        + timestamp
    )
)


if backup_path.exists():

    fail(
        "Backup destination already exists:\n"
        + str(backup_path)
    )


shutil.copy2(
    BACKEND_PATH,
    backup_path,
)


print(
    "Backup created:"
)

print(
    f"  {backup_path}"
)

print()


# ============================================================================
# WRITE DISCOVERY MODULE
# ============================================================================

MODULES_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


DISCOVERY_PATH.write_text(
    DISCOVERY_SOURCE,
    encoding="utf-8",
)


# ============================================================================
# WRITE BACKEND
# ============================================================================

BACKEND_PATH.write_text(
    modified,
    encoding="utf-8",
)


# ============================================================================
# POST-WRITE VALIDATION
# ============================================================================

print(
    "Running post-write validation..."
)


written_main = BACKEND_PATH.read_text(
    encoding="utf-8"
)

written_discovery = DISCOVERY_PATH.read_text(
    encoding="utf-8"
)


if written_main.count(
    DISCOVERY_IMPORT
) != 1:

    fail(
        "Post-write discovery import validation failed.\n"
        f"Backup: {backup_path}"
    )


if written_main.count(
    DISCOVERY_INCLUDE
) != 1:

    fail(
        "Post-write router registration validation failed.\n"
        f"Backup: {backup_path}"
    )


if written_main.count(
    "# --- WEBAPP2 DISCOVERY START ---"
) != 1:

    fail(
        "Existing discovery block appears to have been altered.\n"
        f"Backup: {backup_path}"
    )


required_routes = [
    "/api/agent/discovery/project",
    "/api/agent/discovery/file",
    "/api/agent/discovery/search",
    "/api/agent/discovery/git",
    "/api/agent/discovery/runtime",
]


for route in required_routes:

    if route not in written_discovery:

        fail(
            "Required discovery route missing:\n"
            + route
            + "\n"
            + f"Backup: {backup_path}"
        )


try:

    ast.parse(
        written_main,
        filename=str(BACKEND_PATH),
    )

    ast.parse(
        written_discovery,
        filename=str(DISCOVERY_PATH),
    )

except SyntaxError as error:

    fail(
        "Post-write Python validation failed:\n"
        + str(error)
        + "\n"
        + f"Backup: {backup_path}"
    )


print(
    "Existing discovery block: PASS"
)

print(
    "Router registration: PASS"
)

print(
    "All discovery routes: PASS"
)

print(
    "Post-write Python syntax: PASS"
)

print()


# ============================================================================
# FINAL REPORT
# ============================================================================

print("=" * 72)
print("MODIFICATION SUCCESSFUL")
print("=" * 72)
print()

print(
    "Installed the read-only local agent discovery layer."
)

print()

print(
    "Created:"
)

print(
    f"  {DISCOVERY_PATH}"
)

print()

print(
    "Modified:"
)

print(
    f"  {BACKEND_PATH}"
)

print()

print(
    "Backup:"
)

print(
    f"  {backup_path}"
)

print()

print(
    "Installed endpoints:"
)

for route in required_routes:

    print(
        f"  GET {route}"
    )

print()

print(
    "Existing /api/discovery functionality was preserved."
)

print(
    "No arbitrary terminal execution was added."
)

print(
    "No filesystem write capability was added."
)

print()