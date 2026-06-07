"""Real (non-mock) backtest of the research engine.

Exercises the platform's actual classes — HMMRegimeDetector, SignalGenerator,
MetaLabeler — on simulated regime-switching price data, and compares two
strategies out-of-sample:

  A) Primary signals only      (take every EMA/RSI/MACD/volume signal)
  B) Meta-labelled signals     (take a signal only if the XGBoost meta-labeler
                                predicts trade quality >= threshold)

Reports trades, win rate, false-signal rate, per-trade Sharpe and max drawdown
for each, so the improvement from meta-labelling is quantified honestly.

Run:  PYTHONPATH=. python scripts/backtest_real.py
"""
from __future__ import annotations

import numpy as np

from app.core.strategy_engine.meta_labeler import MetaLabeler
from app.core.strategy_engine.regime_detector import HMMRegimeDetector
from app.core.strategy_engine.signal_generator import SignalGenerator
from app.models.schemas.common import Regime


def simulate_bars(n: int, seed: int = 11) -> list[dict]:
    """Regime-switching OHLCV series: trending / choppy / volatile segments."""
    rng = np.random.default_rng(seed)
    price = 18000.0
    bars: list[dict] = []
    i = 0
    while i < n:
        regime = rng.choice(['trend_up', 'trend_down', 'chop', 'volatile'],
                            p=[0.35, 0.15, 0.3, 0.2])
        seg_len = int(rng.integers(40, 90))
        if regime == 'trend_up':
            drift, vol = 8.0, rng.uniform(8, 18)
        elif regime == 'trend_down':
            drift, vol = -8.0, rng.uniform(8, 18)
        elif regime == 'chop':
            drift, vol = 0.0, rng.uniform(10, 20)
        else:  # volatile
            drift, vol = rng.uniform(-4, 4), rng.uniform(35, 70)
        for _ in range(seg_len):
            ret = drift + rng.normal(0, vol)
            price = max(1000.0, price + ret)
            vol_traded = rng.uniform(8e5, 1.5e6) * (1.3 if regime.startswith('trend') else 1.0)
            bars.append({'close': price, 'volume': vol_traded,
                         'high': price + abs(rng.normal(0, vol)),
                         'low': price - abs(rng.normal(0, vol))})
            i += 1
            if i >= n:
                break
    return bars


def collect_trades(bars: list[dict], hold: int = 30) -> list[dict]:
    """Walk the series, fire primary signals, label by forward return."""
    detector = HMMRegimeDetector(lookback=100)
    prices_all = np.array([b['close'] for b in bars], dtype=float)
    detector.train(prices_all[: len(prices_all) // 2])  # train regime model in-sample
    siggen = SignalGenerator()

    trades: list[dict] = []
    for i in range(120, len(bars) - hold):
        window = prices_all[i - 100:i]
        # HMM produces a regime + confidence used as a meta-label feature.
        regime_state = detector.predict_regime(window)
        # The signal generator's 3-of-4 technical vote (EMA/RSI/MACD/volume) is
        # the actual trend gate; we let it decide which bars produce a signal.
        signals = siggen.generate_signals(bars[i - 60:i], Regime.TRENDING)
        if not signals:
            continue
        sig = signals[0]
        entry = bars[i]['close']
        exit_price = bars[i + hold]['close']
        ret = (exit_price - entry) / entry  # BUY
        local_vol = float(np.std(np.diff(window[-20:]) / window[-20:-1]))
        trades.append({
            'idx': i,
            'ret': ret,
            'profitable': int(ret > 0),
            'features': {
                'signal_strength': sig.confidence,
                'regime_confidence': regime_state.confidence,
                'volatility': min(1.0, local_vol * 50),
                'spread': 0.05,
                'time_of_day': 0.5,
            },
        })
    return trades


def metrics(rets: list[float]) -> dict:
    if not rets:
        return {'trades': 0, 'win_rate': 0.0, 'false_rate': 0.0,
                'sharpe': 0.0, 'avg_ret_bps': 0.0, 'max_dd': 0.0}
    r = np.array(rets, dtype=float)
    wins = float(np.mean(r > 0))
    sharpe = float(np.mean(r) / (np.std(r) + 1e-9))
    equity = np.cumprod(1.0 + r)
    peak = np.maximum.accumulate(equity)
    max_dd = float(np.max((peak - equity) / peak)) if len(equity) else 0.0
    return {
        'trades': len(r),
        'win_rate': round(wins, 4),
        'false_rate': round(1 - wins, 4),
        'sharpe': round(sharpe, 4),
        'avg_ret_bps': round(float(np.mean(r)) * 1e4, 2),
        'max_dd': round(max_dd, 4),
    }


def main() -> None:
    bars = simulate_bars(4000)
    trades = collect_trades(bars)
    print(f'Total primary signals fired: {len(trades)}')
    if len(trades) < 20:
        print('Too few signals to evaluate; adjust simulation.')
        return

    split = len(trades) // 2
    train_t, test_t = trades[:split], trades[split:]

    # Train meta-labeler in-sample.
    X = np.array([[t['features'][k] for k in
                   ('signal_strength', 'regime_confidence', 'volatility', 'spread', 'time_of_day')]
                  for t in train_t], dtype=float)
    y = np.array([t['profitable'] for t in train_t], dtype=int)
    ml = MetaLabeler()
    ml.train(X, y)

    # Pre-compute OOS quality scores once.
    scored = [(t['ret'], ml.predict_quality(t['features'])) for t in test_t]

    ma = metrics([r for r, _ in scored])
    print('\n=== Out-of-sample results: A) primary vs B) meta-labelled ===')
    print(f"{'metric':<14}{'A: primary':>14}")
    for k in ('trades', 'win_rate', 'false_rate', 'sharpe', 'avg_ret_bps', 'max_dd'):
        print(f'{k:<14}{ma[k]:>14}')

    print('\nB) meta-labelled at increasing quality thresholds:')
    print(f"{'threshold':>10}{'trades':>8}{'win_rate':>10}{'false_rate':>12}{'sharpe':>9}{'max_dd':>9}")
    for thr in (0.50, 0.55, 0.60, 0.65, 0.70):
        b = metrics([r for r, q in scored if q >= thr])
        print(f"{thr:>10.2f}{b['trades']:>8}{b['win_rate']:>10}{b['false_rate']:>12}{b['sharpe']:>9}{b['max_dd']:>9}")


if __name__ == '__main__':
    main()
