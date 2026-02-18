# 📋 Complete Command Reference

## 🚀 Quick Start (Copy & Paste)

### Option 1: Automated (Recommended)
```bash
cd /Users/pranavks/project/sniper-platform
bash START_HERE.sh
```
Opens frontend at http://localhost:3000

---

### Option 2: Manual (3 Terminals)

**Terminal 1 — Database:**
```bash
cd /Users/pranavks/project/sniper-platform
docker compose up -d postgres
```

**Terminal 2 — Backend:**
```bash
cd /Users/pranavks/project/sniper-platform/sniper-backend
source .venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

**Terminal 3 — Frontend:**
```bash
cd /Users/pranavks/project/sniper-platform
npm run dev
```

Then open: **http://localhost:3000**

---

## 📦 Installation & Setup

### First-time Frontend Setup
```bash
cd /Users/pranavks/project/sniper-platform
npm install
npx tsc --noEmit  # Verify TypeScript
```

### First-time Backend Setup
```bash
cd /Users/pranavks/project/sniper-platform/sniper-backend

# Create virtual environment
python3 -m venv .venv

# Activate it
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run database migrations
alembic upgrade head
```

### First-time Database Setup
```bash
cd /Users/pranavks/project/sniper-platform
docker compose up -d postgres

# Wait for it to be ready
sleep 5

# Verify it's running
docker ps | grep postgres
```

---

## 🔧 Backend Commands

### Start Backend
```bash
cd /Users/pranavks/project/sniper-platform/sniper-backend
source .venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

### Stop Backend
```bash
# Press Ctrl+C in the backend terminal
# Or kill the process:
lsof -i :8000 | grep -oE "PID|[0-9]+" | head -2 | tail -1 | xargs kill -9
```

### Check Backend Health
```bash
curl http://localhost:8000/health
# Response: {"status":"ok"}
```

### Backend API Documentation
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Key API Endpoints
```bash
# List strategies
curl http://localhost:8000/api/v1/strategy/ | python3 -m json.tool

# Get risk metrics
curl http://localhost:8000/api/v1/risk/metrics | python3 -m json.tool

# Get quantum status
curl http://localhost:8000/api/v1/quantum/status | python3 -m json.tool

# Get positions
curl http://localhost:8000/api/v1/execution/positions | python3 -m json.tool

# Create strategy
curl -X POST http://localhost:8000/api/v1/strategy/ \
  -H "Content-Type: application/json" \
  -d '{"name":"My Strategy","type":"momentum","parameters":{"threshold":0.7}}'
```

### Backend Logs
```bash
# View in current terminal (already visible if running with --reload)

# Or check Docker logs if running in container
docker compose logs sniper-backend -f
```

### Database Connection
```bash
# Connect to PostgreSQL directly
docker exec -it sniper-postgres psql -U postgres -d sniper

# Useful psql commands:
# \dt          - list all tables
# \d orders    - describe 'orders' table
# SELECT * FROM strategies;
# \q           - quit
```

### Run Database Migrations
```bash
cd /Users/pranavks/project/sniper-platform/sniper-backend
source .venv/bin/activate

# Create new migration
alembic revision --autogenerate -m "Add new column"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1
```

---

## 🎨 Frontend Commands

### Start Frontend (Dev Mode)
```bash
cd /Users/pranavks/project/sniper-platform
npm run dev
```
Opens at: http://localhost:3000

### Stop Frontend
```bash
# Press Ctrl+C in the frontend terminal
# Or kill the process:
lsof -i :3000 | grep -oE "PID|[0-9]+" | head -2 | tail -1 | xargs kill -9
```

### Build Frontend (Production)
```bash
cd /Users/pranavks/project/sniper-platform
npm run build
npm start
```

### TypeScript Check
```bash
cd /Users/pranavks/project/sniper-platform
npm run typecheck
# or
npx tsc --noEmit
```

### Linting
```bash
cd /Users/pranavks/project/sniper-platform
npm run lint
```

### Install/Update Dependencies
```bash
cd /Users/pranavks/project/sniper-platform
npm install
npm update
```

### Clear Frontend Cache
```bash
cd /Users/pranavks/project/sniper-platform
rm -rf .next
rm -rf node_modules
npm install
```

---

## 🐳 Docker Commands

### Start Database Only
```bash
docker compose up -d postgres
```

### Stop Database
```bash
docker compose down postgres
```

### Stop Everything
```bash
docker compose down
```

### View Docker Logs
```bash
docker compose logs postgres -f
```

### Check Running Containers
```bash
docker ps
```

### Connect to Container
```bash
docker exec -it sniper-postgres bash
```

### Remove Everything & Start Fresh
```bash
docker compose down -v  # -v removes volumes
docker compose up -d postgres
```

---

## 🧪 Testing & Verification

### Run Smoke Tests
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

### Manual API Test
```bash
# Create a strategy
STRATEGY_ID=$(curl -s -X POST http://localhost:8000/api/v1/strategy/ \
  -H "Content-Type: application/json" \
  -d '{"name":"Test","type":"momentum","parameters":{"threshold":0.7}}' \
  | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])")

echo "Created strategy: $STRATEGY_ID"

# Get it back
curl http://localhost:8000/api/v1/strategy/$STRATEGY_ID | python3 -m json.tool
```

---

## 🛑 Stopping & Restarting

### Stop Everything Gracefully
```bash
# Terminal 2 (Backend): Ctrl+C
# Terminal 3 (Frontend): Ctrl+C
# Terminal 1 (Database):
docker compose down
```

### Emergency Stop (Force Kill)
```bash
pkill -f "uvicorn"
pkill -f "next dev"
docker compose down -v
```

