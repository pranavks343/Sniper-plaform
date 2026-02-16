from __future__ import annotations

from datetime import datetime
from pathlib import Path
from uuid import uuid4

import joblib

from app.config import Settings
from app.core.strategy_engine.feature_engineering import FeatureEngineering
from app.core.strategy_engine.meta_labeler import MetaLabeler
from app.core.strategy_engine.regime_detector import HMMRegimeDetector
from app.core.strategy_engine.signal_generator import SignalGenerator
from app.models.schemas.common import Regime


class StrategyService:
    def __init__(self, settings: Settings, quantum_service) -> None:
        self.settings = settings
        self.quantum_service = quantum_service
        self._strategies: dict[str, dict] = {}
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

    def create(self, payload: dict) -> dict:
        strategy_id = str(uuid4())
        strategy = {
            'id': strategy_id,
            'user_id': 'default-user',
            'name': payload['name'],
            'type': payload['type'],
            'parameters': payload.get('parameters', {}),
            'status': 'inactive',
            'regime_filters': payload.get('regime_filters', []),
            'created_at': datetime.utcnow(),
        }
        self._strategies[strategy_id] = strategy
        return strategy

    def list(self, status: str | None = None, regime: Regime | None = None) -> list[dict]:
        values = list(self._strategies.values())
        if status:
            values = [s for s in values if s['status'] == status]
        if regime:
            values = [s for s in values if not s['regime_filters'] or regime in s['regime_filters']]
        return values

    def get(self, strategy_id: str) -> dict:
        return self._strategies[strategy_id]

    def update(self, strategy_id: str, payload: dict) -> dict:
        strategy = self._strategies[strategy_id]
        strategy.update({k: v for k, v in payload.items() if v is not None})
        return strategy

    def delete(self, strategy_id: str) -> None:
        self._strategies.pop(strategy_id, None)

    def activate(self, strategy_id: str) -> dict:
        self._strategies[strategy_id]['status'] = 'active'
        return self._strategies[strategy_id]

    def deactivate(self, strategy_id: str) -> dict:
        self._strategies[strategy_id]['status'] = 'inactive'
        return self._strategies[strategy_id]

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
