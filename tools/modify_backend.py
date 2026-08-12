#!/usr/bin/env python3

"""
tools/modify_backend.py

Installs the temporary external-access test endpoint for WebApp-2.

This follows the same safety pattern as modify_frontend.py:
- validate the expected source state
- construct the modification
- validate the resulting source
- create a backup
- write the file
- report the modification

Temporary endpoint:

    GET /api/project/test

Expected response:

    {
        "status": "ok",
        "source": "WebApp-2"
    }
"""

from pathlib import Path
import shutil
from datetime import datetime


BACKEND_ROOT = Path(__file__).resolve().parents[1]

BACKEND_PATH = (
    BACKEND_ROOT
    / "backend"
    / "main.py"
)

BACKUP_DIR = (
    BACKEND_ROOT
    / "backend"
    / ".webapp2-refactor-backups"
)

MARKER_START = (
    "# --- WEBAPP2 PROJECT ACCESS TEST START ---"
)

MARKER_END = (
    "# --- WEBAPP2 PROJECT ACCESS TEST END ---"
)


TEST_BLOCK = r'''
# --- WEBAPP2 PROJECT ACCESS TEST START ---

@app.get("/api/project/test")
def project_access_test():
    return {
        "status": "ok",
        "source": "WebApp-2",
    }

# --- WEBAPP2 PROJECT ACCESS TEST END ---
'''


def fail(message):
    raise SystemExit(
        f"ERROR: {message}"
    )


# ---------------------------------------------------------------------------
# Read source
# ---------------------------------------------------------------------------

if not BACKEND_PATH.is_file():
    fail(
        f"Backend entry point was not found: "
        f"{BACKEND_PATH}"
    )


source = BACKEND_PATH.read_text(
    encoding="utf-8"
)


# ---------------------------------------------------------------------------
# Validate expected source state
# ---------------------------------------------------------------------------

if source.count(MARKER_START) > 1:
    fail(
        "Multiple project-access test blocks "
        "were found.\n\n"
        "No changes were made."
    )


if source.count(MARKER_END) > 1:
    fail(
        "Multiple project-access test endings "
        "were found.\n\n"
        "No changes were made."
    )


if MARKER_START in source or MARKER_END in source:
    fail(
        "A project-access test block already exists "
        "or is incomplete.\n\n"
        "No changes were made."
    )


if "from fastapi import FastAPI" not in source:
    fail(
        "Expected FastAPI import was not found.\n\n"
        "No changes were made."
    )


if "app = FastAPI(" not in source:
    fail(
        "FastAPI application initialization was not found.\n\n"
        "No changes were made."
    )


if '@app.get("/api/health")' not in source:
    fail(
        "Expected existing /api/health endpoint "
        "was not found.\n\n"
        "No changes were made."
    )


if '@app.get("/api/project/test")' in source:
    fail(
        "Project-access test endpoint already exists "
        "outside the managed block.\n\n"
        "No changes were made."
    )


# ---------------------------------------------------------------------------
# Construct modification
# ---------------------------------------------------------------------------

modified = (
    source.rstrip()
    + "\n\n"
    + TEST_BLOCK
    + "\n"
)


# ---------------------------------------------------------------------------
# Validate generated modification
# ---------------------------------------------------------------------------

if modified.count(MARKER_START) != 1:
    fail(
        "Generated project-access test block "
        "was not created correctly.\n\n"
        "No changes were made."
    )


if modified.count(MARKER_END) != 1:
    fail(
        "Generated project-access test ending "
        "was not created correctly.\n\n"
        "No changes were made."
    )


if modified.count(
    '@app.get("/api/project/test")'
) != 1:
    fail(
        "Expected exactly one project-access "
        "test endpoint.\n\n"
        "No changes were made."
    )


if "source" not in modified:
    fail(
        "Test response was not generated correctly.\n\n"
        "No changes were made."
    )


# ---------------------------------------------------------------------------
# Backup
# ---------------------------------------------------------------------------

BACKUP_DIR.mkdir(
    parents=True,
    exist_ok=True
)


timestamp = (
    datetime.now()
    .isoformat(timespec="seconds")
    .replace(":", "-")
)


backup_path = (
    BACKUP_DIR
    / (
        "main.py.pre-project-access-test-"
        f"{timestamp}"
    )
)


shutil.copy2(
    BACKEND_PATH,
    backup_path
)


# ---------------------------------------------------------------------------
# Apply
# ---------------------------------------------------------------------------

BACKEND_PATH.write_text(
    modified,
    encoding="utf-8"
)


# ---------------------------------------------------------------------------
# Post-write validation
# ---------------------------------------------------------------------------

written = BACKEND_PATH.read_text(
    encoding="utf-8"
)


if written.count(MARKER_START) != 1:
    fail(
        "Post-write validation failed.\n"
        f"Restore from backup: {backup_path}"
    )


if written.count(MARKER_END) != 1:
    fail(
        "Post-write validation failed.\n"
        f"Restore from backup: {backup_path}"
    )


if written.count(
    '@app.get("/api/project/test")'
) != 1:
    fail(
        "Post-write endpoint validation failed.\n"
        f"Restore from backup: {backup_path}"
    )


print(
    "Project access test endpoint "
    "installed successfully."
)

print(
    f"Modified: {BACKEND_PATH}"
)

print(
    f"Backup:   {backup_path}"
)

print(
    "Endpoint: /api/project/test"
)