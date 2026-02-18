#!/bin/bash
# Stop the Sniper backend (uvicorn). Use this if the backend was started in the
# background or you closed the terminal it was running in.

echo "Stopping backend (uvicorn on port 8000)..."

# Kill by port 8000 (works on macOS and Linux)
if command -v lsof &>/dev/null; then
  PIDS=$(lsof -ti :8000 2>/dev/null)
  if [ -n "$PIDS" ]; then
    echo "$PIDS" | xargs kill -9 2>/dev/null
    echo "Stopped process(es) on port 8000: $PIDS"
  else
    echo "No process found on port 8000."
  fi
else
  pkill -f "uvicorn app.main:app" 2>/dev/null && echo "Stopped uvicorn." || echo "No uvicorn process found."
fi

echo "Done. Verify with: lsof -i :8000  (should be empty)"
