from __future__ import annotations

from dataclasses import dataclass

import numpy as np

try:
    from qiskit_optimization import QuadraticProgram
except Exception:  # pragma: no cover
    QuadraticProgram = object


@dataclass
class PortfolioSolution:
    selected_assets: list[str]
    weights: np.ndarray
    cost: float
    feasible: bool


class PortfolioQuantumOptimizer:
    def build_qubo(self, assets: list[str], returns: np.ndarray, covariances: np.ndarray, constraints: dict) -> dict:
        target_k = int(constraints.get('target_k', min(10, len(assets))))
        return {
            'assets': assets,
            'returns': returns,
            'cov': covariances,
            'constraints': constraints,
            'target_k': target_k,
        }

    def solve_with_qaoa(self, qubo: dict) -> dict:
        # Practical fallback until a live quantum backend is configured.
        returns = np.asarray(qubo['returns'], dtype=float)
        cov = np.asarray(qubo['cov'], dtype=float)
        score = returns / (np.sqrt(np.diag(cov)) + 1e-9)
        k = int(qubo['target_k'])
        idx = np.argsort(score)[-k:]
        bitstring = ''.join('1' if i in idx else '0' for i in range(len(score)))
        return {'solution': bitstring, 'cost': float(-np.sum(score[idx])), 'feasible': True}

    def decode_solution(self, bitstring: str, assets: list[str]) -> list[str]:
        return [asset for i, asset in enumerate(assets) if i < len(bitstring) and bitstring[i] == '1']

    def calculate_weights(self, selected_assets: list[str], returns_map: dict[str, float]) -> np.ndarray:
        raw = np.array([max(returns_map.get(a, 0.0), 0.001) for a in selected_assets], dtype=float)
        weights = raw / np.sum(raw)
        return weights

    def classical_markowitz(self, assets: list[str], returns: np.ndarray, covariances: np.ndarray, k: int = 10) -> PortfolioSolution:
        score = returns / (np.sqrt(np.diag(covariances)) + 1e-9)
        idx = np.argsort(score)[-k:]
        selected = [assets[i] for i in idx]
        raw = np.maximum(returns[idx], 1e-4)
        weights = raw / np.sum(raw)
        cost = float(-np.dot(weights, returns[idx]))
        return PortfolioSolution(selected_assets=selected, weights=weights, cost=cost, feasible=True)
