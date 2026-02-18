# Sniper Trading System

Quantum-enhanced algorithmic trading platform scaffold with:

- **Frontend**: Next.js 14 App Router + Zustand + Tailwind
- **Backend**: FastAPI + modular Strategy/Execution/Risk/Quantum engines
- **Infra**: TimescaleDB + Convex + Docker Compose

## Monorepo layout

- `sniper-backend/`: FastAPI service and engine modules
- `app/`, `components/`, `hooks/`, `store/`: Next.js app
- `docker-compose.yml`: full stack orchestration

## Run backend locally

```bash
cd sniper-backend
cp .env.example .env
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python scripts/train_models.py
uvicorn app.main:app --reload --port 8000
```

To run with Upstox broker mode, set `BROKER_PROVIDER=upstox` plus `UPSTOX_API_KEY` and `UPSTOX_API_SECRET` in `sniper-backend/.env`.

## Run frontend locally

```bash
npm install
npm run dev
```

## Clerk (App Router) setup

1. Install SDK (already added in this repo):

```bash
npm install @clerk/nextjs@latest
```

2. Add keys to `.env.local`:

```bash
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=YOUR_PUBLISHABLE_KEY
CLERK_SECRET_KEY=YOUR_SECRET_KEY
```

You can copy from the template:

```bash
cp .env.local.example .env.local
```

3. Add Convex URL to `.env.local`:

```bash
NEXT_PUBLIC_CONVEX_URL=https://<your-deployment>.convex.cloud
```

4. Restart frontend dev server:

```bash
npm run dev
```

## Full stack via Docker

```bash
docker compose up --build
```

## Convex functions deployment

```bash
npm install convex
npx convex dev --once
```

In `sniper-backend/.env`, set:

```bash
CONVEX_DEPLOYMENT=...
CONVEX_URL=https://<your-deployment>.convex.cloud
CONVEX_DEPLOY_KEY=...
```

## Implemented API endpoints

- `GET /health`
- `POST /api/v1/strategy/`
- `GET /api/v1/strategy/`
- `POST /api/v1/execution/order`
- `GET /api/v1/execution/orders`
- `GET /api/v1/risk/metrics`
- `POST /api/v1/backtest/`
- `GET /api/v1/quantum/status`
- WebSocket streams: `/ws/market`, `/ws/orders`, `/ws/positions`, `/ws/risk`

## Notes

This is a production-oriented scaffold with fully wired modules, simplified model logic, and local fallbacks for external systems (broker APIs and live IBM Quantum jobs).
