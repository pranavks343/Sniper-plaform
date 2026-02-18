#!/bin/bash
# Start the Sniper backend (FastAPI) on http://localhost:8000
# Run from: sniper-platform/sniper-backend (or project root)

set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "Starting backend at http://localhost:8000 ..."
echo ""

# Use Python 3.12 or 3.11 (pydantic-core has no wheels for 3.13/3.14)
for py in python3.12 python3.11; do
    if command -v "$py" &>/dev/null; then
        PYTHON="$py"
        break
    fi
done
PYTHON="${PYTHON:-python3}"

# Create venv with correct Python if missing
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment ($PYTHON)..."
    $PYTHON -m venv .venv
fi

source .venv/bin/activate

# Ensure uvicorn and deps are installed
if ! python -c "import uvicorn" 2>/dev/null; then
    echo "Installing dependencies (this may take a minute)..."
    pip install -q -r requirements.txt
fi

echo "Backend will be at: http://localhost:8000"
echo "Health check: http://localhost:8000/health"
echo "Press Ctrl+C to stop."
echo ""

exec uvicorn app.main:app --reload --port 8000