### Full System Restart
```bash
# 1. Stop everything
docker compose down
pkill -f "uvicorn"
pkill -f "next dev"

# 2. Clear caches
rm -rf /Users/pranavks/project/sniper-platform/.next
rm -rf /Users/pranavks/project/sniper-platform/node_modules

# 3. Restart services (see "Quick Start" above)
```

---

## 🔍 Debugging

### Check All Ports in Use
```bash
lsof -i -P -n | grep LISTEN
```

### Check Specific Ports
```bash
lsof -i :3000   # Frontend
lsof -i :8000   # Backend
lsof -i :5432   # Database
```

### Kill Process on Port
```bash
kill -9 $(lsof -t -i :3000)   # Frontend
kill -9 $(lsof -t -i :8000)   # Backend
kill -9 $(lsof -t -i :5432)   # Database
```

### Check Backend Imports
```bash
cd /Users/pranavks/project/sniper-platform/sniper-backend
source .venv/bin/activate
python3 -c "from app.main import app; print('✅ Imports OK')"
```

### View Node Modules Size
```bash
du -sh /Users/pranavks/project/sniper-platform/node_modules
```

### Check Disk Space
```bash
df -h
```

---

## 📊 Monitoring

### Monitor Frontend Performance
- Open http://localhost:3000
- Press F12 → Performance tab
- Record a session and analyze

### Monitor Backend Performance
- Open http://localhost:8000/docs
- Check response times in browser DevTools

### Monitor Database
```bash
# Connect to database
docker exec -it sniper-postgres psql -U postgres -d sniper

# Check table sizes
SELECT schemaname, tablename, pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename))
FROM pg_tables
WHERE schemaname != 'pg_catalog'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

# Check active connections
SELECT * FROM pg_stat_activity;
```

---

## 🔐 Environment Variables

### View Frontend Env
```bash
cat /Users/pranavks/project/sniper-platform/.env.local
```

### View Backend Env
```bash
cat /Users/pranavks/project/sniper-platform/sniper-backend/.env
```

### Update Frontend Env
```bash
nano /Users/pranavks/project/sniper-platform/.env.local
# Edit and save, then restart frontend
```

### Update Backend Env
```bash
nano /Users/pranavks/project/sniper-platform/sniper-backend/.env
# Edit and save, then restart backend
```

---

## 📦 Dependency Management

### Update All Frontend Dependencies
```bash
cd /Users/pranavks/project/sniper-platform
npm update
npm audit fix  # Fix vulnerabilities
```

### Update All Backend Dependencies
```bash
cd /Users/pranavks/project/sniper-platform/sniper-backend
source .venv/bin/activate
pip install --upgrade -r requirements.txt
```

### Check for Outdated Packages
```bash
# Frontend
cd /Users/pranavks/project/sniper-platform
npm outdated

# Backend
cd /Users/pranavks/project/sniper-platform/sniper-backend
source .venv/bin/activate
pip list --outdated
```

---

## 🚀 Deployment

### Build Frontend for Production
```bash
cd /Users/pranavks/project/sniper-platform
npm run build
npm start  # Starts on port 3000
```

### Build Backend Docker Image (Future)
```bash
# This would be in sniper-backend/Dockerfile
# For now, backend runs directly with uvicorn
```

---

## 📚 Useful Links

| Service | URL | Purpose |
|---------|-----|---------|
| Frontend | http://localhost:3000 | Main application |
| Backend API | http://localhost:8000 | API endpoint |
| API Docs (Swagger) | http://localhost:8000/docs | Interactive API documentation |
| API Docs (ReDoc) | http://localhost:8000/redoc | Alternative API documentation |
| Database | localhost:5432 | PostgreSQL connection |

---

## 🎯 Common Workflows

### Workflow 1: Development
```bash
# Terminal 1
docker compose up -d postgres

# Terminal 2
cd sniper-backend && source .venv/bin/activate && uvicorn app.main:app --reload --port 8000

# Terminal 3
cd sniper-platform && npm run dev

# Now make code changes, they auto-reload
```

### Workflow 2: Testing a New Strategy
```bash
# 1. Create strategy via frontend (http://localhost:3000)
# 2. Run backtest
# 3. Check results
# 4. Activate strategy
# 5. Monitor in Live Trading
```

### Workflow 3: Database Debugging
```bash
# Connect to database
docker exec -it sniper-postgres psql -U postgres -d sniper

# Check a table
SELECT * FROM strategies LIMIT 5;

# Count rows
SELECT COUNT(*) FROM strategies;

# Exit
\q
```

---

## 🆘 Emergency Commands

### Database is Corrupted
```bash
docker compose down -v  # Remove volume
docker compose up -d postgres  # Recreate
cd sniper-backend && source .venv/bin/activate && alembic upgrade head
```

### Port Conflicts
```bash
# Find what's using the port
lsof -i :8000

# Kill it
kill -9 <PID>
```

### Virtual Environment is Broken
```bash
cd sniper-backend
rm -rf .venv
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
```

### Node Modules are Broken
```bash
cd sniper-platform
rm -rf node_modules package-lock.json
npm install
```

---

## 📋 Checklist Before Asking for Help

- [ ] All three services are running (`docker ps`, check terminals)
- [ ] No error messages in logs
- [ ] Ports are correct (3000, 8000, 5432)
- [ ] Smoke tests pass (`bash smoke-test.sh`)
- [ ] Frontend loads at http://localhost:3000
- [ ] Backend API responds at http://localhost:8000/health
- [ ] Database container is running
- [ ] `.env.local` has valid Clerk keys
- [ ] `sniper-backend/.env` exists

---

**Last Updated**: 2026-02-18
**Status**: ✅ Production Ready
