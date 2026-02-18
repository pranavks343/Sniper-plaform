#!/bin/bash
# Stop all Sniper dev processes: frontend (3000), backend (8000), and optionally Postgres (Docker).
# Usage: bash stop-all.sh

set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

kill_port() {
  local port=$1
  local name=$2
  if ! command -v lsof &>/dev/null; then
    echo "${YELLOW}lsof not found; cannot kill port $port${NC}"
    return 1
  fi
  local pids
  pids=$(lsof -ti :"$port" 2>/dev/null)
  if [ -n "$pids" ]; then
    echo "$pids" | xargs kill -9 2>/dev/null
    echo "${GREEN}Stopped $name (port $port) — PIDs: $pids${NC}"
    return 0
  else
    echo "No process on port $port ($name)."
    return 1
  fi
}

echo "Stopping all Sniper dev processes..."
echo ""

kill_port 3000 "Frontend (Next.js)"
kill_port 8000 "Backend (uvicorn)"
echo ""

# Stop Postgres (Docker) if docker compose is available
if command -v docker &>/dev/null && [ -f "docker-compose.yml" ] || [ -f "compose.yml" ]; then
  echo "Stopping Postgres (Docker)..."
  docker compose down 2>/dev/null || docker-compose down 2>/dev/null || true
  echo "${GREEN}Docker Compose stopped.${NC}"
else
  echo "To stop Postgres (port 5432), run: docker compose down"
fi

echo ""
echo "Done. Ports 3000 and 8000 should be free."
echo "Verify: lsof -i :3000; lsof -i :8000"
