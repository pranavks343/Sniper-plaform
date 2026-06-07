"""Quantum portfolio optimisation.

Formulates cardinality-constrained mean-variance asset selection as a QUBO
and solves it with QAOA (via :class:`app.quantum.qaoa_engine.QAOAEngine`),
falling back to a classical Markowitz-style ranking when needed.

QUBO objective (binary x_i = include asset i):

    minimise  -mu^T x  +  q * x^T Sigma x  +  P * (sum_i x_i - k)^2

where
    mu     = expected returns
    Sigma  = covariance matrix
    q      = risk-aversion coefficient
    k      = target number of assets (cardinality)
    P      = penalty weight enforcing the cardinality constraint
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from app.quantum.qaoa_engine import QAOAEngine


@dataclass
class PortfolioSolution:
    selected_assets: list[str]
    weights: np.ndarray
    cost: float
    feasible: bool


class PortfolioQuantumOptimizer:
    def __init__(self, risk_aversion: float = 1.0, qaoa_reps: int = 2) -> None:
        self.risk_aversion = risk_aversion
        self.engine = QAOAEngine(reps=qaoa_reps)

    # ------------------------------------------------------------------
    # QUBO construction
    # ------------------------------------------------------------------

    def build_qubo(
        self,   
        assets: list[str],
        returns: np.ndarray,
        covariances: np.ndarray,
        constraints: dict,
    ) -> dict:
        returns = np.asarray(returns, dtype=float)
        cov = np.asarray(covariances, dtype=float)
        n = len(assets)
        k = int(constraints.get("target_k", min(10, n)))
        q = float(constraints.get("risk_aversion", self.risk_aversion))

        # Penalty must dominate the objective so the constraint is respected.
        scale = float(np.abs(returns).max() + np.abs(cov).max() + 1e-9)
        P = float(constraints.get("penalty", 2.0 * scale * max(n, 1)))

        Q = np.zeros((n, n), dtype=float)
        for i in range(n):
            Q[i, i] = -returns[i] + q * cov[i, i] + P * (1.0 - 2.0 * k)
        for i in range(n):
            for j in range(i + 1, n):
                qij = q * cov[i, j] + P
                Q[i, j] = qij
                Q[j, i] = qij

        offset = P * (k ** 2)
        return {
            "Q": Q,
            "offset": offset,
            "assets": assets,
            "returns": returns,
            "cov": cov,
            "constraints": constraints,
            "target_k": k,
            "risk_aversion": q,
            "penalty": P,
        }

    # ------------------------------------------------------------------
    # Solve
    # ------------------------------------------------------------------

    def solve_with_qaoa(self, qubo: dict) -> dict:
        """Solve the portfolio QUBO with QAOA (matrix path) or fall back."""
        if qubo.get("Q") is None:
            qubo = self.build_qubo(
                qubo["assets"],
                qubo["returns"],
                qubo["cov"],
                qubo.get("constraints", {"target_k": qubo.get("target_k", 10)}),
            )
        result = self.engine.solve_qubo(np.asarray(qubo["Q"], dtype=float), offset=float(qubo["offset"]))
        result.setdefault("feasible", True)
        return result

    def decode_solution(self, bitstring: str, assets: list[str]) -> list[str]:
        return [asset for i, asset in enumerate(assets) if i < len(bitstring) and bitstring[i] == "1"]

    def calculate_weights(self, selected_assets: list[str], returns_map: dict[str, float]) -> np.ndarray:
        raw = np.array([max(returns_map.get(a, 0.0), 0.001) for a in selected_assets], dtype=float)
        weights = raw / np.sum(raw)
        return weights

    def optimize(
        self,
        assets: list[str],
        returns: np.ndarray,
        covariances: np.ndarray,
        target_k: int = 10,
    ) -> PortfolioSolution:
        """End-to-end: build QUBO -> QAOA -> decode -> weight."""
        returns = np.asarray(returns, dtype=float)
        covariances = np.asarray(covariances, dtype=float)
        qubo = self.build_qubo(assets, returns, covariances, {"target_k": target_k})    
        result = self.solve_with_qaoa(qubo)
        selected = self.decode_solution(result["solution"], assets)
        if not selected:  # guard against degenerate empty selection
            return self.classical_markowitz(assets, returns, covariances, target_k)
        returns_map = {a: float(returns[i]) for i, a in enumerate(assets)}
        weights = self.calculate_weights(selected, returns_map)
        return PortfolioSolution(
            selected_assets=selected,
            weights=weights,
            cost=float(result["cost"]),
            feasible=bool(result.get("feasible", True)),
        )

    def classical_markowitz(
        self,
        assets: list[str],
        returns: np.ndarray,
        covariances: np.ndarray,
        k: int = 10,
    ) -> PortfolioSolution:
        score = returns / (np.sqrt(np.diag(covariances)) + 1e-9)
        idx = np.argsort(score)[-k:]
        selected = [assets[i] for i in idx]
        raw = np.maximum(returns[idx], 1e-4)
        weights = raw / np.sum(raw)
        cost = float(-np.dot(weights, returns[idx]))
        return PortfolioSolution(selected_assets=selected, weights=weights, cost=cost, feasible=True)
