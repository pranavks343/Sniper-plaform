from __future__ import annotations

import numpy as np

from app.core.strategy_engine.portfolio_quantum import PortfolioQuantumOptimizer
from app.quantum.qaoa_engine import QAOAEngine


class PortfolioQAOA:
    """Thin adapter exposing portfolio QUBO optimisation over QAOA."""

    def __init__(self, qaoa_reps: int = 2) -> None:
        self.optimizer = PortfolioQuantumOptimizer(qaoa_reps=qaoa_reps)
        self.engine = QAOAEngine(reps=qaoa_reps)

    def solve(self, qubo: dict) -> dict:
        # Real matrix QUBO -> QAOA. Builds the matrix from returns/cov if absent.
        if qubo.get("Q") is None and "returns" in qubo and "cov" in qubo:
            qubo = self.optimizer.build_qubo(
                qubo["assets"],
                qubo["returns"],
                qubo["cov"],
                qubo.get("constraints", {"target_k": qubo.get("target_k", 10)}),
            )
        return self.engine.solve(qubo)

    def optimize(self, assets, returns, covariances, target_k: int = 10):
        return self.optimizer.optimize(assets, np.asarray(returns), np.asarray(covariances), target_k)
