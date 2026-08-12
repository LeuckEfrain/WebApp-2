# tools/modify_frontend.py

from pathlib import Path
import shutil
from datetime import datetime


PROJECT_ROOT = Path(__file__).resolve().parents[1]

FRONTEND_ROOT = PROJECT_ROOT / "frontend"
VITE_CONFIG_PATH = FRONTEND_ROOT / "vite.config.js"

BACKUP_DIR = FRONTEND_ROOT / ".webapp2-refactor-backups"

MARKER_START = "// WEBAPP2_API_PROXY_START"
MARKER_END = "// WEBAPP2_API_PROXY_END"


def fail(message):
    raise SystemExit(
        f"ERROR: {message}\n\n"
        "No changes were made."
    )


if not VITE_CONFIG_PATH.is_file():
    fail(
        f"Vite configuration was not found:\n"
        f"{VITE_CONFIG_PATH}"
    )


source = VITE_CONFIG_PATH.read_text(
    encoding="utf-8"
)


# ---------------------------------------------------------------------------
# Validate existing state
# ---------------------------------------------------------------------------

if source.count(MARKER_START) > 1:
    fail(
        "Multiple API proxy blocks were found."
    )

if source.count(MARKER_END) > 1:
    fail(
        "Multiple API proxy endings were found."
    )

if MARKER_START in source or MARKER_END in source:
    fail(
        "An API proxy block already exists or is incomplete."
    )

if "export default defineConfig(" not in source:
    fail(
        "Expected Vite defineConfig() export was not found."
    )

if "server:" not in source:
    fail(
        "Expected Vite server configuration was not found."
    )

if "allowedHosts:" not in source:
    fail(
        "Expected existing allowedHosts configuration was not found."
    )


# ---------------------------------------------------------------------------
# Locate the existing server configuration.
#
# We intentionally do not replace allowedHosts. The user's existing
# allowedHosts modification must remain untouched.
# ---------------------------------------------------------------------------

server_start = source.find("server:")

if server_start == -1:
    fail(
        "Unable to locate Vite server configuration."
    )


brace_start = source.find(
    "{",
    server_start
)

if brace_start == -1:
    fail(
        "Unable to locate the opening brace of the Vite server configuration."
    )


# Find the matching closing brace while respecting strings/comments.
depth = 0
server_end = None

for index in range(
    brace_start,
    len(source)
):
    character = source[index]

    if character == "{":
        depth += 1

    elif character == "}":
        depth -= 1

        if depth == 0:
            server_end = index + 1
            break


if server_end is None:
    fail(
        "Unable to safely locate the end of the Vite server configuration."
    )


server_block = source[
    server_start:
    server_end
]


if "allowedHosts:" not in server_block:
    fail(
        "The identified Vite server block does not contain allowedHosts."
    )


# ---------------------------------------------------------------------------
# Build the proxy block.
# ---------------------------------------------------------------------------

proxy_block = f"""
        {MARKER_START}

        /*
         * Forward externally exposed /api requests to FastAPI.
         *
         * Cloudflare -> Vite -> FastAPI
         *
         * The existing allowedHosts configuration is intentionally
         * preserved exactly as-is.
         */
        proxy: {{
            '/api': {{
                target: 'http://localhost:8000',
                changeOrigin: true
            }}
        }},

        {MARKER_END}"""


# ---------------------------------------------------------------------------
# Insert immediately after the existing allowedHosts property.
#
# We do not reconstruct or replace allowedHosts. Instead, we locate its
# existing closing bracket and insert the proxy afterward.
# ---------------------------------------------------------------------------

allowed_hosts_start = server_block.find(
    "allowedHosts:"
)

if allowed_hosts_start == -1:
    fail(
        "Unable to locate allowedHosts inside the server block."
    )


allowed_hosts_array_start = server_block.find(
    "[",
    allowed_hosts_start
)

if allowed_hosts_array_start == -1:
    fail(
        "Unable to locate the allowedHosts array."
    )


allowed_hosts_array_end = server_block.find(
    "]",
    allowed_hosts_array_start
)

if allowed_hosts_array_end == -1:
    fail(
        "Unable to locate the end of the allowedHosts array."
    )


insert_position = allowed_hosts_array_end + 1


modified_server_block = (
    server_block[:insert_position]
    + ","
    + proxy_block
    + server_block[insert_position:]
)


modified = source.replace(
    server_block,
    modified_server_block,
    1
)


# ---------------------------------------------------------------------------
# Validate generated modification before writing.
# ---------------------------------------------------------------------------

if modified.count(MARKER_START) != 1:
    fail(
        "Generated API proxy block was not created correctly."
    )

if modified.count(MARKER_END) != 1:
    fail(
        "Generated API proxy ending was not created correctly."
    )

if modified.count(
    "target: 'http://localhost:8000'"
) != 1:
    fail(
        "Expected FastAPI proxy target was not generated correctly."
    )

if modified.count(
    "'/api'"
) != 1:
    fail(
        "Expected exactly one /api proxy was not generated."
    )


# ---------------------------------------------------------------------------
# Verify that the existing allowedHosts configuration survived unchanged.
# ---------------------------------------------------------------------------

original_allowed_hosts = server_block[
    allowed_hosts_start:
    allowed_hosts_array_end + 1
]

modified_server_start = modified.find(
    "server:"
)

modified_server_brace_start = modified.find(
    "{",
    modified_server_start
)

modified_allowed_hosts_start = modified.find(
    "allowedHosts:",
    modified_server_brace_start
)

modified_allowed_hosts_array_start = modified.find(
    "[",
    modified_allowed_hosts_start
)

modified_allowed_hosts_array_end = modified.find(
    "]",
    modified_allowed_hosts_array_start
)

modified_allowed_hosts = modified[
    modified_allowed_hosts_start:
    modified_allowed_hosts_array_end + 1
]


if original_allowed_hosts != modified_allowed_hosts:
    fail(
        "The existing allowedHosts configuration would be changed."
    )


# ---------------------------------------------------------------------------
# Backup only after validation succeeds.
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
    / f"vite.config.js.pre-api-proxy-{timestamp}"
)


shutil.copy2(
    VITE_CONFIG_PATH,
    backup_path
)


# ---------------------------------------------------------------------------
# Apply modification.
# ---------------------------------------------------------------------------

VITE_CONFIG_PATH.write_text(
    modified,
    encoding="utf-8"
)


# ---------------------------------------------------------------------------
# Post-write validation.
# ---------------------------------------------------------------------------

written = VITE_CONFIG_PATH.read_text(
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
    "target: 'http://localhost:8000'"
) != 1:
    fail(
        "Post-write FastAPI proxy validation failed.\n"
        f"Restore from backup: {backup_path}"
    )


print(
    "WebApp-2 API proxy installed successfully."
)

print(
    f"Modified: {VITE_CONFIG_PATH}"
)

print(
    f"Backup:   {backup_path}"
)

print(
    "Proxy:    /api -> http://localhost:8000"
)

print(
    "Existing allowedHosts configuration was preserved."
)