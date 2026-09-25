#!/usr/bin/env bash
# Linux/macOS entrypoint for scripts/lib/healthcheck.py. See that file for
# what it actually checks.
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# On Windows, `python3` may exist on PATH as a non-functional Microsoft
# Store alias stub, so check it actually runs rather than just exists.
PYTHON=python3
python3 --version >/dev/null 2>&1 || PYTHON=python

exec "$PYTHON" "$SCRIPT_DIR/lib/healthcheck.py" "$@"
