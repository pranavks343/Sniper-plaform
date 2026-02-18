# 🚀 Sniper Algo Platform — Complete Startup Guide

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    SNIPER ALGORITHMIC TRADING PLATFORM                  │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐ │
│  │  Frontend (Web)  │    │  Backend (API)   │    │  Database        │ │
│  ├──────────────────┤    ├──────────────────┤    ├──────────────────┤ │
│  │ Next.js 14       │    │ FastAPI (Python) │    │ PostgreSQL       │ │
│  │ React 18         │    │ WebSocket feeds  │    │ Port: 5432       │ │
│  │ Tailwind CSS     │    │ Backtest engine  │    │ Docker container │ │
│  │ GSAP animations  │    │ Risk engine      │    │                  │ │
│  │ Port: 3000       │    │ Port: 8000       │    │ User: postgres   │ │
│  │                  │    │                  │    │ Pass: postgres   │ │
│  └──────────────────┘    └──────────────────┘    └──────────────────┘ │
│         │                         │                       │            │
│         └─────────────────────────┴───────────────────────┘            │
│                                   │                                   │
│         ┌─────────────────────────┴─────────────────────────┐          │
│         │                                                   │          │
│    ┌────────────────┐                          ┌──────────────────┐  │
│    │ Clerk Auth     │                          │ Convex Backend   │  │
│    │ (User login)   │                          │ (Real-time DB)   │  │
│    │ Cloud-hosted   │                          │ Cloud-hosted     │  │
│    └────────────────┘                          └──────────────────┘  │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 📋 Prerequisites

Before starting, ensure you have installed:

```bash
# Check versions
node --version          # v18+
npm --version           # v9+
python3 --version       # v3.10+
docker --version        # latest
docker-compose --version # v2+
```

If not installed, install them:
- **Node.js**: https://nodejs.org/ (LTS recommended)
- **Python 3**: https://www.python.org/
- **Docker Desktop**: https://www.docker.com/products/docker-desktop

---

## 🎯 QUICK START (3 steps)

### Step 1: Start Database & Backend

**Terminal 1 — Database:**
```bash
# From /Users/pranavks/project/sniper-platform
docker compose up -d postgres

# Verify it's running
docker ps | grep postgres
# Should show: sniper-postgres  Up X minutes
```

**Terminal 2 — Backend API:**
```bash
cd /Users/pranavks/project/sniper-platform/sniper-backend

# Create virtual environment (first time only)
python3 -m venv .venv

# Activate virtual environment
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run database migrations (first time only)
alembic upgrade head

# Start backend server
uvicorn app.main:app --reload --port 8000
```

Backend will start at: **http://localhost:8000**

### Step 2: Start Frontend

**Terminal 3 — Frontend:**
```bash
cd /Users/pranavks/project/sniper-platform

# Install dependencies (if not done yet)
npm install

# Start dev server
npm run dev
```

Frontend will start at: **http://localhost:3000**

### Step 3: Access the Application

Open in browser:
- **Application**: http://localhost:3000
- **Backend Docs**: http://localhost:8000/docs
- **Backend ReDoc**: http://localhost:8000/redoc

---

## 🔧 DETAILED SERVICE STARTUP

### Database (PostgreSQL)

**Start:**
```bash
cd /Users/pranavks/project/sniper-platform
docker compose up -d postgres
```

**Stop:**
```bash
docker compose down postgres
```

**Check logs:**
```bash
docker compose logs postgres
```

**Connect to database directly:**
```bash
docker exec -it sniper-postgres psql -U postgres -d sniper
# Then run: \dt (list tables), \q (quit)
```

---

### Backend (FastAPI + Python)

**First-time setup:**
```bash
cd /Users/pranavks/project/sniper-platform/sniper-backend

# Create virtual environment
python3 -m venv .venv

# Activate it
source .venv/bin/activate  # macOS/Linux
# or on Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run database migrations
alembic upgrade head

# Check imports work
python3 -c "from app.main import app; print('✅ Backend imports OK')"
```

**Run backend:**
```bash
cd /Users/pranavks/project/sniper-platform/sniper-backend
source .venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

**Backend health check:**
```bash
curl http://localhost:8000/health
# Response: {"status":"ok"}
```

**Key API endpoints:**
```bash
# List strategies
curl http://localhost:8000/api/v1/strategy/

# Get risk metrics
curl http://localhost:8000/api/v1/risk/metrics

# Check quantum status
curl http://localhost:8000/api/v1/quantum/status

# Interactive API docs
open http://localhost:8000/docs
```

---

### Frontend (Next.js)

**First-time setup:**
```bash
cd /Users/pranavks/project/sniper-platform

