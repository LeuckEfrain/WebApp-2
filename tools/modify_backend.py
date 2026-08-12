#!/usr/bin/env python3
# real-time testing

"""
tools/modify_backend.py

Replaces the temporary external-access test endpoint with the
GitHub-backed project access gateway for WebApp-2.

The gateway exposes GitHub's existing API through the local backend,
allowing an external client to inspect the project without requiring
the user to manually provide project files.

Endpoints installed:

    GET /api/project/tree
    GET /api/project/contents

Examples:

    /api/project/tree?ref=tests

    /api/project/contents?path=backend/main.py&ref=tests
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
    "# --- WEBAPP2 PROJECT ACCESS START ---"
)

MARKER_END = (
    "# --- WEBAPP2 PROJECT ACCESS END ---"
)


TEST_MARKER_START = (
    "# --- WEBAPP2 PROJECT ACCESS TEST START ---"
)

TEST_MARKER_END = (
    "# --- WEBAPP2 PROJECT ACCESS TEST END ---"
)


GITHUB_GATEWAY_BLOCK = r'''
# --- WEBAPP2 PROJECT ACCESS START ---

@app.get("/api/project/tree")
def project_tree(
    ref: str = "tests",
    recursive: bool = True,
):
    import json
    import urllib.error
    import urllib.parse
    import urllib.request

    if ref not in {"tests", "main"}:
        return {
            "error": "Unsupported repository ref.",
            "allowed_refs": ["main", "tests"],
        }

    url = (
        "https://api.github.com/repos/"
        "LeuckEfrain/WebApp-2/git/trees/"
        + urllib.parse.quote(ref, safe="")
    )

    if recursive:
        url += "?recursive=1"

    request = urllib.request.Request(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "WebApp-2-project-access",
        },
    )

    try:
        with urllib.request.urlopen(
            request,
            timeout=15,
        ) as response:
            return json.loads(
                response.read().decode("utf-8")
            )

    except urllib.error.HTTPError as error:
        try:
            body = error.read().decode("utf-8")
            github_error = json.loads(body)
        except Exception:
            github_error = {
                "message": str(error)
            }

        return {
            "error": "GitHub tree request failed.",
            "status": error.code,
            "github": github_error,
        }

    except Exception as error:
        return {
            "error": "Unable to retrieve project tree.",
            "detail": str(error),
        }


@app.get("/api/project/contents")
def project_contents(
    path: str = "",
    ref: str = "tests",
):
    import json
    import urllib.error
    import urllib.parse
    import urllib.request

    if ref not in {"tests", "main"}:
        return {
            "error": "Unsupported repository ref.",
            "allowed_refs": ["main", "tests"],
        }

    clean_path = path.strip("/")

    encoded_path = urllib.parse.quote(
        clean_path,
        safe="/",
    )

    url = (
        "https://api.github.com/repos/"
        "LeuckEfrain/WebApp-2/contents/"
        + encoded_path
        + "?ref="
        + urllib.parse.quote(ref, safe="")
    )

    request = urllib.request.Request(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "WebApp-2-project-access",
        },
    )

    try:
        with urllib.request.urlopen(
            request,
            timeout=15,
        ) as response:
            return json.loads(
                response.read().decode("utf-8")
            )

    except urllib.error.HTTPError as error:
        try:
            body = error.read().decode("utf-8")
            github_error = json.loads(body)
        except Exception:
            github_error = {
                "message": str(error)
            }

        return {
            "error": "GitHub contents request failed.",
            "status": error.code,
            "github": github_error,
        }

    except Exception as error:
        return {
            "error": "Unable to retrieve project contents.",
            "detail": str(error),
        }


# --- WEBAPP2 PROJECT ACCESS END ---
'''


def fail(message):
    raise SystemExit(
        f"ERROR: {message}\n\n"
        "No changes were made."
    )


# ---------------------------------------------------------------------------
# Read source
# ---------------------------------------------------------------------------

if not BACKEND_PATH.is_file():
    fail(
        "Backend entry point was not found:\n"
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
        "Multiple project-access blocks were found."
    )


if source.count(MARKER_END) > 1:
    fail(
        "Multiple project-access endings were found."
    )


if MARKER_START in source or MARKER_END in source:
    fail(
        "A project-access block already exists or is incomplete."
    )


if "from fastapi import FastAPI" not in source:
    fail(
        "Expected FastAPI import was not found."
    )


if "app = FastAPI(" not in source:
    fail(
        "FastAPI application initialization was not found."
    )


if '@app.get("/api/health")' not in source:
    fail(
        "Expected existing /api/health endpoint was not found."
    )


TEST_ROUTE = '@app.get("/api/project/test")'

if TEST_ROUTE not in source:
    fail(
        "Expected temporary project-access test endpoint "
        "was not found."
    )


if source.count(TEST_MARKER_START) != 1:
    fail(
        "Expected exactly one temporary project-access "
        "test block."
    )


if source.count(TEST_MARKER_END) != 1:
    fail(
        "Expected exactly one temporary project-access "
        "test block ending."
    )


# ---------------------------------------------------------------------------
# Remove temporary test block
# ---------------------------------------------------------------------------

test_start = source.index(TEST_MARKER_START)

test_end = source.index(
    TEST_MARKER_END,
    test_start,
)

test_end += len(TEST_MARKER_END)


modified = (
    source[:test_start]
    + GITHUB_GATEWAY_BLOCK.strip()
    + source[test_end:]
)


# ---------------------------------------------------------------------------
# Validate generated modification
# ---------------------------------------------------------------------------

if modified.count(MARKER_START) != 1:
    fail(
        "Generated project-access block was not created correctly."
    )


if modified.count(MARKER_END) != 1:
    fail(
        "Generated project-access ending was not created correctly."
    )


if modified.count(
    '@app.get("/api/project/tree")'
) != 1:
    fail(
        "GitHub tree endpoint was not generated correctly."
    )


if modified.count(
    '@app.get("/api/project/contents")'
) != 1:
    fail(
        "GitHub contents endpoint was not generated correctly."
    )


if TEST_ROUTE in modified:
    fail(
        "Temporary project-access test endpoint still exists."
    )


# Validate GitHub tree target by source components.
if (
    "https://api.github.com/repos/"
    not in modified
    or "LeuckEfrain/WebApp-2/git/trees/"
    not in modified
):
    fail(
        "GitHub tree API target was not generated."
    )


# Validate GitHub contents target by source components.
if (
    "https://api.github.com/repos/"
    not in modified
    or "LeuckEfrain/WebApp-2/contents/"
    not in modified
):
    fail(
        "GitHub contents API target was not generated."
    )


if "application/vnd.github+json" not in modified:
    fail(
        "GitHub API media type was not generated."
    )


if "urllib.parse.quote" not in modified:
    fail(
        "URL encoding support was not generated."
    )


# ---------------------------------------------------------------------------
# Backup
# ---------------------------------------------------------------------------

BACKUP_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


timestamp = (
    datetime.now()
    .isoformat(timespec="seconds")
    .replace(":", "-")
)


backup_path = (
    BACKUP_DIR
    / (
        "main.py.pre-project-github-access-"
        f"{timestamp}"
    )
)


shutil.copy2(
    BACKEND_PATH,
    backup_path,
)


# ---------------------------------------------------------------------------
# Apply
# ---------------------------------------------------------------------------

BACKEND_PATH.write_text(
    modified,
    encoding="utf-8",
)


# ---------------------------------------------------------------------------
# Post-write validation
# ---------------------------------------------------------------------------

written = BACKEND_PATH.read_text(
    encoding="utf-8"
)


if written.count(MARKER_START) != 1:
    fail(
        "Post-write project-access marker validation failed.\n"
        f"Restore from backup: {backup_path}"
    )


if written.count(MARKER_END) != 1:
    fail(
        "Post-write project-access ending validation failed.\n"
        f"Restore from backup: {backup_path}"
    )


if TEST_ROUTE in written:
    fail(
        "Temporary test endpoint remains after write.\n"
        f"Restore from backup: {backup_path}"
    )


if written.count(
    '@app.get("/api/project/tree")'
) != 1:
    fail(
        "Post-write tree endpoint validation failed.\n"
        f"Restore from backup: {backup_path}"
    )


if written.count(
    '@app.get("/api/project/contents")'
) != 1:
    fail(
        "Post-write contents endpoint validation failed.\n"
        f"Restore from backup: {backup_path}"
    )


if (
    "https://api.github.com/repos/"
    not in written
    or "LeuckEfrain/WebApp-2/git/trees/"
    not in written
):
    fail(
        "Post-write GitHub tree target validation failed.\n"
        f"Restore from backup: {backup_path}"
    )


if (
    "https://api.github.com/repos/"
    not in written
    or "LeuckEfrain/WebApp-2/contents/"
    not in written
):
    fail(
        "Post-write GitHub contents target validation failed.\n"
        f"Restore from backup: {backup_path}"
    )


print(
    "GitHub project access gateway installed successfully."
)

print(
    f"Modified: {BACKEND_PATH}"
)

print(
    f"Backup:   {backup_path}"
)

print(
    "Endpoints:"
)

print(
    "  /api/project/tree"
)

print(
    "  /api/project/contents"
)

print(
    "Source: GitHub API"
)

print(
    "Repository: LeuckEfrain/WebApp-2"
)

print(
    "Default ref: tests"
)