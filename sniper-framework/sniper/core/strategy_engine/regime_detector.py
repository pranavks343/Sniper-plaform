"""Market regime detection (trending / mean-reverting / volatile) via features and optional HMM."""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from sniper.schemas.common import Regime

try:
    from hmmlearn.hmm import GaussianHMM
except Exception:  # pragma: no cover
    GaussianHMM = None


@dataclass
class RegimeState:
    regime: Regime
    confidence: float
    transition_prob: float


class HMMRegimeDetector:
    def __init__(self, lookback: int = 100) -> None:
        self.lookback = lookback
        self.model = (
            GaussianHMM(n_components=3, covariance_type="diag", n_iter=100)
            if GaussianHMM
            else None
        )
        self._trained = False

    def calculate_features(self, prices: np.ndarray) -> np.ndarray:
        returns = np.diff(np.log(np.maximum(prices, 1e-9)))
        if len(returns) < 15:
            raise ValueError("insufficient prices for feature extraction")
        hurst = self._calculate_hurst(prices)
        adx = self._calculate_adx(prices)
        vol_pct = float(np.percentile(np.abs(returns), 80))
        autocorr = (
            float(np.corrcoef(returns[:-1], returns[1:])[0, 1])
            if len(returns) > 2
            else 0.0
        )
        return np.array([hurst, adx, vol_pct, autocorr], dtype=float)

    def _calculate_hurst(self, prices: np.ndarray) -> float:
        prices = np.asarray(prices, dtype=float)
        if len(prices) < 20:
            return 0.5
        lags = range(2, min(20, len(prices) // 2))
        tau = [np.std(np.subtract(prices[lag:], prices[:-lag])) for lag in lags]
        if not tau or min(tau) <= 0:
            return 0.5
        poly = np.polyfit(np.log(list(lags)), np.log(tau), 1)
        return float(np.clip(poly[0], 0.0, 1.0))

    def _calculate_adx(self, prices: np.ndarray) -> float:
        prices = np.asarray(prices, dtype=float)
        if len(prices) < 15:
            return 25.0
        delta = np.diff(prices)
        up = np.where(delta > 0, delta, 0)
        down = np.where(delta < 0, -delta, 0)
        plus_di = 100 * np.mean(up[-14:]) / (np.mean(np.abs(delta[-14:])) + 1e-9)
        minus_di = 100 * np.mean(down[-14:]) / (np.mean(np.abs(delta[-14:])) + 1e-9)
        adx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di + 1e-9)
        return float(np.clip(adx, 0.0, 100.0))

    def train(self, historical_prices: np.ndarray) -> None:
        prices = np.asarray(historical_prices, dtype=float)
        windows = []
        for i in range(self.lookback, len(prices)):
            try:
                windows.append(
                    self.calculate_features(prices[i - self.lookback : i])
                )
            except ValueError:
                continue
        if not windows:
            raise ValueError("not enough data to train HMM regime detector")
        features = np.asarray(windows)
        if self.model:
            self.model.fit(features)
            self._trained = True
        else:
            self._trained = True

    def predict_regime(self, recent_prices: np.ndarray) -> RegimeState:
        features = self.calculate_features(
            np.asarray(recent_prices, dtype=float)
        ).reshape(1, -1)
        if self.model and self._trained:
            state_idx = int(self.model.predict(features)[0])
            probs = self.model.predict_proba(features)[0]
            confidence = float(probs[state_idx])
            transition_prob = float(np.max(self.model.transmat_[state_idx]))
        else:
            trend_strength = features[0, 1]
            volatility = features[0, 2]
            if trend_strength > 25 and volatility < 0.015:
                state_idx = 0
            elif volatility > 0.02:
                state_idx = 2
            else:
                state_idx = 1
            confidence = 0.65
            transition_prob = 0.6

        mapping = {
            0: Regime.TRENDING,
            1: Regime.MEAN_REVERTING,
            2: Regime.VOLATILE,
        }
        return RegimeState(
            regime=mapping.get(state_idx, Regime.MEAN_REVERTING),
            confidence=confidence,
            transition_prob=transition_prob,
        )
