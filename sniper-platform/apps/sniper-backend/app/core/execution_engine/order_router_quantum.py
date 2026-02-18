from __future__ import annotations

import time
from dataclasses import dataclass

from app.core.execution_engine.order_router import RoutingDecision, SmartOrderRouter
from app.quantum.order_routing_qaoa import OrderRoutingQAOA


@dataclass
class QuantumRoutingConfig:
    max_cost: float = 5000.0


class QuantumOrderRouter:
    def __init__(self) -> None:
        self.qaoa = OrderRoutingQAOA()
        self.fallback = SmartOrderRouter()

    def build_routing_qubo(self, order: dict, market_state: dict, config: dict) -> dict:
        return {'order': order, 'market_state': market_state, 'config': config}

    def solve_with_qaoa(self, qubo: dict) -> dict:
        return self.qaoa.solve(qubo)

    def decode_routing_decision(self, bitstring: str) -> RoutingDecision:
        timing_map = {'00': 'now', '01': '5s', '10': '10s', '11': '30s'}
        order_type_map = {'00': 'MARKET', '01': 'LIMIT', '10': 'ICEBERG', '11': 'LIMIT'}
        splits_map = {'00': 1, '01': 2, '10': 3, '11': 5}

        timing = timing_map.get(bitstring[:2], 'now')
        order_type = order_type_map.get(bitstring[2:4], 'MARKET')
        splits = splits_map.get(bitstring[4:6], 1)
        venue = 'primary' if bitstring[-1] == '0' else 'secondary'
        return RoutingDecision(timing=timing, order_type=order_type, splits=splits, venue=venue, expected_cost=0.0, solve_time_ms=0.0)

    def route(self, order: dict, market_state: dict, config: QuantumRoutingConfig) -> RoutingDecision:
        try:
            start = time.perf_counter()
            qubo = self.build_routing_qubo(order, market_state, {'max_cost': config.max_cost})
            result = self.solve_with_qaoa(qubo)
            decision = self.decode_routing_decision(result['solution'])
            elapsed = (time.perf_counter() - start) * 1000
            decision.expected_cost = result.get('cost', decision.expected_cost)
            decision.solve_time_ms = elapsed
            return decision
        except Exception:
            return self.fallback.route(order, market_state)
