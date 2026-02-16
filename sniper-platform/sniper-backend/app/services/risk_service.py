from __future__ import annotations

from app.config import Settings
from app.core.risk_engine.circuit_breaker import CircuitBreaker
from app.core.risk_engine.greeks_calculator import GreeksCalculator
from app.core.risk_engine.hedge_optimizer_quantum import HedgeOptimizerQuantum
from app.core.risk_engine.limit_monitor import LimitMonitor


class RiskService:
    def __init__(self, settings: Settings, quantum_service) -> None:
        self.settings = settings
        self.quantum_service = quantum_service
        self.greeks_calculator = GreeksCalculator()
        self.circuit_breaker = CircuitBreaker()
        self.hedge_optimizer = HedgeOptimizerQuantum()
        self.limit_monitor = LimitMonitor(
            {
                'max_daily_loss_pct': settings.max_daily_loss_pct,
                'max_drawdown_pct': settings.max_drawdown_pct,
                'max_delta': settings.max_delta,
                'max_gamma': settings.max_gamma,
                'max_vega': settings.max_vega,
            }
        )
        self._portfolio_state = {
            'daily_loss_pct': 0.0,
            'drawdown_pct': 0.0,
            'delta': 0.0,
            'gamma': 0.0,
            'vega': 0.0,
        }

    def set_portfolio_state(self, state: dict) -> None:
        self._portfolio_state.update(state)

    def get_metrics(self) -> dict:
        status = self.limit_monitor.check_all_limits(self._portfolio_state)
        return {
            'daily_pnl': -self._portfolio_state['daily_loss_pct'],
            'drawdown': self._portfolio_state['drawdown_pct'],
            'delta': self._portfolio_state['delta'],
            'gamma': self._portfolio_state['gamma'],
            'vega': self._portfolio_state['vega'],
            'trading_allowed': status.trading_allowed and not self.circuit_breaker.status.active,
            'violations': status.violations,
        }

    def get_greeks(self) -> dict:
        return {
            'delta': self._portfolio_state['delta'],
            'gamma': self._portfolio_state['gamma'],
            'vega': self._portfolio_state['vega'],
            'theta': self._portfolio_state.get('theta', 0.0),
        }

    def get_limits(self) -> dict:
        return self.limit_monitor.limits

    def update_limits(self, limits: dict) -> dict:
        self.limit_monitor.limits.update({k: v for k, v in limits.items() if v is not None})
        return self.limit_monitor.limits

    def get_violations(self) -> list[dict]:
        return self.limit_monitor.get_violations()

    def activate_circuit_breaker(self, reason: str) -> dict:
        self.circuit_breaker.activate_breaker(reason)
        return self._breaker_payload()

    def deactivate_circuit_breaker(self, admin_password: str) -> dict:
        self.circuit_breaker.deactivate_breaker(admin_password)
        return self._breaker_payload()

    def _breaker_payload(self) -> dict:
        status = self.circuit_breaker.status
        return {
            'active': status.active,
            'reason': status.reason,
            'timestamp': status.timestamp,
            'actions_taken': status.actions_taken,
        }

    def check_pre_trade(self, proposed_position: dict) -> bool:
        return self.limit_monitor.check_pre_trade(proposed_position, self._portfolio_state) and not self.circuit_breaker.status.active
