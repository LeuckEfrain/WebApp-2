"""
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
