from __future__ import annotations

from dataclasses import dataclass


@dataclass
class RoutingDecision:
    timing: str
    order_type: str
    splits: int
    venue: str
    expected_cost: float
    solve_time_ms: float


class SmartOrderRouter:
    def route(self, order: dict, market_state: dict) -> RoutingDecision:
        spread = market_state.get('spread', 0.5)
        if spread > 1.0:
            order_type = 'LIMIT'
            timing = '5s'
        else:
            order_type = 'MARKET'
            timing = 'now'

        splits = 1 if order.get('quantity', 0) < 500 else 3
        venue = 'primary'
        expected_cost = float(spread * order.get('quantity', 0) * 0.3)
        return RoutingDecision(timing=timing, order_type=order_type, splits=splits, venue=venue, expected_cost=expected_cost, solve_time_ms=2.0)
