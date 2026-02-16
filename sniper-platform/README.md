# Sniper Trading System

Quantum-enhanced algorithmic trading platform scaffold with:

- **Frontend**: Next.js 14 App Router + Zustand + Tailwind
- **Backend**: FastAPI + modular Strategy/Execution/Risk/Quantum engines
- **Infra**: TimescaleDB + Redis + Docker Compose

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

## Run frontend locally

```bash
npm install
npm run dev
```

## Full stack via Docker

```bash
docker compose up --build
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