# Install dependencies
npm install

# Check TypeScript compiles
npx tsc --noEmit

# Build (optional)
npm run build
```

**Run frontend (development mode):**
```bash
cd /Users/pranavks/project/sniper-platform
npm run dev
```

Frontend will be at: **http://localhost:3000**

**Frontend build (production):**
```bash
npm run build
npm start
```

**Linting:**
```bash
npm run lint
```

**TypeScript check:**
```bash
npm run typecheck
```

---

## 🧪 Verify Everything Works

### Automated Smoke Tests

```bash
cd /Users/pranavks/project/sniper-platform
bash smoke-test.sh
```

Expected output:
```
=== SMOKE TEST SUITE ===
✓ Testing backend health endpoint...
  ✓ Backend health OK
✓ Testing strategy API...
  ✓ Strategy API OK
✓ Testing risk metrics API...
  ✓ Risk metrics API OK
✓ Testing execution API...
  ✓ Execution API OK
✓ Testing quantum API...
  ✓ Quantum API OK
✓ Testing frontend...
  ✓ Frontend OK
=== ALL SMOKE TESTS PASSED ===
```

### Manual Test Flow

**1. Create a Strategy:**
```bash
curl -X POST http://localhost:8000/api/v1/strategy/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Iron Condor NIFTY",
    "type": "options_sell",
    "parameters": {
      "symbol": "NIFTY",
      "timeframe": "15m"
    }
  }' | python3 -m json.tool
```

Copy the `id` from response.

**2. Get Strategy Details:**
```bash
curl http://localhost:8000/api/v1/strategy/{id} | python3 -m json.tool
```

**3. List All Strategies:**
```bash
curl http://localhost:8000/api/v1/strategy/ | python3 -m json.tool
```

**4. Check Risk Metrics:**
```bash
curl http://localhost:8000/api/v1/risk/metrics | python3 -m json.tool
```

**5. Get Positions:**
```bash
curl http://localhost:8000/api/v1/execution/positions | python3 -m json.tool
```

---

## 🛑 Stopping All Services

**Stop everything gracefully:**
```bash
# In Terminal 2 (Backend): Ctrl+C
# In Terminal 3 (Frontend): Ctrl+C

# In Terminal 1 (Database):
docker compose down
```

**Verify all stopped:**
```bash
docker ps
# Should be empty

lsof -i :3000   # Should return nothing
lsof -i :8000   # Should return nothing
lsof -i :5432   # Should return nothing
```

---

## 🔄 Complete System Restart

If something goes wrong, restart everything:

```bash
# 1. Stop everything
docker compose down
pkill -f "uvicorn"
pkill -f "next dev"

# 2. Clear cache (optional)
rm -rf /Users/pranavks/project/sniper-platform/.next
rm -rf /Users/pranavks/project/sniper-platform/sniper-backend/.venv

# 3. Restart from Step 1 above
```

---

## 📝 Environment Variables

### Frontend (`.env.local`)
```bash
# Clerk Auth (already set)
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_c3R1bm5pbmctYnVsbGZyb2ctNi5jbGVyay5hY2NvdW50cy5kZXYk
CLERK_SECRET_KEY=sk_test_mNVySwRHQmxljdVxTpaIAfhmw3zUY4eOS0W0fDlZ07

# Convex Backend (already set)
NEXT_PUBLIC_CONVEX_URL=https://robust-tern-944.convex.cloud
```

### Backend (`sniper-backend/.env`)
```bash
# Database (Docker)
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/sniper

# Broker (paper trading)
BROKER_PROVIDER=paper

