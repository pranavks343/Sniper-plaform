from __future__ import annotations

import numpy as np


class FeatureEngineering:
    def _safe_return(self, series: np.ndarray, periods: int) -> float:
        if len(series) <= periods:
            return 0.0
        return float((series[-1] - series[-1 - periods]) / max(series[-1 - periods], 1e-9))

    def _ema(self, prices: np.ndarray, period: int) -> float:
        if len(prices) < period:
            return float(prices[-1])
        alpha = 2 / (period + 1)
        ema = prices[0]
        for price in prices[1:]:
            ema = alpha * price + (1 - alpha) * ema
        return float(ema)

    def _rsi(self, prices: np.ndarray, period: int = 14) -> float:
        delta = np.diff(prices)
        up = np.where(delta > 0, delta, 0)
        down = np.where(delta < 0, -delta, 0)
        avg_up = np.mean(up[-period:]) if len(up) >= period else np.mean(up) if len(up) else 0
        avg_down = np.mean(down[-period:]) if len(down) >= period else np.mean(down) if len(down) else 0
        if avg_down == 0:
            return 100.0
        rs = avg_up / avg_down
        return float(100 - (100 / (1 + rs)))

    def calculate_momentum_features(self, bars: list[dict]) -> dict:
        close = np.asarray([b['close'] for b in bars], dtype=float)
        high = np.asarray([b.get('high', b['close']) for b in bars], dtype=float)
        low = np.asarray([b.get('low', b['close']) for b in bars], dtype=float)

        macd = self._ema(close, 12) - self._ema(close, 26)
        stochastic = float((close[-1] - low[-14:].min()) / max(high[-14:].max() - low[-14:].min(), 1e-9)) if len(close) >= 14 else 0.0
        adx_proxy = float(np.clip(np.std(np.diff(close[-20:])) * 100, 0, 100)) if len(close) > 20 else 20.0

        return {
            'rsi': self._rsi(close),
            'macd': macd,
            'adx': adx_proxy,
            'stochastic': stochastic,
        }

    def calculate_volatility_features(self, bars: list[dict]) -> dict:
        close = np.asarray([b['close'] for b in bars], dtype=float)
        high = np.asarray([b.get('high', b['close']) for b in bars], dtype=float)
        low = np.asarray([b.get('low', b['close']) for b in bars], dtype=float)

        returns = np.diff(np.log(np.maximum(close, 1e-9)))
        atr = float(np.mean(high[-14:] - low[-14:])) if len(high) >= 14 else float(np.mean(high - low))
        boll_width = float((np.std(close[-20:]) * 4) / max(np.mean(close[-20:]), 1e-9)) if len(close) >= 20 else 0.0
        parkinson = float(np.mean((np.log(np.maximum(high, 1e-9) / np.maximum(low, 1e-9))) ** 2) / (4 * np.log(2)))

        return {
            'atr': atr,
            'bollinger_width': boll_width,
            'parkinson': parkinson,
            'realized_volatility': float(np.std(returns)) if len(returns) else 0.0,
        }

    def calculate_all_features(self, bars: list[dict]) -> np.ndarray:
        close = np.asarray([b['close'] for b in bars], dtype=float)
        volume = np.asarray([b.get('volume', 0.0) for b in bars], dtype=float)

        m = self.calculate_momentum_features(bars)
        v = self.calculate_volatility_features(bars)

        features = {
            'ret_1': self._safe_return(close, 1),
            'ret_5': self._safe_return(close, 5),
            'ret_15': self._safe_return(close, 15),
            'log_ret': float(np.log(close[-1] / max(close[-2], 1e-9))) if len(close) > 1 else 0.0,
            'rsi': m['rsi'],
            'macd': m['macd'],
            'adx': m['adx'],
            'stochastic': m['stochastic'],
            'atr': v['atr'],
            'bollinger_width': v['bollinger_width'],
            'parkinson': v['parkinson'],
            'volume_ratio': float(volume[-1] / max(np.mean(volume[-20:]), 1e-9)) if len(volume) >= 20 else 1.0,
            'obv': float(np.sum(np.sign(np.diff(close, prepend=close[0])) * volume)),
            'vwap': float(np.sum(close * volume) / max(np.sum(volume), 1e-9)),
            'spread': float(bars[-1].get('spread', 0.0)),
            'order_imbalance': float(bars[-1].get('order_imbalance', 0.0)),
            'put_call_ratio': float(bars[-1].get('put_call_ratio', 1.0)),
            'iv_rank': float(bars[-1].get('iv_rank', 0.5)),
            'mtf_alignment': float(bars[-1].get('mtf_alignment', 0.0)),
            'realized_volatility': v['realized_volatility'],
            'ema_20': self._ema(close, 20),
            'ema_50': self._ema(close, 50),
        }   

        return np.array(list(features.values()), dtype=float)
