#!/bin/bash
# 🚀 Sniper Platform - One-Command Startup
# Usage: bash START_HERE.sh

set -e

PROJECT_DIR="/Users/pranavks/project/sniper-platform"
BACKEND_DIR="$PROJECT_DIR/sniper-backend"

echo "🚀 Starting Sniper Algorithmic Trading Platform..."
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check prerequisites
echo "${BLUE}📋 Checking prerequisites...${NC}"
command -v node >/dev/null 2>&1 || { echo "${RED}❌ Node.js not found${NC}"; exit 1; }
command -v python3 >/dev/null 2>&1 || { echo "${RED}❌ Python3 not found${NC}"; exit 1; }
command -v docker >/dev/null 2>&1 || { echo "${RED}❌ Docker not found${NC}"; exit 1; }
echo "${GREEN}✅ All prerequisites installed${NC}"
echo ""

# Step 1: Start Database
echo "${BLUE}📦 Starting PostgreSQL database...${NC}"
cd "$PROJECT_DIR"
docker compose up -d postgres
sleep 3
docker ps | grep postgres | grep -q "Up" && echo "${GREEN}✅ Database running on port 5432${NC}" || { echo "${RED}❌ Database failed to start${NC}"; exit 1; }
echo ""

# Step 2: Start Backend
echo "${BLUE}🔧 Starting FastAPI backend...${NC}"
cd "$BACKEND_DIR"

# Create venv if needed
if [ ! -d ".venv" ]; then
    echo "   Creating Python virtual environment..."
    python3 -m venv .venv
fi

# Activate venv
source .venv/bin/activate

# Install requirements if needed
if ! python3 -c "import fastapi" 2>/dev/null; then
    echo "   Installing Python dependencies..."
    pip install -r requirements.txt > /dev/null 2>&1
fi

# Run migrations
echo "   Running database migrations..."
alembic upgrade head > /dev/null 2>&1 || true

# Start backend in background
uvicorn app.main:app --reload --port 8000 &
BACKEND_PID=$!
sleep 3

# Check if backend started
if curl -s http://localhost:8000/health | grep -q "ok"; then
    echo "${GREEN}✅ Backend running on port 8000${NC}"
else
    echo "${RED}❌ Backend failed to start${NC}"
    kill $BACKEND_PID 2>/dev/null || true
    exit 1
fi
echo ""

# Step 3: Install Frontend Dependencies
echo "${BLUE}🎨 Installing frontend dependencies...${NC}"
cd "$PROJECT_DIR"
if [ ! -d "node_modules" ]; then
    npm install > /dev/null 2>&1
else
    echo "   Dependencies already installed"
fi
echo "${GREEN}✅ Frontend dependencies ready${NC}"
echo ""

# Final status
echo "${GREEN}═══════════════════════════════════════════════════════════${NC}"
echo "${GREEN}✅ SYSTEM READY - Starting frontend...${NC}"
echo "${GREEN}═══════════════════════════════════════════════════════════${NC}"
echo ""
echo "${BLUE}📍 Access points:${NC}"
echo "   Frontend:        ${YELLOW}http://localhost:3000${NC}"
echo "   Backend API:     ${YELLOW}http://localhost:8000${NC}"
echo "   API Docs:        ${YELLOW}http://localhost:8000/docs${NC}"
echo "   Database:        localhost:5432"
echo ""
echo "${BLUE}🛑 To stop all services:${NC}"
echo "   Press Ctrl+C to stop the frontend"
echo "   Then run: docker compose down"
echo ""

# Start frontend
npm run dev
