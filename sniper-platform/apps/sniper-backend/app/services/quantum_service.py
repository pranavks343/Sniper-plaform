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
        # Auto-connect on init using the token from .env so the engine is
        # always operational at startup (falls back to local simulation if
        # IBM Quantum cloud is unavailable).
        self._auto_connect()

    def _auto_connect(self) -> None:
        backend = (self.settings.ibm_quantum_backend or 'ibm_brisbane').strip()
        # Fast startup path: always enable local fallback immediately.
        # Cloud connect (if token exists) is handled separately with a timeout.
        self.client.connect('', backend)

    def connect(self, api_token: str | None = None) -> bool:
        token = (api_token or self.settings.ibm_quantum_token or '').strip()
        backend = (self.settings.ibm_quantum_backend or 'ibm_brisbane').strip()
        self.client.connect(token, backend)
        return self.client.connected

    def disconnect(self) -> dict:
        self.client.disconnect()
        return {'connected': self.client.connected}

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
        mode = getattr(self.client, 'mode', 'unknown')
        provider_map = {
            'ibm_cloud':   'IBM Quantum (cloud)',
            'aer_local':   'Qiskit Aer (local)',
            'numpy_local': 'NumPy Simulator (local)',
        }
        provider = provider_map.get(mode, 'IBM Quantum')
        return QuantumStatus(
            available=self.client.connected,
            provider=provider,
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
        if not self.client.connected:
            self._auto_connect()
        return {
            'available_backends': self.client.get_available_backends(),
            'connected': self.client.connected,
            'backend': self.settings.ibm_quantum_backend,
            'mode': getattr(self.client, 'mode', 'unknown'),
        }

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
