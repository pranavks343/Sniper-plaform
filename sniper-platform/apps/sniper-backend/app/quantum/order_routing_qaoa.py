from __future__ import annotations

from app.quantum.qaoa_engine import QAOAEngine


class OrderRoutingQAOA:
    def __init__(self) -> None:
        self.engine = QAOAEngine()

    def solve(self, qubo: dict) -> dict:
        result = self.engine.solve(qubo)
        return {'solution': result['solution'], 'cost': result['cost'], 'feasible': result['feasible'], 'solve_time_ms': result['solve_time_ms']}
