from __future__ import annotations

import math

import numpy as np

try:
    from xgboost import XGBClassifier
except Exception:  # pragma: no cover
    XGBClassifier = None


class MetaLabeler:
    def __init__(self, threshold: float = 0.7) -> None:
        self.threshold = threshold
        self.model = (
            XGBClassifier(
                n_estimators=150,
                max_depth=4,
                learning_rate=0.05,
                subsample=0.9,
                colsample_bytree=0.9,
                eval_metric='logloss',
            )
            if XGBClassifier
            else None
        )
        self._trained = False

    def train(self, features: np.ndarray, labels: np.ndarray) -> None:
        if self.model is None:
            self._trained = True
            return
        self.model.fit(features, labels)
        self._trained = True

    def predict_quality(self, signal_features: dict[str, float]) -> float:
        vector = np.array(
            [
                signal_features.get('signal_strength', 0.0),
                signal_features.get('regime_confidence', 0.0),
                signal_features.get('volatility', 0.0),
                signal_features.get('spread', 0.0),
                signal_features.get('time_of_day', 0.5),
            ],
            dtype=float,
        )
        if self.model and self._trained:
            prob = float(self.model.predict_proba(vector.reshape(1, -1))[0, 1])
            return prob

        # Fallback logistic scoring calibrated to [0,1].
        score = 1.8 * vector[0] + 1.2 * vector[1] - 0.8 * vector[2] - 0.6 * vector[3] + 0.2 * vector[4]
        return float(1 / (1 + math.exp(-score)))

    def calculate_position_size(self, quality_score: float, capital: float) -> int:
        if quality_score < self.threshold:
            return 0
        edge = max(0.0, quality_score - 0.5)
        kelly_fraction = min(0.05, edge / 2)
        position_value = capital * kelly_fraction
        return int(position_value)
