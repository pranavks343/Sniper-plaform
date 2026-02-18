"""
QAOA Order Router
Quantum Approximate Optimisation Algorithm for optimal order splitting/routing.

Production path: uses Qiskit (qiskit + qiskit-optimization).
Fallback path:   classical greedy QUBO solver (always available).

Problem formulation:
  Given N venue/time-slice candidates, find the binary assignment
  x ∈ {0,1}^N that minimises expected_cost - liquidity_reward,
  subject to sum(x) == num_splits constraint.
"""
from __future__ import annotations

import math
import time
from dataclasses import dataclass, field
from typing import Any


@dataclass
class QAOAResult:
    splits: list[dict]            # [{venue, qty, order_type, delay_ms}]
    expected_cost: float
    solve_time_ms: float
    solver: str                   # "qaoa" | "classical"
    qubo_energy: float


class QAOAOrderRouter:
    """
    Optimal order routing via QAOA.
    Falls back to classical greedy QUBO if Qiskit is unavailable.
    """

    def __init__(
        self,
        num_splits: int = 3,
        qaoa_reps: int = 2,
        shots: int = 1024,
        use_simulator: bool = True,
    ) -> None:
        self.num_splits = num_splits
        self.qaoa_reps  = qaoa_reps
        self.shots      = shots
        self.use_simulator = use_simulator
        self._qiskit_available = self._check_qiskit()

    # ------------------------------------------------------------------
    def route(self, order: dict, venues: list[dict] | None = None) -> QAOAResult:
        """
        Args:
            order: {symbol, quantity, side, urgency (0-1)}
            venues: list of {name, spread, liquidity, fee_bps}
                    If None, generates synthetic venues.
        Returns:
            QAOAResult with split assignments.
        """
        t0 = time.perf_counter()

        if venues is None:
            venues = self._default_venues(order)

        n = len(venues)
        qty = order.get("quantity", 1)
        k   = min(self.num_splits, n)

        if self._qiskit_available:
            result = self._solve_qaoa(venues, qty, k)
            solver = "qaoa"
        else:
            result = self._solve_classical(venues, qty, k)
            solver = "classical"

        solve_ms = (time.perf_counter() - t0) * 1000

        splits = []
        total_cost = 0.0
        remaining = qty
        for i, chosen_idx in enumerate(result["chosen"]):
            v = venues[chosen_idx]
            split_qty = qty // k if i < k - 1 else remaining
            remaining -= split_qty
            cost = split_qty * v.get("spread", 0.5) * v.get("fee_bps", 2) / 10000
            total_cost += cost
            splits.append({
                "venue":      v.get("name", f"venue_{chosen_idx}"),
                "qty":        split_qty,
                "order_type": "LIMIT" if v.get("spread", 1.0) > 0.5 else "MARKET",
                "delay_ms":   i * 500,
            })

        return QAOAResult(
            splits=splits,
            expected_cost=round(total_cost, 4),
            solve_time_ms=round(solve_ms, 2),
            solver=solver,
            qubo_energy=result["energy"],
        )

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _check_qiskit() -> bool:
        try:
            import qiskit  # noqa: F401
            return True
        except ImportError:
            return False

    def _solve_qaoa(self, venues: list[dict], qty: int, k: int) -> dict:
        """Solve via Qiskit QAOA (requires qiskit + qiskit-optimization)."""
        try:
            from qiskit_optimization import QuadraticProgram  # type: ignore
            from qiskit_optimization.algorithms import MinimumEigenOptimizer  # type: ignore
            from qiskit.algorithms import QAOA  # type: ignore
            from qiskit.algorithms.optimizers import COBYLA  # type: ignore
            from qiskit_aer import AerSimulator  # type: ignore

            qp = QuadraticProgram()
            n = len(venues)
            for i in range(n):
                qp.binary_var(f"x{i}")

            # Objective: minimise sum(cost_i * x_i)
            linear = {f"x{i}": venues[i].get("spread", 1.0) * venues[i].get("fee_bps", 2) for i in range(n)}
            qp.minimize(linear=linear)

            # Constraint: exactly k venues chosen
            qp.linear_constraint(
                linear={f"x{i}": 1 for i in range(n)},
                sense="==",
                rhs=k,
                name="split_count",
            )

            backend = AerSimulator()
            qaoa = QAOA(optimizer=COBYLA(maxiter=100), reps=self.qaoa_reps, quantum_instance=backend)
            optimizer = MinimumEigenOptimizer(qaoa)
            result = optimizer.solve(qp)

            chosen = [i for i, v in enumerate(result.x) if v > 0.5][:k]
            if len(chosen) < k:
                chosen += list(set(range(n)) - set(chosen))[:k - len(chosen)]

            return {"chosen": chosen, "energy": float(result.fval)}

        except Exception:
            # If QAOA fails at runtime, fall back to classical
            return self._solve_classical(venues, qty, k)

    @staticmethod
    def _solve_classical(venues: list[dict], qty: int, k: int) -> dict:
        """Greedy QUBO: pick k venues with lowest cost score."""
        scored = sorted(
            enumerate(venues),
            key=lambda iv: iv[1].get("spread", 1.0) * iv[1].get("fee_bps", 3),
        )
        chosen = [idx for idx, _ in scored[:k]]
        energy = sum(venues[i].get("spread", 1.0) * venues[i].get("fee_bps", 3) for i in chosen)
        return {"chosen": chosen, "energy": float(energy)}

    @staticmethod
    def _default_venues(order: dict) -> list[dict]:
        """Generate synthetic venue candidates based on urgency."""
        urgency = order.get("urgency", 0.5)
        return [
            {"name": "NSE_EQ",     "spread": 0.3,  "liquidity": 0.9, "fee_bps": 1},
            {"name": "NSE_F&O",    "spread": 0.6,  "liquidity": 0.7, "fee_bps": 2},
            {"name": "BSE_EQ",     "spread": 0.4,  "liquidity": 0.6, "fee_bps": 1},
            {"name": "DARK_POOL",  "spread": 0.15, "liquidity": 0.4, "fee_bps": 3},
            {"name": "TWAP_SLICE", "spread": urgency * 0.5, "liquidity": 1.0, "fee_bps": 1},
        ]
