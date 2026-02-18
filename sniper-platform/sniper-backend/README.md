# Sniper Trading Backend

FastAPI backend implementing strategy, execution, risk, backtesting, and quantum control endpoints.

## Python version

Use **Python 3.11 or 3.12**. Python 3.13/3.14 are not yet supported by pydantic-core (build will fail). If you only have 3.14, install 3.12 (e.g. `brew install python@3.12`) and use it for the venv.

## Quick start

```bash
cp .env.example .env
# Use Python 3.12 or 3.11 for the venv (see above)
python3.12 -m venv .venv   # or: python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python scripts/train_models.py
python scripts/generate_sample_data.py
uvicorn app.main:app --reload --port 8000
```

Or run `./start-backend.sh` (it picks 3.12/3.11 if available).

## Database migrations (Alembic)

```bash
# With venv activated:
alembic upgrade head

# Or use the script (creates/uses .venv with a compatible Python):
bash scripts/run-alembic.sh upgrade head
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
