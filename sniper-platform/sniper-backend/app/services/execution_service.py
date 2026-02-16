from __future__ import annotations

from datetime import datetime
from pathlib import Path
from uuid import uuid4

import joblib

from app.brokers.paper_trading import PaperTradingBroker
from app.config import Settings
from app.core.execution_engine.cost_estimator import CostEstimator
from app.core.execution_engine.order_router import SmartOrderRouter
from app.core.execution_engine.order_router_quantum import QuantumOrderRouter, QuantumRoutingConfig
from app.core.execution_engine.rl_agent import PPOExecutionAgent


class ExecutionService:
    def __init__(self, settings: Settings, quantum_service, risk_service) -> None:
        self.settings = settings
        self.quantum_service = quantum_service
        self.risk_service = risk_service
        self.cost_estimator = CostEstimator()
        self.rl_agent = PPOExecutionAgent()
        self.classical_router = SmartOrderRouter()
        self.quantum_router = QuantumOrderRouter()
        self.broker = PaperTradingBroker()
        self.broker.connect({})
        self.orders: dict[str, dict] = {}
        self.trades: dict[str, dict] = {}

    def load_models(self, models_dir: str) -> None:
        path = Path(models_dir) / 'ppo_execution.joblib'
        if path.exists():
            artifact = joblib.load(path)
            if 'weights' in artifact:
                self.rl_agent.weights = artifact['weights']

    def place_order(self, payload: dict) -> dict:
        symbol = payload['symbol']
        quantity = int(payload['quantity'])
        raw_side = payload['side']
        side = raw_side.value if hasattr(raw_side, 'value') else str(raw_side)

        if not self.risk_service.check_pre_trade({'delta': quantity if side == 'BUY' else -quantity, 'gamma': 0.0}):
            raise ValueError('pre-trade risk check failed')

        market_state = {
            'price': float(payload.get('price') or 100.0),
            'spread': 0.05,
            'avg_daily_volume': 2_000_000,
            'instrument_type': 'FUT',
        }

        if self.settings.enable_quantum_routing and quantity * market_state['price'] >= self.settings.quantum_routing_min_order_size:
            decision = self.quantum_router.route({'quantity': quantity}, market_state, QuantumRoutingConfig())
            self.quantum_service.record_solve('routing', decision.solve_time_ms, decision.expected_cost, True)
        else:
            decision = self.classical_router.route({'quantity': quantity}, market_state)

        costs = self.cost_estimator.estimate_total_cost(
            symbol=symbol,
            quantity=quantity,
            order_type=decision.order_type,
            urgency=float(payload.get('urgency', 0.5)),
            market_state=market_state,
            side=side,
        )

        broker_order = self.broker.place_order(
            symbol=symbol,
            quantity=quantity,
            order_type=decision.order_type,
            price=market_state['price'],
            side=side,
        )

        order_id = str(uuid4())
        order = {
            'id': order_id,
            'symbol': symbol,
            'side': side,
            'quantity': quantity,
            'order_type': decision.order_type,
            'status': 'COMPLETE',
            'price': market_state['price'],
            'filled_qty': broker_order['filled_qty'],
            'avg_price': broker_order['avg_price'],
            'strategy_id': payload.get('strategy_id'),
            'timestamp': datetime.utcnow(),
            'costs': costs.__dict__,
            'routing': decision.__dict__,
        }
        self.orders[order_id] = order

        trade_id = str(uuid4())
        self.trades[trade_id] = {
            'id': trade_id,
            'order_id': order_id,
            'symbol': symbol,
            'side': side,
            'quantity': quantity,
            'entry_price': order['avg_price'],
            'exit_price': None,
            'pnl': 0.0,
            'entry_time': datetime.utcnow(),
            'exit_time': None,
        }
        return order

    def list_orders(self, status: str | None = None, strategy_id: str | None = None) -> list[dict]:
        orders = list(self.orders.values())
        if status:
            orders = [o for o in orders if o['status'] == status]
        if strategy_id:
            orders = [o for o in orders if o.get('strategy_id') == strategy_id]
        return orders

    def get_order(self, order_id: str) -> dict:
        return self.orders[order_id]

    def cancel_order(self, order_id: str) -> dict:
        order = self.orders[order_id]
        order['status'] = 'CANCELLED'
        return order

    def get_positions(self) -> list[dict]:
        positions = self.broker.get_positions()
        for pos in positions:
            pos.setdefault('delta', 0.0)
            pos.setdefault('gamma', 0.0)
            pos.setdefault('theta', 0.0)
            pos.setdefault('vega', 0.0)
        return positions

    def list_trades(self, strategy_id: str | None = None, symbol: str | None = None) -> list[dict]:
        trades = list(self.trades.values())
        if strategy_id:
            order_ids = {o['id'] for o in self.orders.values() if o.get('strategy_id') == strategy_id}
            trades = [t for t in trades if t['order_id'] in order_ids]
        if symbol:
            trades = [t for t in trades if t['symbol'] == symbol]
        return trades
