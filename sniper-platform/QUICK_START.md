# Quick Start Guide - Sniper Trading Platform

## ✅ Current Status: ALL SYSTEMS OPERATIONAL

---

## Services Running

| Service | Status | URL | Port |
|---------|--------|-----|------|
| Frontend | ✅ Running | http://localhost:3000 | 3000 |
| Backend | ✅ Running | http://localhost:8000 | 8000 |
| Database | ✅ Running | localhost:5432 | 5432 |
| Convex | ✅ Connected | https://robust-tern-944.convex.cloud | - |

---

## Verify Everything Works

Run the smoke test suite:
```bash
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

---

## Test the Trading Flow

### 1. Create a Strategy
```bash
curl -X POST http://localhost:8000/api/v1/strategy/ \
  -H "Content-Type: application/json" \
  -d '{"name":"My Strategy","type":"momentum","parameters":{"threshold":0.7}}'
```

Copy the `id` from the response.

### 2. Place an Order
```bash
curl -X POST http://localhost:8000/api/v1/execution/order \
  -H "Content-Type: application/json" \
  -d '{"symbol":"NIFTY","side":"BUY","quantity":100,"order_type":"MARKET","strategy_id":"<STRATEGY_ID>"}'
```

### 3. Check Your Position
```bash
curl http://localhost:8000/api/v1/execution/positions | python3 -m json.tool
```

### 4. Check Risk Metrics
```bash
curl http://localhost:8000/api/v1/risk/metrics | python3 -m json.tool
```

---

## Restart Services (If Needed)

### Stop Everything
```bash
# Stop frontend (Ctrl+C in terminal 14)
# Stop backend (Ctrl+C in terminal 106977)
docker compose down
```

### Start Everything
```bash
# Terminal 1: Database
docker compose up -d postgres

# Terminal 2: Backend
cd sniper-backend
source .venv/bin/activate
uvicorn app.main:app --reload --port 8000

# Terminal 3: Frontend
npm run dev
```

---

## Access the Application

- **Frontend**: http://localhost:3000
- **Backend API Docs**: http://localhost:8000/docs
- **Backend ReDoc**: http://localhost:8000/redoc

---

## Key API Endpoints

### Strategies
- `GET /api/v1/strategy/` - List all strategies
- `POST /api/v1/strategy/` - Create strategy
- `POST /api/v1/strategy/{id}/activate` - Activate strategy

### Orders & Execution
- `POST /api/v1/execution/order` - Place order
- `GET /api/v1/execution/orders` - List orders
- `GET /api/v1/execution/positions` - Get positions

### Risk
- `GET /api/v1/risk/metrics` - Get risk metrics
- `GET /api/v1/risk/violations` - Get violations

### Quantum
- `GET /api/v1/quantum/status` - Quantum system status

---

## Environment Files

### Frontend: `.env.local`
```bash
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_***
CLERK_SECRET_KEY=sk_test_***
NEXT_PUBLIC_CONVEX_URL=https://robust-tern-944.convex.cloud
```

### Backend: `sniper-backend/.env`
```bash
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/sniper
BROKER_PROVIDER=paper
```

---

## Troubleshooting

### Backend won't start
```bash
cd sniper-backend
source .venv/bin/activate
python -c "from app.main import app; print('OK')"
```

### Database connection issues
```bash
docker ps | grep postgres
# Should show: sniper-postgres Up X minutes
```

### Frontend build errors
```bash
npm install
npx tsc --noEmit
```

---

## Development Mode

Current configuration:
- ✅ Paper trading (no real money)
- ✅ Simulated market data
- ✅ Local database
- ✅ Development CORS (localhost:3000)

To enable real trading:
1. Add broker API keys to `sniper-backend/.env`
2. Set `BROKER_PROVIDER=upstox` (or zerodha/dhan)
3. Restart backend

---

## Documentation

- **System Status**: `SYSTEM_STATUS.md` - Complete system overview
- **Fix Log**: `FIX_LOG.md` - Detailed debugging history
- **API Docs**: http://localhost:8000/docs - Interactive API documentation

---

## Support

If something isn't working:
1. Check `SYSTEM_STATUS.md` for detailed status
2. Run `bash smoke-test.sh` to identify issues
3. Check terminal logs for errors
4. Verify environment variables are set

---

**Last Updated**: 2026-02-17  
**Status**: ✅ All systems operational
