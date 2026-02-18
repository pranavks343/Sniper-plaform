#!/bin/bash
# Run Alembic from sniper-backend using its .venv (creates venv and installs deps if needed).
# Requires Python 3.11 or 3.12 (pydantic-core does not support 3.14 yet).
set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$BACKEND_ROOT"

# Prefer 3.12 then 3.11 (avoid 3.13/3.14 for pydantic-core wheel compatibility)
for py in python3.12 python3.11 python3; do
    if command -v "$py" &>/dev/null && "$py" -c 'import sys; exit(0 if sys.version_info < (3, 13) else 1)' 2>/dev/null; then
        PYTHON="$py"
        break
    fi
done
PYTHON="${PYTHON:-python3}"

if [ ! -d ".venv" ]; then
    echo "Creating .venv with $PYTHON and installing dependencies..."
    "$PYTHON" -m venv .venv
    .venv/bin/pip install -q -r requirements.txt
elif ! .venv/bin/python -c "import alembic" 2>/dev/null; then
    echo "Installing dependencies into existing .venv..."
    .venv/bin/pip install -q -r requirements.txt
fi

.venv/bin/python -m alembic "$@"
