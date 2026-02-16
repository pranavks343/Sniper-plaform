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

## Docker

```bash
docker compose up --build
```

## API surface

- `GET /health`
- `POST /api/v1/strategy/`
- `POST /api/v1/execution/order`
- `GET /api/v1/risk/metrics`
- `POST /api/v1/backtest/`
- `GET /api/v1/quantum/status`
- WebSockets: `/ws/market`, `/ws/orders`, `/ws/positions`, `/ws/risk`
