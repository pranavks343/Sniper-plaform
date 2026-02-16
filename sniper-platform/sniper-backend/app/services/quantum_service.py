from __future__ import annotations

from datetime import datetime

from app.config import Settings
from app.models.schemas.quantum import QuantumStatus, QuantumUsageStats
from app.quantum.quantum_client import IBMQuantumClient


class QuantumService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.client = IBMQuantumClient()
        self._usage: list[dict] = []
        self._last_solve: str | None = None

    def connect(self) -> None:
        if self.settings.ibm_quantum_token:
            self.client.connect(self.settings.ibm_quantum_token)

    def record_solve(self, optimization_type: str, solve_time_ms: float, cost: float, success: bool) -> None:
        self._usage.append(
            {
                'timestamp': datetime.utcnow(),
                'optimization_type': optimization_type,
                'solve_time_ms': solve_time_ms,
                'cost': cost,
                'success': success,
            }
        )
        self._last_solve = datetime.utcnow().isoformat()

    def get_status(self) -> QuantumStatus:
        return QuantumStatus(
            available=self.client.connected,
            provider='IBM Quantum',
            backend=self.settings.ibm_quantum_backend,
            credits=100.0,
            last_solve=self._last_solve,
        )

    def get_usage(self) -> QuantumUsageStats:
        total = len(self._usage)
        avg = sum(item['solve_time_ms'] for item in self._usage) / total if total else 0.0
        monthly = sum(item['cost'] for item in self._usage)
        return QuantumUsageStats(total_solves=total, avg_solve_time_ms=avg, cost_this_month=monthly)

    def test_connection(self) -> dict:
        return {'available_backends': self.client.get_available_backends(), 'connected': self.client.connected}

    def update_config(self, payload: dict) -> dict:
        for key, value in payload.items():
            if value is not None and hasattr(self.settings, key):
                setattr(self.settings, key, value)
        return {
            'enable_quantum_routing': self.settings.enable_quantum_routing,
            'enable_quantum_portfolio': self.settings.enable_quantum_portfolio,
            'enable_quantum_hedging': self.settings.enable_quantum_hedging,
            'quantum_timeout_ms': self.settings.quantum_timeout_ms,
        }
