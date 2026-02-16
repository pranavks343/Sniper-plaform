from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from app.config import Settings


class BacktestService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.jobs: dict[str, dict] = {}

    def create_backtest(self, payload: dict) -> dict:
        job_id = str(uuid4())
        self.jobs[job_id] = {
            'job_id': job_id,
            'status': 'completed',
            'progress': 1.0,
            'created_at': datetime.utcnow(),
            'payload': payload,
            'results': self._mock_result(payload),
        }
        return {'job_id': job_id, 'status': 'completed', 'progress': 1.0}

    def get_status(self, job_id: str) -> dict:
        return {'job_id': job_id, 'status': self.jobs[job_id]['status'], 'progress': self.jobs[job_id]['progress']}

    def get_results(self, job_id: str) -> dict:
        return self.jobs[job_id]['results']

    def list_backtests(self) -> list[dict]:
        return [
            {
                'job_id': job_id,
                'status': data['status'],
                'progress': data['progress'],
                'strategy_id': data['payload'].get('strategy_id'),
                'created_at': data['created_at'],
            }
            for job_id, data in self.jobs.items()
        ]

    def _mock_result(self, payload: dict) -> dict:
        initial = float(payload['initial_capital'])
        final = initial * 1.18
        equity_curve = [{'t': i, 'value': initial * (1 + i / 200)} for i in range(100)]
        trades = [
            {'symbol': 'NIFTY', 'side': 'BUY', 'qty': 50, 'entry': 100 + i, 'exit': 100.5 + i, 'pnl': 25.0}
            for i in range(10)
        ]
        return {
            'job_id': payload.get('job_id', ''),
            'metrics': {
                'total_return': (final - initial) / initial,
                'cagr': 0.18,
                'sharpe': 1.9,
                'sortino': 2.2,
                'max_drawdown': 0.08,
                'win_rate': 0.62,
                'final_capital': final,
            },
            'equity_curve': equity_curve,
            'trades': trades,
            'drawdowns': [{'t': 10, 'drawdown': -0.03}, {'t': 20, 'drawdown': -0.05}],
        }
