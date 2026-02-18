# 📑 Sniper Platform - Complete Index

## 🚀 Getting Started

**Start here if you're new:**

1. **[START_HERE.sh](./START_HERE.sh)** — One-liner to start everything
   ```bash
   bash START_HERE.sh
   ```

2. **[STARTUP_GUIDE.md](./STARTUP_GUIDE.md)** — Detailed setup instructions
   - Prerequisites
   - Step-by-step setup
   - Environment variables
   - Troubleshooting

3. **[COMMANDS.md](./COMMANDS.md)** — Complete command reference
   - All startup commands
   - Backend API commands
   - Frontend commands
   - Docker commands
   - Debugging commands

---

## 📚 Documentation

### Platform Overview
- **[README_ALGO_PLATFORM.md](./README_ALGO_PLATFORM.md)** — Transformation from manual to algo trading
  - What changed
  - New user flow
  - Pages & features
  - Architecture overview
  - Workflow examples

- **[SYSTEM_STATUS.md](./SYSTEM_STATUS.md)** — Complete system overview
  - Current status
  - Running services
  - Configuration details

### Development Guides
- **[FIX_LOG.md](./FIX_LOG.md)** — Debugging history and fixes
- **[QUICK_START.md](./QUICK_START.md)** — Original quick start guide
- **[VERIFICATION_CHECKLIST.md](./VERIFICATION_CHECKLIST.md)** — Pre-launch checklist

