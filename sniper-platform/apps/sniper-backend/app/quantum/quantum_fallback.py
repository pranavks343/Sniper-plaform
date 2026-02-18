from __future__ import annotations


class QuantumFallback:
    def solve_routing(self, order: dict, market_state: dict) -> dict:
        _ = market_state
        return {'timing': 'now', 'order_type': 'MARKET', 'splits': 1, 'venue': 'primary', 'expected_cost': order.get('quantity', 0) * 0.1}

    def solve_portfolio(self, assets: list[str]) -> dict:
        return {'selected_assets': assets[:10], 'method': 'markowitz'}

    def solve_hedging(self, positions: list[dict]) -> dict:
        return {'positions_to_close': [p.get('id') for p in positions[:2]], 'method': 'greedy'}
