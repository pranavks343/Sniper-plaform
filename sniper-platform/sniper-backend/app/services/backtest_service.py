from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.config import Settings
from app.models.database.audit import AuditLog
from app.models.database.backtest import BacktestMetric, BacktestRun, BacktestTrade


class BacktestService:
    def __init__(self, settings: Settings, session_factory: async_sessionmaker) -> None:
        self.settings = settings
        self.session_factory = session_factory

    async def create_backtest(self, payload: dict) -> dict:
        job_id = str(uuid4())
        now = datetime.utcnow()
        mock = self._mock_result(payload)
        metrics = mock['metrics']
        trade_rows = mock['trades']

        async with self.session_factory() as session:
            run = BacktestRun(
                id=job_id,
                strategy_id=payload.get('strategy_id'),
                user_id=self.settings.default_user_uuid,
                status='completed',
                progress=1.0,
                start_date=payload['start_date'],
                end_date=payload['end_date'],
                initial_capital=float(payload['initial_capital']),
                final_capital=float(metrics.get('final_capital', 0.0)),
                transaction_cost_model=str(payload.get('transaction_cost_model', 'realistic')),
                config=payload,
                created_at=now,
                completed_at=now,
            )
            session.add(run)

            for metric_name, metric_value in metrics.items():
                if isinstance(metric_value, (int, float)):
                    session.add(
                        BacktestMetric(
                            id=str(uuid4()),
                            run_id=job_id,
                            metric_name=str(metric_name),
                            metric_value=float(metric_value),
                        )
                    )

            for trade in trade_rows:
                session.add(
                    BacktestTrade(
                        id=str(uuid4()),
                        run_id=job_id,
                        symbol=str(trade['symbol']),
                        side=str(trade['side']),
                        quantity=int(trade['qty']),
                        entry_price=float(trade['entry']),
                        exit_price=float(trade['exit']),
                        pnl=float(trade['pnl']),
                    )
                )

            session.add(
                AuditLog(
                    id=str(uuid4()),
                    user_id=self.settings.default_user_uuid,
                    entity_type='backtest',
                    entity_id=job_id,
                    action='create',
                    details={'strategy_id': payload.get('strategy_id')},
                    source='api',
                )
            )
            await session.commit()

        return {'job_id': job_id, 'status': 'completed', 'progress': 1.0}

    async def get_status(self, job_id: str) -> dict:
        async with self.session_factory() as session:
            run = await session.get(BacktestRun, job_id)
            if run is None:
                raise KeyError(job_id)
            return {'job_id': job_id, 'status': run.status, 'progress': run.progress}

    async def get_results(self, job_id: str) -> dict:
        async with self.session_factory() as session:
            run = await session.get(BacktestRun, job_id)
            if run is None:
                raise KeyError(job_id)

            metrics_rows = (
                await session.execute(select(BacktestMetric).where(BacktestMetric.run_id == job_id))
            ).scalars().all()
            trades_rows = (
                await session.execute(select(BacktestTrade).where(BacktestTrade.run_id == job_id).order_by(BacktestTrade.trade_time.asc()))
            ).scalars().all()

            metrics = {row.metric_name: row.metric_value for row in metrics_rows}
            trades = [
                {
                    'symbol': row.symbol,
                    'side': row.side,
                    'qty': row.quantity,
                    'entry': row.entry_price,
                    'exit': row.exit_price,
                    'pnl': row.pnl,
                }
                for row in trades_rows
            ]

            return {
                'job_id': run.id,
                'metrics': metrics,
                'equity_curve': self._mock_equity_curve(run.initial_capital),
                'trades': trades,
                'drawdowns': [{'t': 10, 'drawdown': -0.03}, {'t': 20, 'drawdown': -0.05}],
            }

    async def list_backtests(self) -> list[dict]:
        async with self.session_factory() as session:
            runs = (await session.execute(select(BacktestRun).order_by(BacktestRun.created_at.desc()))).scalars().all()
            return [
                {
                    'job_id': run.id,
                    'status': run.status,
                    'progress': run.progress,
                    'strategy_id': run.strategy_id,
                    'created_at': run.created_at,
                }
                for run in runs
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

    def _mock_equity_curve(self, initial: float) -> list[dict]:
        return [{'t': i, 'value': initial * (1 + i / 200)} for i in range(100)]