# (Optional) For real trading, add:
# UPSTOX_API_KEY=your_key
# UPSTOX_API_SECRET=your_secret
```

---

## 🎨 Frontend User Flow

### 1. **Strategy Dashboard** (`/dashboard`)
- View all active strategies
- Monitor portfolio P&L
- See algo-generated positions
- Risk status indicator

### 2. **Strategy Library** (`/dashboard/strategies`)
- Browse all strategies
- Filter: Active / Paused / Inactive
- Create, edit, delete strategies
- Start/Stop strategies

### 3. **Strategy Builder** (`/dashboard/strategies/new`)
- **Step 1**: Setup (name, type, symbol, timeframe)
- **Step 2**: Visual Logic Builder (drag-drop indicators → conditions → actions)
- **Step 3**: Risk Parameters (max loss, position limits, stop loss type)
- **Step 4**: Review & Activate

### 4. **Backtesting** (`/dashboard/backtesting`)
- Configure backtest: date range, capital, commission
- Run simulation with progress indicator
- View equity curve
- Analyze metrics: Sharpe, Sortino, Win Rate, Profit Factor, Drawdown

### 5. **Live Monitor** (`/dashboard/live-trading`)
- Watch active algos execute
- Real-time activity feed: ENTRY / EXIT / HEDGE / SL HIT
- Algo control panel (Start/Stop each strategy)
- Risk status and margin tracking

### 6. **Risk Engine** (`/dashboard/risk`)
- Greeks dashboard (Delta, Gamma, Vega, Theta)
- Circuit breaker status
- Position limits tracking

### 7. **Analytics** (`/dashboard/analytics`)
- Historical performance
- Win rate, trade count
- Monthly P&L breakdown

---

## 📊 Key Features

### ✅ What's Implemented
- [x] User authentication (Clerk)
- [x] Strategy CRUD (create, read, update, delete)
- [x] Visual strategy builder with drag-drop nodes
- [x] Backtesting engine with equity curve
- [x] Paper trading (no real money)
- [x] Risk management & Greeks
- [x] Real-time WebSocket feeds
- [x] Live trading monitor (read-only, algo-only)
- [x] Dark/Light mode toggle
- [x] GSAP smooth animations
- [x] Responsive design (mobile-friendly)

### ❌ Removed (Legacy)
- Manual order entry (buy/sell buttons)
- Paper trading simulator
- Manual position close button
- "Discretionary" mode toggle

---

## 🐛 Troubleshooting

### "Backend won't start"
```bash
# Check if port 8000 is in use
lsof -i :8000

# If it is, kill the process
kill -9 <PID>

# Or change port
uvicorn app.main:app --port 8001
```

### "Database connection refused"
```bash
# Check Docker container
docker ps | grep postgres

# If not running, start it
docker compose up -d postgres

# Check logs
docker compose logs postgres
```

### "Frontend build errors"
```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json .next
npm install
npx tsc --noEmit
```

### "Module not found" errors in backend
```bash
cd sniper-backend
source .venv/bin/activate
pip install -r requirements.txt --upgrade
python3 -c "from app.main import app; print('OK')"
```

### "Port already in use"
```bash
# Find what's using the port
lsof -i :3000   # Frontend
lsof -i :8000   # Backend
lsof -i :5432   # Database

# Kill the process
kill -9 <PID>
```

---

## 📚 Useful Commands Reference

| Task | Command |
|------|---------|
| Start all services | `docker compose up -d postgres && cd sniper-backend && source .venv/bin/activate && uvicorn app.main:app --reload --port 8000` (terminal 2) + `npm run dev` (terminal 3) |
| Stop all services | `docker compose down` + `Ctrl+C` in terminals 2 & 3 |
| View backend logs | `docker compose logs postgres` or check terminal output |
| Access database CLI | `docker exec -it sniper-postgres psql -U postgres -d sniper` |
| Run migrations | `cd sniper-backend && source .venv/bin/activate && alembic upgrade head` |
| Run smoke tests | `bash smoke-test.sh` |
| Build frontend | `npm run build` |
| Type check | `npx tsc --noEmit` |
| Lint frontend | `npm run lint` |

---

## 🎓 Documentation

- **System Status**: `SYSTEM_STATUS.md` — Full system overview
- **Fix Log**: `FIX_LOG.md` — Debugging history
- **Backend API**: http://localhost:8000/docs — Interactive Swagger docs
- **Backend ReDoc**: http://localhost:8000/redoc — Alternative API docs

---

## ✅ Checklist Before First Run

- [ ] Node.js v18+ installed
- [ ] Python 3.10+ installed
- [ ] Docker & Docker Compose installed
- [ ] `.env.local` file exists with Clerk keys
- [ ] `sniper-backend/.env` exists with database URL
- [ ] PostgreSQL container ready (`docker compose up -d postgres`)
- [ ] Backend virtual environment created (`python3 -m venv .venv`)
- [ ] Frontend dependencies installed (`npm install`)
- [ ] All three services can start without errors

---

## 🚀 You're Ready!

**Next Steps:**
1. ✅ Start the three services (follow Step 1-2 above)
2. ✅ Open http://localhost:3000 in your browser
3. ✅ Log in with Clerk
4. ✅ Create your first strategy
5. ✅ Run a backtest
6. ✅ Activate the strategy to see it trade

**Questions?** Check the logs, run smoke tests, or review `SYSTEM_STATUS.md`.

---

**Last Updated**: 2026-02-18
**Status**: ✅ Ready for production
