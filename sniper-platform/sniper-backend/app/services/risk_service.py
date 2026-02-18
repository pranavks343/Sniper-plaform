from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.config import Settings
from app.core.risk_engine.circuit_breaker import CircuitBreaker
from app.core.risk_engine.greeks_calculator import GreeksCalculator
from app.core.risk_engine.hedge_optimizer_quantum import HedgeOptimizerQuantum
from app.core.risk_engine.limit_monitor import LimitMonitor
from app.models.database.audit import AuditLog
from app.models.database.risk import CircuitBreakerEvent, RiskBreach, RiskLimit
from app.utils.convex_bus import ConvexBus


class RiskService:
    def __init__(
        self,
        settings: Settings,
        quantum_service,
        event_bus: ConvexBus | None = None,
        session_factory: async_sessionmaker | None = None,
    ) -> None:
        self.settings = settings
        self.quantum_service = quantum_service
        self.event_bus = event_bus
        self.session_factory = session_factory
        self.greeks_calculator = GreeksCalculator()
        self.circuit_breaker = CircuitBreaker(admin_secret=settings.circuit_breaker_admin_secret)
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

    async def bootstrap_limits(self) -> None:
        if self.session_factory is None:
            return
        async with self.session_factory() as session:
            existing = (
                await session.execute(
                    select(RiskLimit)
                    .where(RiskLimit.user_id == self.settings.default_user_uuid)
                    .order_by(RiskLimit.updated_at.desc())
                )
            ).scalars().first()
            if existing is None:
                session.add(
                    RiskLimit(
                        id=str(uuid4()),
                        user_id=self.settings.default_user_uuid,
                        max_daily_loss_pct=self.settings.max_daily_loss_pct,
                        max_drawdown_pct=self.settings.max_drawdown_pct,
                        max_delta=self.settings.max_delta,
                        max_gamma=self.settings.max_gamma,
                        max_vega=self.settings.max_vega,
                        updated_by='bootstrap',
                    )
                )
                await session.commit()
            else:
                self.limit_monitor.limits.update(
                    {
                        'max_daily_loss_pct': existing.max_daily_loss_pct,
                        'max_drawdown_pct': existing.max_drawdown_pct,
                        'max_delta': existing.max_delta,
                        'max_gamma': existing.max_gamma,
                        'max_vega': existing.max_vega,
                    }
                )

    async def get_metrics(self) -> dict:
        metrics = self._build_metrics()
        await self._persist_violations(metrics.get('violations', []))
        self._publish_risk_update('risk:update', metrics)
        return metrics

    def _build_metrics(self) -> dict:
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

    async def get_greeks(self) -> dict:
        return {
            'delta': self._portfolio_state['delta'],
            'gamma': self._portfolio_state['gamma'],
            'vega': self._portfolio_state['vega'],
            'theta': self._portfolio_state.get('theta', 0.0),
        }

    async def get_limits(self) -> dict:
        if self.session_factory is not None:
            async with self.session_factory() as session:
                latest = (
                    await session.execute(
                        select(RiskLimit)
                        .where(RiskLimit.user_id == self.settings.default_user_uuid)
                        .order_by(RiskLimit.updated_at.desc())
                    )
                ).scalars().first()
                if latest is not None:
                    self.limit_monitor.limits.update(
                        {
                            'max_daily_loss_pct': latest.max_daily_loss_pct,
                            'max_drawdown_pct': latest.max_drawdown_pct,
                            'max_delta': latest.max_delta,
                            'max_gamma': latest.max_gamma,
                            'max_vega': latest.max_vega,
                        }
                    )
        return self.limit_monitor.limits

    async def update_limits(self, limits: dict) -> dict:
        self.limit_monitor.limits.update({k: v for k, v in limits.items() if v is not None})
        if self.session_factory is not None:
            async with self.session_factory() as session:
                session.add(
                    RiskLimit(
                        id=str(uuid4()),
                        user_id=self.settings.default_user_uuid,
                        max_daily_loss_pct=self.limit_monitor.limits['max_daily_loss_pct'],
                        max_drawdown_pct=self.limit_monitor.limits['max_drawdown_pct'],
                        max_delta=self.limit_monitor.limits['max_delta'],
                        max_gamma=self.limit_monitor.limits['max_gamma'],
                        max_vega=self.limit_monitor.limits['max_vega'],
                        updated_by='api',
                    )
                )
                session.add(
                    AuditLog(
                        id=str(uuid4()),
                        user_id=self.settings.default_user_uuid,
                        entity_type='risk_limits',
                        entity_id=self.settings.default_user_uuid,
                        action='update',
                        details=self._json_ready(self.limit_monitor.limits),
                        source='api',
                    )
                )
                await session.commit()
        self._publish_risk_update('risk:limits:update', self._build_metrics())
        return self.limit_monitor.limits

    async def get_violations(self) -> list[dict]:
        if self.session_factory is None:
            return self.limit_monitor.get_violations()
        async with self.session_factory() as session:
            rows = (
                await session.execute(
                    select(RiskBreach)
                    .where(RiskBreach.user_id == self.settings.default_user_uuid)
                    .order_by(RiskBreach.created_at.desc())
                    .limit(200)
                )
            ).scalars().all()
            return [
                {
                    'type': row.type,
                    'severity': row.severity,
                    'value': row.value,
                    'limit': row.limit,
                    'action_taken': row.action_taken,
                    'timestamp': row.created_at,
                }
                for row in rows
            ]

    async def activate_circuit_breaker(self, reason: str) -> dict:
        self.circuit_breaker.activate_breaker(reason)
        payload = self._breaker_payload()
        await self._persist_breaker_event('ACTIVATE', reason, payload)
        self._publish_risk_update('risk:breaker:update', self._build_metrics(), {'breaker': payload})
        return payload

    async def deactivate_circuit_breaker(self, admin_password: str) -> dict:
        self.circuit_breaker.deactivate_breaker(admin_password)
        payload = self._breaker_payload()
        await self._persist_breaker_event('DEACTIVATE', 'manual reset', payload)
        self._publish_risk_update('risk:breaker:update', self._build_metrics(), {'breaker': payload})
        return payload

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

    def _publish_risk_update(self, event: str, metrics: dict, extra: dict | None = None) -> None:
        if self.event_bus is None:
            return
        payload = {
            'metrics': self._json_ready(metrics),
            'limits': self._json_ready(self.limit_monitor.limits),
            'violations': self._json_ready(self.limit_monitor.get_violations()),
            'circuit_breaker': self._json_ready(self._breaker_payload()),
        }
        if extra:
            payload.update(self._json_ready(extra))
        self.event_bus.publish_event_nowait('risk:update', event, payload)
        self.event_bus.set_json_nowait('risk:latest', payload, ttl_seconds=86400)

    def _json_ready(self, value):
        if isinstance(value, datetime):
            return value.isoformat()
        if isinstance(value, dict):
            return {key: self._json_ready(val) for key, val in value.items()}
        if isinstance(value, list):
            return [self._json_ready(item) for item in value]
        return value

    async def _persist_violations(self, violations: list[dict]) -> None:
        if self.session_factory is None or not violations:
            return
        async with self.session_factory() as session:
            for violation in violations:
                session.add(
                    RiskBreach(
                        id=str(uuid4()),
                        user_id=self.settings.default_user_uuid,
                        type=str(violation.get('type', 'unknown')),
                        severity=str(violation.get('severity', 'medium')),
                        value=float(violation.get('value', 0.0)),
                        limit=float(violation.get('limit', 0.0)),
                        action_taken=violation.get('action_taken'),
                        details=self._json_ready(violation),
                    )
                )
            await session.commit()

    async def _persist_breaker_event(self, action: str, reason: str | None, payload: dict) -> None:
        if self.session_factory is None:
            return
        async with self.session_factory() as session:
            session.add(
                CircuitBreakerEvent(
                    id=str(uuid4()),
                    user_id=self.settings.default_user_uuid,
                    action=action,
                    reason=reason,
                    actor='api',
                    payload=self._json_ready(payload),
                )
            )
            session.add(
                AuditLog(
                    id=str(uuid4()),
                    user_id=self.settings.default_user_uuid,
                    entity_type='circuit_breaker',
                    entity_id=self.settings.default_user_uuid,
                    action=action.lower(),
                    details=self._json_ready(payload),
                    source='api',
                )
            )
            await session.commit()
