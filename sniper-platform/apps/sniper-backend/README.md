# Sniper Trading Backend

FastAPI backend implementing strategy, execution, risk, backtesting, and quantum control endpoints.

## Quick start

```bash
cp .env.example .env
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python scripts/train_models.py
python scripts/generate_sample_data.py
uvicorn app.main:app --reload --port 8000
```

## Database migrations (Alembic)

```bash
alembic upgrade head
```

Schema namespaces used by this backend:

- `auth`: `users`, `user_preferences`
- `brokers`: `broker_accounts`
- `strategies`: `strategies`, `strategy_versions`
- `trading`: `orders`, `order_events`, `trades`
- `portfolio`: `position_snapshots`
- `risk`: `risk_limits`, `risk_breaches`, `circuit_breaker_events`
- `backtest`: `backtest_runs`, `backtest_metrics`, `backtest_trades`
- `analytics`: `pnl_intraday`, `pnl_daily`, `quantum_usage`
- `audit`: `audit_logs`

Timescale hypertables (when extension is available):

- `portfolio.position_snapshots` on `as_of`
- `analytics.pnl_intraday` on `as_of`

## Docker

```bash
docker compose up --build
```

## Broker configuration

Set broker mode in `.env`:

```bash
BROKER_PROVIDER=paper   # paper | upstox | zerodha | dhan
```

For Upstox mode:

```bash
UPSTOX_API_KEY=...
UPSTOX_API_SECRET=...
UPSTOX_REDIRECT_URI=...
UPSTOX_ACCESS_TOKEN=... # optional for scaffolded adapter
DATA_ENCRYPTION_KEY=... # required when BROKER_PROVIDER is not paper
```

## Convex configuration (replaces Redis)

Set these in `.env`:

```bash
CONVEX_DEPLOYMENT=...
CONVEX_URL=https://<your-deployment>.convex.cloud
CONVEX_DEPLOY_KEY=...
```

The backend uses Convex for event persistence and an in-process event bus for websocket fan-out.

## API surface

- `GET /health`
- `POST /api/v1/strategy/`
- `POST /api/v1/execution/order`
- `GET /api/v1/risk/metrics`
- `POST /api/v1/backtest/`
- `GET /api/v1/quantum/status`
- WebSockets: `/ws/market`, `/ws/orders`, `/ws/positions`, `/ws/risk`
