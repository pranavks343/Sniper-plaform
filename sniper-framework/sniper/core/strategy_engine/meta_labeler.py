"""
XGBoost Meta-Labeling
Filters primary signals using a secondary ML model that predicts whether
a trade will actually be profitable (bet-sizing / signal validation).

References: Lopez de Prado "Advances in Financial Machine Learning" Ch.3
"""
from __future__ import annotations

import json
import math
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import numpy as np


@dataclass
class MetaLabel:
    primary_signal: int        # 1 = take trade, 0 = skip
    confidence: float          # probability of trade being profitable (0-1)
    bet_size: float            # scaled position size (0-1)
    features_used: list[str]
    model_type: str            # "xgboost" | "logistic" | "heuristic"


class MetaLabeler:
    """
    Secondary classifier that decides WHETHER to take a primary signal.

    Production path: uses XGBoost (xgboost package).
    Fallback path:   logistic-regression-style sigmoid on hand-crafted features.

    Features fed to the model:
    - RSI, MACD, EMA spread, volume ratio
    - Regime confidence
    - Recent win streak / loss streak
    - Volatility (ATR%)
    """

    FEATURE_NAMES = [
        "rsi", "macd_hist", "ema_spread_pct",
        "vol_ratio", "regime_confidence",
        "win_streak", "loss_streak", "atr_pct",
    ]

    def __init__(self, model_path: str | None = None) -> None:
        self._model: Any = None
        self._model_type = "heuristic"
        self._threshold = 0.50       # minimum confidence to take trade
        self._fitted = False

        if model_path:
            self._load(model_path)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def predict(self, features: dict[str, float]) -> MetaLabel:
        """
        Args:
            features: dict with keys from FEATURE_NAMES
        Returns:
            MetaLabel with go/no-go decision and bet size
        """
        x = self._build_vector(features)
        confidence = self._score(x)
        take = 1 if confidence >= self._threshold else 0
        bet_size = self._kelly_bet_size(confidence)

        return MetaLabel(
            primary_signal=take,
            confidence=round(confidence, 4),
            bet_size=round(bet_size, 4),
            features_used=self.FEATURE_NAMES,
            model_type=self._model_type,
        )

    def fit(
        self,
        X: list[list[float]],
        y: list[int],
        eval_set: tuple | None = None,
    ) -> None:
        """
        Train the meta-labeler.
        Uses XGBoost if installed, else falls back to numpy logistic regression.

        Args:
            X: list of feature vectors (each = FEATURE_NAMES values)
            y: list of labels (1 = trade was profitable, 0 = not)
        """
        X_arr = np.array(X, dtype=float)
        y_arr = np.array(y, dtype=float)

        try:
            import xgboost as xgb  # type: ignore

            self._model = xgb.XGBClassifier(
                n_estimators=200,
                max_depth=4,
                learning_rate=0.05,
                subsample=0.8,
                colsample_bytree=0.8,
                use_label_encoder=False,
                eval_metric="logloss",
                random_state=42,
            )
            fit_kwargs: dict = {}
            if eval_set:
                fit_kwargs["eval_set"] = [eval_set]
                fit_kwargs["verbose"] = False
            self._model.fit(X_arr, y_arr, **fit_kwargs)
            self._model_type = "xgboost"
        except ImportError:
            # Fallback: train logistic regression via gradient descent
            self._weights = self._train_logistic(X_arr, y_arr)
            self._model_type = "logistic"

        self._fitted = True

    def save(self, path: str) -> None:
        """Persist model weights to disk."""
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        if self._model_type == "xgboost" and self._model is not None:
            self._model.save_model(str(p.with_suffix(".json")))
        elif self._model_type == "logistic" and hasattr(self, "_weights"):
            np.save(str(p.with_suffix(".npy")), self._weights)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _load(self, path: str) -> None:
        p = Path(path)
        try:
            import xgboost as xgb  # type: ignore

            m = xgb.XGBClassifier()
            m.load_model(str(p))
            self._model = m
            self._model_type = "xgboost"
            self._fitted = True
        except Exception:
            npy = p.with_suffix(".npy")
            if npy.exists():
                self._weights = np.load(str(npy))
                self._model_type = "logistic"
                self._fitted = True

    def _build_vector(self, features: dict[str, float]) -> np.ndarray:
        return np.array([features.get(k, 0.0) for k in self.FEATURE_NAMES], dtype=float)

    def _score(self, x: np.ndarray) -> float:
        if self._model_type == "xgboost" and self._model is not None:
            prob = self._model.predict_proba(x.reshape(1, -1))[0][1]
            return float(prob)
        if self._model_type == "logistic" and hasattr(self, "_weights"):
            logit = float(np.dot(self._weights[:-1], x) + self._weights[-1])
            return self._sigmoid(logit)
        # Heuristic fallback — weighted score on raw features
        rsi         = x[0]
        macd_hist   = x[1]
        regime_conf = x[4]
        win_streak  = x[5]
        loss_streak = x[6]

        score = 0.5
        if 40 < rsi < 60:
            score += 0.05
        if macd_hist > 0:
            score += 0.1
        score += regime_conf * 0.15
        score += win_streak * 0.02
        score -= loss_streak * 0.03
        return float(min(0.95, max(0.05, score)))

    @staticmethod
    def _sigmoid(x: float) -> float:
        return 1.0 / (1.0 + math.exp(-x))

    def _kelly_bet_size(self, p: float) -> float:
        """Continuous Kelly bet size from confidence probability."""
        if p <= 0.5:
            return 0.0
        # b = p / (1-p) simplified; fractional Kelly 0.25
        b = p / (1 - p)
        kelly = (b * p - (1 - p)) / b
        return round(min(1.0, max(0.0, kelly * 0.25)), 4)

    @staticmethod
    def _train_logistic(X: np.ndarray, y: np.ndarray, lr: float = 0.01, epochs: int = 500) -> np.ndarray:
        """Mini gradient-descent logistic regression."""
        n_feat = X.shape[1]
        w = np.zeros(n_feat + 1)  # +1 for bias
        X_b = np.c_[X, np.ones(len(X))]
        for _ in range(epochs):
            logits = X_b @ w
            preds = 1.0 / (1.0 + np.exp(-np.clip(logits, -20, 20)))
            grad = X_b.T @ (preds - y) / len(y)
            w -= lr * grad
        return w