### API Documentation
- **[http://localhost:8000/docs](http://localhost:8000/docs)** — Interactive Swagger documentation (when backend is running)
- **[http://localhost:8000/redoc](http://localhost:8000/redoc)** — Alternative ReDoc documentation

---

## 🏗️ Project Structure

### Frontend (Next.js)
```
app/(dashboard)/
├── page.tsx                     → Strategy Dashboard
├── strategies/
│   ├── page.tsx                → Strategy Library
│   ├── new/page.tsx            → Strategy Builder
│   └── [id]/builder/page.tsx   → Visual Logic Editor
├── backtesting/page.tsx        → Backtesting Engine
├── live-trading/page.tsx       → Live Monitor
├── risk/page.tsx               → Risk Dashboard
├── analytics/page.tsx          → Analytics
└── profile/page.tsx            → User Profile

components/
├── layout/
│   ├── sidebar.tsx             → Navigation sidebar
│   └── header.tsx              → Top header bar
├── trading/
│   └── position-table.tsx      → Algo positions display
├── strategy/
│   └── strategy-cards.tsx      → Strategy cards UI
└── ui/                         → Reusable UI components
```

### Backend (FastAPI)
```
sniper-backend/
├── app/
│   ├── api/v1/
│   │   ├── strategy.py         → Strategy endpoints
│   │   ├── execution.py        → Order execution
│   │   ├── backtest.py         → Backtesting
│   │   ├── risk.py             → Risk metrics
│   │   ├── quantum.py          → Quantum signals
│   │   └── websocket.py        → Real-time feeds
│   ├── core/
│   │   ├── strategy_engine/    → Strategy execution logic
│   │   ├── execution_engine/   → Order routing
│   │   ├── risk_engine/        → Greeks & controls
│   │   └── data_pipeline/      → Market data
│   └── services/               → Business services
└── requirements.txt            → Python dependencies
```

### Database
```
PostgreSQL on Docker
├── strategies table
├── backtest_runs table
├── positions table
├── orders table
├── trades table
└── risk_metrics table
```

---

## 🎯 Key Pages & Features

### Strategy Dashboard (`/dashboard`)
Monitor all algorithmic trading activity in one place
- Portfolio P&L
- Active strategies with enable/disable toggles
- Algo-generated positions (read-only)
- Risk status and Greeks

### Strategy Library (`/dashboard/strategies`)
Manage all strategies
- Create new strategy
- Edit strategy logic
- Run backtest
- Activate/deactivate strategy
- Delete strategy
- Filter: Active / Paused / Inactive

### Strategy Builder (`/dashboard/strategies/new`)
Visual strategy creation with 4 steps
1. **Setup**: Name, type, symbol, timeframe
2. **Builder**: Drag-drop indicators → conditions → actions
3. **Risk**: Max loss, position limits, stop loss type
4. **Review**: Summary and activate

### Backtesting (`/dashboard/backtesting`)
Validate strategies on historical data
- Configure: date range, capital, commission
- Run simulation with progress bar
- View equity curve
- Analyze metrics: Sharpe, Sortino, Win Rate, Drawdown, Profit Factor

### Live Monitor (`/dashboard/live-trading`)
Watch algorithms trade in real-time (read-only)
- Active algos panel
- Real-time activity feed: ENTRY/EXIT/HEDGE/SL HIT
- Portfolio status bar
- Risk tracking
- No manual trading buttons

### Risk Engine (`/dashboard/risk`)
Monitor portfolio risk
- Greeks dashboard (Delta, Gamma, Vega, Theta)
- Circuit breaker status
- Position limits
- Margin tracking

### Analytics (`/dashboard/analytics`)
Historical performance analysis
- Win rate, trade count
- Best/worst days
- Monthly P&L breakdown
- Strategy comparison

---

## ⚡ Quick Commands

### Start Everything
```bash
bash START_HERE.sh
```

### Start Services Manually
```bash
# Terminal 1: Database
docker compose up -d postgres

# Terminal 2: Backend
cd sniper-backend && source .venv/bin/activate
uvicorn app.main:app --reload --port 8000

# Terminal 3: Frontend
npm run dev
```

### Verify Setup
```bash
bash smoke-test.sh
```

### Stop Everything
```bash
# Press Ctrl+C in all terminals
docker compose down
```

### View Logs
```bash
docker compose logs postgres -f
```

### Database Access
```bash
docker exec -it sniper-postgres psql -U postgres -d sniper
```

### TypeScript Check
```bash
npm run typecheck
# or
npx tsc --noEmit
```

---

## 🌐 Access Points

When services are running:

| Service | URL | Purpose |
|---------|-----|---------|
| **Frontend** | http://localhost:3000 | Main application |
| **Backend** | http://localhost:8000 | API endpoint |
| **API Docs** | http://localhost:8000/docs | Swagger documentation |
| **API ReDoc** | http://localhost:8000/redoc | Alternative API docs |
| **Database** | localhost:5432 | PostgreSQL (postgres:postgres) |

---

## 📊 Technology Stack

### Frontend
- **Framework**: Next.js 14 (App Router)
- **UI Library**: React 18
- **Styling**: Tailwind CSS 3
- **Animations**: GSAP 3
- **State Management**: Zustand
- **Authentication**: Clerk
- **Backend**: Convex (real-time DB)
- **Charts**: lightweight-charts

### Backend
- **Framework**: FastAPI
- **Server**: Uvicorn
- **Database**: PostgreSQL + SQLAlchemy
- **Async**: asyncpg
- **Migrations**: Alembic
- **ML**: XGBoost, scikit-learn, Stable Baselines 3
- **Quantum**: Qiskit

### Infrastructure
- **Container**: Docker
- **Orchestration**: Docker Compose
- **Version Control**: Git
- **Python**: 3.10+
- **Node**: 18+

---

## 🔍 Troubleshooting Guide

### Port Already in Use
```bash
# Find process
lsof -i :3000    # Frontend
lsof -i :8000    # Backend
lsof -i :5432    # Database

# Kill process
kill -9 <PID>
```

### Database Connection Issues
```bash
# Restart database
docker compose down -v
docker compose up -d postgres
```

### Frontend Build Errors
```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json .next
npm install
npx tsc --noEmit
```

### Backend Import Errors
```bash
# Reinstall dependencies
cd sniper-backend
source .venv/bin/activate
pip install -r requirements.txt --upgrade
```

### Smoke Tests Fail
```bash
# Run individual checks
curl http://localhost:8000/health
curl http://localhost:8000/api/v1/strategy/
npm run typecheck
```

See **[COMMANDS.md](./COMMANDS.md)** for more troubleshooting.

---

## 📋 File Manifest

### Root Level
- `START_HERE.sh` — One-liner startup script
- `STARTUP_GUIDE.md` — Detailed setup instructions
- `COMMANDS.md` — Complete command reference
- `README_ALGO_PLATFORM.md` — Platform transformation overview
- `SYSTEM_STATUS.md` — Current system status
- `QUICK_START.md` — Original quick start guide
- `FIX_LOG.md` — Debugging history
- `VERIFICATION_CHECKLIST.md` — Pre-launch checklist
- `BUG_FIXES_SUMMARY.md` — Bug fixes and solutions
- `INDEX.md` — This file

### Configuration
- `.env.local` — Frontend environment variables (Clerk, Convex)
- `sniper-backend/.env` — Backend environment variables (database, broker)
- `package.json` — Frontend dependencies
- `sniper-backend/requirements.txt` — Backend dependencies
- `tsconfig.json` — TypeScript configuration
- `tailwind.config.ts` — Tailwind CSS configuration
- `docker-compose.yml` — Docker services definition

### Application Code
- `app/` — Next.js pages and routes
- `components/` — React components
- `hooks/` — Custom React hooks
- `lib/` — Utilities and helpers
- `store/` — Zustand state management
- `types/` — TypeScript type definitions
- `sniper-backend/app/` — FastAPI backend code
- `convex/` — Convex backend schema

---

## ✅ Pre-Flight Checklist

Before first run:
- [ ] Node.js v18+ installed
- [ ] Python 3.10+ installed
- [ ] Docker & Docker Compose installed
- [ ] All `.env` files in place
- [ ] Read `STARTUP_GUIDE.md`
- [ ] No services running on ports 3000, 8000, 5432

Before first deployment:
- [ ] `npm run build` succeeds
- [ ] `npx tsc --noEmit` passes
- [ ] `bash smoke-test.sh` passes
- [ ] All three services start without errors
- [ ] Can access http://localhost:3000
- [ ] Can access http://localhost:8000/docs

---

## 🎓 Learning Path

1. **Understand the Architecture** → Read `README_ALGO_PLATFORM.md`
2. **Start the Services** → Run `bash START_HERE.sh`
3. **Explore the UI** → Visit http://localhost:3000
4. **Create a Strategy** → Use Strategy Builder
5. **Run a Backtest** → Validate on historical data
6. **Activate Strategy** → Watch it trade automatically
7. **Check Logs & Docs** → Study `COMMANDS.md` and backend `/docs`

---

## 🆘 Getting Help

1. **Check Documentation**
   - `STARTUP_GUIDE.md` — Setup issues
   - `COMMANDS.md` — Command reference
   - `FIX_LOG.md` — Known issues
   - `http://localhost:8000/docs` — API reference

2. **Run Smoke Tests**
   ```bash
   bash smoke-test.sh
   ```

3. **Check Logs**
   ```bash
   docker compose logs postgres -f
   # Terminal 2 shows backend logs
   # Terminal 3 shows frontend logs
   ```

4. **Try Troubleshooting**
   - See "Troubleshooting Guide" in `COMMANDS.md`

---

## 📞 Support

| Issue | Solution |
|-------|----------|
| Port in use | See "Port Already in Use" in troubleshooting |
| Database won't start | See "Database Connection Issues" |
| Smoke tests fail | Check `FIX_LOG.md` for similar issues |
| Frontend won't build | Clear cache and reinstall |
| Backend won't start | Check Python virtual environment |

---

## 🚀 You're Ready!

**Next steps:**
1. Run: `bash START_HERE.sh`
2. Open: http://localhost:3000
3. Create your first algorithmic strategy
4. Run a backtest
5. Activate and watch it trade

For detailed guidance, see:
- **Setup**: `STARTUP_GUIDE.md`
- **Commands**: `COMMANDS.md`
- **Platform**: `README_ALGO_PLATFORM.md`

---

**Last Updated**: 2026-02-18
**Status**: ✅ Production Ready
**Version**: 1.0.0
