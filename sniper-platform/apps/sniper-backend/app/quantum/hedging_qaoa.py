from __future__ import annotations

from app.quantum.qaoa_engine import QAOAEngine


class HedgingQAOA:
    def __init__(self) -> None:
        self.engine = QAOAEngine()

    def solve(self, qubo: dict) -> dict:
        return self.engine.solve(qubo)
