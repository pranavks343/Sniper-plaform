from __future__ import annotations

from datetime import datetime
from pathlib import Path
from uuid import uuid4

import joblib
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.config import Settings
from app.core.strategy_engine.feature_engineering import FeatureEngineering
from app.core.strategy_engine.meta_labeler import MetaLabeler
from app.core.strategy_engine.regime_detector import HMMRegimeDetector
from app.core.strategy_engine.signal_generator import SignalGenerator
from app.models.database.audit import AuditLog
from app.models.database.strategy import Strategy, StrategyVersion
from app.models.schemas.common import Regime


class StrategyService:
    def __init__(self, settings: Settings, quantum_service, session_factory: async_sessionmaker) -> None:
        self.settings = settings
        self.quantum_service = quantum_service
        self.session_factory = session_factory
        self.regime_detector = HMMRegimeDetector()
        self.signal_generator = SignalGenerator()
        self.meta_labeler = MetaLabeler()
        self.feature_engineering = FeatureEngineering()

    def load_models(self, models_dir: str) -> None:
        meta_path = Path(models_dir) / 'meta_labeler.joblib'
        if meta_path.exists():
            artifact = joblib.load(meta_path)
            threshold = artifact.get('threshold')
            if threshold is not None:
                self.meta_labeler.threshold = float(threshold)

    async def create(self, payload: dict) -> dict:
        strategy_id = str(uuid4())
        created_at = datetime.utcnow()
        regime_filters = [r.value if hasattr(r, 'value') else str(r) for r in payload.get('regime_filters', [])]

        async with self.session_factory() as session:
            strategy = Strategy(
                id=strategy_id,
                user_id=self.settings.default_user_uuid,
                name=payload['name'],
                type=payload['type'],
                parameters=payload.get('parameters', {}),
                status='inactive',
                regime_filters=regime_filters,
                created_at=created_at,
            )
            version = StrategyVersion(
                id=str(uuid4()),
                strategy_id=strategy_id,
                version=1,
                parameters=strategy.parameters,
                status='inactive',
                changed_by='system',
                notes='initial version',
            )
            audit = AuditLog(
                id=str(uuid4()),
                user_id=self.settings.default_user_uuid,
                entity_type='strategy',
                entity_id=strategy_id,
                action='create',
                details={'name': strategy.name, 'type': strategy.type},
                source='api',
            )
            session.add_all([strategy, version, audit])
            await session.commit()
            await session.refresh(strategy)
            return self._to_dict(strategy)

    async def list(self, status: str | None = None, regime: Regime | None = None) -> list[dict]:
        async with self.session_factory() as session:
            query = select(Strategy).where(Strategy.deleted_at.is_(None))
            if status:
                query = query.where(Strategy.status == status)
            rows = (await session.execute(query.order_by(Strategy.created_at.desc()))).scalars().all()
            values = [self._to_dict(row) for row in rows]
            if regime:
                regime_value = regime.value if hasattr(regime, 'value') else str(regime)
                values = [s for s in values if not s['regime_filters'] or regime_value in s['regime_filters']]
            return values

    async def get(self, strategy_id: str) -> dict:
        async with self.session_factory() as session:
            row = await session.get(Strategy, strategy_id)
            if row is None or row.deleted_at is not None:
                raise KeyError(strategy_id)
            return self._to_dict(row)

    async def update(self, strategy_id: str, payload: dict) -> dict:
        async with self.session_factory() as session:
            row = await session.get(Strategy, strategy_id)
            if row is None or row.deleted_at is not None:
                raise KeyError(strategy_id)

            updates = {k: v for k, v in payload.items() if v is not None}
            if 'regime_filters' in updates:
                updates['regime_filters'] = [r.value if hasattr(r, 'value') else str(r) for r in updates['regime_filters']]
            for key, value in updates.items():
                setattr(row, key, value)

            current_version = (
                await session.execute(select(func.coalesce(func.max(StrategyVersion.version), 0)).where(StrategyVersion.strategy_id == strategy_id))
            ).scalar_one()
            session.add(
                StrategyVersion(
                    id=str(uuid4()),
                    strategy_id=strategy_id,
                    version=int(current_version) + 1,
                    parameters=row.parameters,
                    status=row.status,
                    changed_by='system',
                    notes='strategy update',
                )
            )
            session.add(
                AuditLog(
                    id=str(uuid4()),
                    user_id=self.settings.default_user_uuid,
                    entity_type='strategy',
                    entity_id=strategy_id,
                    action='update',
                    details={'fields': list(updates.keys())},
                    source='api',
                )
            )
            await session.commit()
            await session.refresh(row)
            return self._to_dict(row)

    async def delete(self, strategy_id: str) -> None:
        async with self.session_factory() as session:
            row = await session.get(Strategy, strategy_id)
            if row is None or row.deleted_at is not None:
                return
            row.deleted_at = datetime.utcnow()
            row.status = 'deleted'
            session.add(
                AuditLog(
                    id=str(uuid4()),
                    user_id=self.settings.default_user_uuid,
                    entity_type='strategy',
                    entity_id=strategy_id,
                    action='delete',
                    details={},
                    source='api',
                )
            )
            await session.commit()

    async def activate(self, strategy_id: str) -> dict:
        return await self.update(strategy_id, {'status': 'active'})

    async def deactivate(self, strategy_id: str) -> dict:
        return await self.update(strategy_id, {'status': 'inactive'})

    def evaluate_bars(self, bars: list[dict]) -> list[dict]:
        if len(bars) < 100:
            return []
        prices = [b['close'] for b in bars]
        regime_state = self.regime_detector.predict_regime(prices)
        signals = self.signal_generator.generate_signals(bars, regime_state.regime)
        approved_signals = []
        for signal in signals:
            quality = self.meta_labeler.predict_quality(
                {
                    'signal_strength': signal.confidence,
                    'regime_confidence': regime_state.confidence,
                    'volatility': abs(bars[-1].get('close', 0) - bars[-2].get('close', 0)) / max(bars[-2].get('close', 1), 1),
                    'spread': bars[-1].get('spread', 0.0),
                    'time_of_day': 0.5,
                }
            )
            if quality >= self.meta_labeler.threshold:
                approved_signals.append(
                    {
                        'direction': signal.direction,
                        'confidence': signal.confidence,
                        'entry_price': signal.entry_price,
                        'expected_hold_time': signal.expected_hold_time,
                        'quality_score': quality,
                        'regime': regime_state.regime,
                    }
                )
        return approved_signals

    def _to_dict(self, row: Strategy) -> dict:
        return {
            'id': row.id,
            'user_id': row.user_id,
            'name': row.name,
            'type': row.type,
            'parameters': row.parameters or {},
            'status': row.status,
            'regime_filters': row.regime_filters or [],
            'created_at': row.created_at,
        }
