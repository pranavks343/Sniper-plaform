from __future__ import annotations

from dataclasses import dataclass


@dataclass
class RiskStatus:
    violations: list[dict]
    trading_allowed: bool
    warnings: list[str]


class LimitMonitor:
    def __init__(self, limits: dict[str, float]) -> None:
        self.limits = limits
        self._violations: list[dict] = []

    def check_all_limits(self, portfolio_state: dict) -> RiskStatus:
        violations: list[dict] = []

        checks = {
            'daily_loss_pct': ('max_daily_loss_pct', abs(portfolio_state.get('daily_loss_pct', 0.0))),
            'drawdown_pct': ('max_drawdown_pct', abs(portfolio_state.get('drawdown_pct', 0.0))),
            'delta': ('max_delta', abs(portfolio_state.get('delta', 0.0))),
            'gamma': ('max_gamma', abs(portfolio_state.get('gamma', 0.0))),
            'vega': ('max_vega', abs(portfolio_state.get('vega', 0.0))),
        }

        for metric, (limit_key, value) in checks.items():
            limit = float(self.limits.get(limit_key, float('inf')))
            if value > limit:
                violations.append(
                    {
                        'type': metric,
                        'severity': 'critical' if metric in {'daily_loss_pct', 'drawdown_pct'} else 'high',
                        'value': value,
                        'limit': limit,
                        'action_taken': 'trading_halt' if metric in {'daily_loss_pct', 'drawdown_pct'} else 'alert',
                    }
                )

        self._violations.extend(violations)
        return RiskStatus(violations=violations, trading_allowed=not any(v['severity'] == 'critical' for v in violations), warnings=[v['type'] for v in violations])

    def check_pre_trade(self, new_position: dict, current_portfolio: dict) -> bool:
        next_delta = abs(current_portfolio.get('delta', 0.0) + new_position.get('delta', 0.0))
        next_gamma = abs(current_portfolio.get('gamma', 0.0) + new_position.get('gamma', 0.0))
        return next_delta <= self.limits.get('max_delta', float('inf')) and next_gamma <= self.limits.get('max_gamma', float('inf'))

    def get_violations(self) -> list[dict]:
        return list(self._violations[-200:])

    def calculate_margin_requirement(self, positions: list[dict]) -> float:
        return float(sum(abs(p.get('quantity', 0)) * p.get('current_price', 0) * 0.2 for p in positions))
