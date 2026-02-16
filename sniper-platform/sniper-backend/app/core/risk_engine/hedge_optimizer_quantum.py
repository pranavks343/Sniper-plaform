from __future__ import annotations


class HedgeOptimizerQuantum:
    def build_hedging_qubo(self, positions: list[dict], current_greeks: dict, target_greeks: dict, available_hedges: list[dict]) -> dict:
        return {
            'positions': positions,
            'current_greeks': current_greeks,
            'target_greeks': target_greeks,
            'available_hedges': available_hedges,
        }

    def solve_with_qaoa(self, qubo: dict) -> dict:
        positions = sorted(qubo['positions'], key=lambda x: abs(x.get('delta', 0.0)), reverse=True)
        target = abs(qubo['target_greeks'].get('delta', 0.0))
        current = abs(qubo['current_greeks'].get('delta', 0.0))
        to_close = []
        running = current
        for p in positions:
            if running <= target:
                break
            to_close.append(p.get('id', p.get('symbol', 'UNKNOWN')))
            running -= abs(p.get('delta', 0.0))
        return {'solution': {'positions_to_close': to_close, 'hedges_to_add': []}, 'cost': float(len(to_close) * 25), 'feasible': running <= target}

    def decode_hedging_plan(self, solution: dict) -> dict:
        return {
            'positions_to_close': solution.get('positions_to_close', []),
            'hedges_to_add': solution.get('hedges_to_add', []),
        }

    def calculate_new_greeks(self, positions: list[dict], hedges: list[dict]) -> dict:
        delta = sum(p.get('delta', 0.0) for p in positions) + sum(h.get('delta', 0.0) for h in hedges)
        gamma = sum(p.get('gamma', 0.0) for p in positions) + sum(h.get('gamma', 0.0) for h in hedges)
        vega = sum(p.get('vega', 0.0) for p in positions) + sum(h.get('vega', 0.0) for h in hedges)
        return {'delta': delta, 'gamma': gamma, 'vega': vega}
