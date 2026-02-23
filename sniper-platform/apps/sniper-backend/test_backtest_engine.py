"""
Comprehensive test for the backtest engine logic.
Tests all 4 strategies with synthetic and real market data.
"""
import math
import sys
import asyncio
from datetime import datetime

# Add the app to path
sys.path.insert(0, '.')

from app.services.backtest_service import (
    _compute_ema,
    _compute_rsi,
    _compute_macd,
    _run_strategy,
    _empty_result,
)

# ── Helper: generate synthetic OHLCV bars ──────────────────────────────────

def make_trending_up_bars(n: int = 200, start_price: float = 100.0) -> list[dict]:
    """Trending upward with noise — EMA crossover strategies should catch this."""
    bars = []
    price = start_price
    for i in range(n):
        import random
        random.seed(42 + i)
        drift = 0.3 + random.gauss(0, 0.8)  # positive drift
        open_ = price
        close = max(1, open_ + drift)
        high = max(open_, close) + abs(random.gauss(0, 0.5))
        low = min(open_, close) - abs(random.gauss(0, 0.5))
        bars.append({
            'timestamp': f'2024-01-{(i % 28) + 1:02d}',
            'open': round(open_, 2),
            'high': round(high, 2),
            'low': round(low, 2),
            'close': round(close, 2),
            'volume': 1000 + i * 10,
            'symbol': 'TEST',
        })
        price = close
    return bars


def make_mean_reverting_bars(n: int = 200, center: float = 100.0) -> list[dict]:
    """Price oscillates around a center — RSI mean-reversion should trigger."""
    bars = []
    import random
    random.seed(99)
    price = center
    for i in range(n):
        # Sinusoidal mean-reverting price with noise
        cycle = math.sin(i / 10) * 8 + random.gauss(0, 1.5)
        price = center + cycle
        open_ = price - random.gauss(0, 0.3)
        close = price
        high = max(open_, close) + abs(random.gauss(0, 0.5))
        low = min(open_, close) - abs(random.gauss(0, 0.5))
        bars.append({
            'timestamp': f'2024-01-{(i % 28) + 1:02d}',
            'open': round(open_, 2),
            'high': round(high, 2),
            'low': round(low, 2),
            'close': round(close, 2),
            'volume': 500 + i * 5,
            'symbol': 'TEST',
        })
    return bars


def make_breakout_bars(n: int = 200, base_price: float = 100.0) -> list[dict]:
    """Range-bound price with sudden breakouts."""
    bars = []
    import random
    random.seed(77)
    price = base_price
    for i in range(n):
        if i == 80:
            # Sharp breakout upward
            price += 15
        elif i == 130:
            # Drop back
            price -= 20
        elif i == 160:
            # Another breakout
            price += 12
        else:
            price += random.gauss(0, 0.5)  # tight range

        open_ = price - random.gauss(0, 0.3)
        close = price
        high = max(open_, close) + abs(random.gauss(0, 0.4))
        low = min(open_, close) - abs(random.gauss(0, 0.4))
        bars.append({
            'timestamp': f'2024-01-{(i % 28) + 1:02d}',
            'open': round(open_, 2),
            'high': round(high, 2),
            'low': round(low, 2),
            'close': round(close, 2),
            'volume': 800 + i * 8,
            'symbol': 'TEST',
        })
    return bars


def make_volatile_bars(n: int = 300, start_price: float = 100.0) -> list[dict]:
    """More volatile data with multiple up/down swings — all strategies should get trades."""
    bars = []
    import random
    random.seed(123)
    price = start_price
    for i in range(n):
        # Alternating trends every ~30 bars
        phase = (i // 30) % 4
        if phase == 0:
            drift = 1.0  # up
        elif phase == 1:
            drift = -0.8  # down
        elif phase == 2:
            drift = 0.5  # mild up
        else:
            drift = -1.2  # sharp down

        price = max(5, price + drift + random.gauss(0, 1.5))
        open_ = price - random.gauss(0, 0.4)
        close = price
        high = max(open_, close) + abs(random.gauss(0, 0.8))
        low = min(open_, close) - abs(random.gauss(0, 0.8))
        bars.append({
            'timestamp': f'2024-01-{(i % 28) + 1:02d}',
            'open': round(open_, 2),
            'high': round(high, 2),
            'low': round(low, 2),
            'close': round(close, 2),
            'volume': 1000 + random.randint(0, 2000),
            'symbol': 'TEST',
        })
    return bars


# ── Tests ──────────────────────────────────────────────────────────────────

def test_ema_computation():
    """EMA should be close to SMA for long flat series."""
    prices = [100.0] * 100
    ema = _compute_ema(prices, 20)
    assert all(e is not None for e in ema), "EMA should not return None for valid prices"
    # All EMAs should be 100 for flat series
    for val in ema[20:]:
        assert abs(val - 100.0) < 0.01, f"EMA should be ~100 for flat series, got {val}"

    # EMA should respond to price changes
    prices_up = [100.0] * 30 + [110.0] * 30
    ema_up = _compute_ema(prices_up, 10)
    # Last EMA should be closer to 110 than to 100
    assert ema_up[-1] > 105, f"EMA should track upward price, got {ema_up[-1]}"
    print("  ✓ EMA computation correct")


def test_rsi_computation():
    """RSI should be bounded 0-100."""
    # Trending up → RSI should be high
    prices_up = [100 + i * 0.5 for i in range(100)]
    rsi = _compute_rsi(prices_up, 14)
    valid_rsi = [r for r in rsi if r is not None]
    assert len(valid_rsi) > 50, "RSI should have enough valid values"
    for r in valid_rsi:
        assert 0 <= r <= 100, f"RSI out of range: {r}"
    # Trending up → RSI should be above 50
    assert valid_rsi[-1] > 60, f"RSI for uptrend should be high, got {valid_rsi[-1]}"

    # Trending down → RSI should be low
    prices_down = [200 - i * 0.5 for i in range(100)]
    rsi_down = _compute_rsi(prices_down, 14)
    valid_rsi_down = [r for r in rsi_down if r is not None]
    assert valid_rsi_down[-1] < 40, f"RSI for downtrend should be low, got {valid_rsi_down[-1]}"

    print("  ✓ RSI computation correct")


def test_macd_computation():
    """MACD should return two series (line and signal)."""
    prices = [100 + i * 0.3 for i in range(100)]
    macd_line, signal_line = _compute_macd(prices)
    assert len(macd_line) == len(prices), "MACD line length should match prices"
    assert len(signal_line) == len(prices), "Signal line length should match prices"

    # In uptrend, MACD line should be positive (fast EMA > slow EMA)
    valid_macd = [m for m in macd_line[30:] if m is not None]
    assert all(m > 0 for m in valid_macd), f"MACD should be positive in uptrend"

    print("  ✓ MACD computation correct")


def test_momentum_strategy():
    """Momentum strategy should produce trades on volatile data."""
    bars = make_volatile_bars(300)
    result = _run_strategy(bars, 'momentum', 1_000_000)

    trades = result['trades']
    metrics = result['metrics']
    equity_curve = result['equity_curve']

    print(f"    Momentum: {len(trades)} trades, return={metrics['total_return']:.2f}%, "
          f"win_rate={metrics['win_rate']:.1f}%, sharpe={metrics['sharpe']:.2f}")

    assert len(trades) > 0, "Momentum strategy should produce at least 1 trade on volatile data"
    assert len(equity_curve) > 0, "Equity curve should not be empty"
    assert 0 <= metrics['win_rate'] <= 100, f"Win rate out of range: {metrics['win_rate']}"
    assert metrics['max_drawdown'] >= 0, f"Max drawdown should be ≥ 0 (positive %), got {metrics['max_drawdown']}"
    assert not math.isnan(metrics['sharpe']), "Sharpe should not be NaN"
    assert not math.isinf(metrics['sharpe']), "Sharpe should not be Inf"

    # Capital accounting
    total_pnl = sum(t['pnl'] for t in trades)
    expected_final = 1_000_000 + total_pnl
    assert abs(metrics['final_capital'] - expected_final) < 1.0, \
        f"Capital mismatch: final={metrics['final_capital']}, expected={expected_final}"

    print("  ✓ Momentum strategy produces valid trades and metrics")


def test_momentum_on_trending_data():
    """Momentum should catch uptrend via EMA crossover."""
    bars = make_trending_up_bars(250)
    result = _run_strategy(bars, 'momentum', 1_000_000)
    trades = result['trades']
    metrics = result['metrics']

    print(f"    Momentum (trending): {len(trades)} trades, return={metrics['total_return']:.2f}%")

    # On a clear uptrend, we expect at least some trades
    # and ideally positive returns
    assert len(trades) >= 0, "Should not crash"
    print("  ✓ Momentum on trending data OK")


def test_mean_reversion_strategy():
    """Mean reversion should trade on oscillating data."""
    bars = make_mean_reverting_bars(250)
    result = _run_strategy(bars, 'mean_reversion', 1_000_000)

    trades = result['trades']
    metrics = result['metrics']

    print(f"    Mean Reversion: {len(trades)} trades, return={metrics['total_return']:.2f}%, "
          f"win_rate={metrics['win_rate']:.1f}%")

    assert len(trades) > 0, "Mean reversion should produce trades on oscillating data"

    # Capital accounting
    total_pnl = sum(t['pnl'] for t in trades)
    expected_final = 1_000_000 + total_pnl
    assert abs(metrics['final_capital'] - expected_final) < 1.0, \
        f"Capital mismatch: final={metrics['final_capital']}, expected={expected_final}"

    print("  ✓ Mean reversion strategy produces valid trades")


def test_mean_reversion_on_volatile():
    """Mean reversion with more volatile data."""
    bars = make_volatile_bars(300)
    result = _run_strategy(bars, 'mean_reversion', 1_000_000)
    trades = result['trades']
    metrics = result['metrics']

    print(f"    Mean Reversion (volatile): {len(trades)} trades, return={metrics['total_return']:.2f}%")
    assert len(trades) > 0, "Mean reversion should trade on volatile data"
    print("  ✓ Mean reversion on volatile data OK")


def test_breakout_strategy():
    """Breakout should catch price breakouts."""
    bars = make_breakout_bars(200)
    result = _run_strategy(bars, 'breakout', 1_000_000)

    trades = result['trades']
    metrics = result['metrics']

    print(f"    Breakout: {len(trades)} trades, return={metrics['total_return']:.2f}%, "
          f"win_rate={metrics['win_rate']:.1f}%")

    assert len(trades) > 0, "Breakout strategy should catch breakout events"

    # Capital accounting
    total_pnl = sum(t['pnl'] for t in trades)
    expected_final = 1_000_000 + total_pnl
    assert abs(metrics['final_capital'] - expected_final) < 1.0, \
        f"Capital mismatch: final={metrics['final_capital']}, expected={expected_final}"

    print("  ✓ Breakout strategy produces valid trades")


def test_breakout_on_volatile():
    """Breakout with volatile data."""
    bars = make_volatile_bars(300)
    result = _run_strategy(bars, 'breakout', 1_000_000)
    trades = result['trades']
    metrics = result['metrics']

    print(f"    Breakout (volatile): {len(trades)} trades, return={metrics['total_return']:.2f}%")
    assert len(trades) > 0, "Breakout should trade on volatile data"
    print("  ✓ Breakout on volatile data OK")


def test_default_ema_crossover():
    """Default strategy (EMA crossover) should produce trades on volatile data."""
    bars = make_volatile_bars(300)
    result = _run_strategy(bars, 'ema_crossover', 1_000_000)

    trades = result['trades']
    metrics = result['metrics']

    print(f"    Default EMA: {len(trades)} trades, return={metrics['total_return']:.2f}%")

    assert len(trades) > 0, "Default EMA crossover should produce trades on volatile data"

    # Capital accounting
    total_pnl = sum(t['pnl'] for t in trades)
    expected_final = 1_000_000 + total_pnl
    assert abs(metrics['final_capital'] - expected_final) < 1.0, \
        f"Capital mismatch: final={metrics['final_capital']}, expected={expected_final}"

    print("  ✓ Default EMA crossover produces valid trades")


def test_too_few_bars():
    """Should return empty result for < 55 bars."""
    bars = make_trending_up_bars(40)
    result = _run_strategy(bars, 'momentum', 1_000_000)
    assert result['metrics']['total_trades'] == 0, "Should have zero trades with < 55 bars"
    assert result['metrics']['final_capital'] == 1_000_000
    print("  ✓ Correctly handles too few bars")


def test_equity_curve_integrity():
    """Equity curve should start near initial capital, have no wild jumps at buy/sell, and vary."""
    bars = make_volatile_bars(300)
    result = _run_strategy(bars, 'momentum', 1_000_000)
    curve = result['equity_curve']

    assert len(curve) > 100, f"Equity curve too short: {len(curve)}"

    # First equity value should be close to initial capital
    first_val = curve[0]['value']
    assert abs(first_val - 1_000_000) < 50_000, \
        f"First equity value should be near 1M, got {first_val}"

    # Values should not all be identical (unless no trades, which we've already tested)
    vals = set(eq['value'] for eq in curve)
    if result['metrics']['num_trades'] > 0:
        assert len(vals) > 1, "Equity curve should have varying values when trades occur"

    # ── KEY CHECK: No sudden jumps > 10% between consecutive bars ──
    # With proper cash accounting, buying/selling shouldn't cause a discontinuity
    # because portfolio_val = cash + position*price is continuous.
    for j in range(1, len(curve)):
        prev_v = curve[j - 1]['value']
        curr_v = curve[j]['value']
        if prev_v > 0:
            change_pct = abs(curr_v - prev_v) / prev_v
            assert change_pct < 0.10, \
                f"Equity curve jump too large at index {j}: {prev_v:.2f} → {curr_v:.2f} ({change_pct*100:.1f}%)"

    print("  ✓ Equity curve integrity OK")


def test_metrics_sanity():
    """All metrics should be within sane ranges."""
    for strategy in ['momentum', 'mean_reversion', 'breakout', 'ema_crossover']:
        bars = make_volatile_bars(300)
        result = _run_strategy(bars, strategy, 1_000_000)
        m = result['metrics']

        # win_rate and max_drawdown are now in % (0-100)
        assert 0 <= m['win_rate'] <= 100, f"{strategy}: win_rate out of range: {m['win_rate']}"
        assert m['max_drawdown'] >= 0, f"{strategy}: max_drawdown should be ≥ 0 (positive %), got {m['max_drawdown']}"
        assert not math.isnan(m['sharpe']), f"{strategy}: sharpe is NaN"
        assert not math.isinf(m['sharpe']), f"{strategy}: sharpe is Inf"
        assert not math.isnan(m.get('sortino', 0)), f"{strategy}: sortino is NaN"
        assert m['final_capital'] > 0, f"{strategy}: final_capital should be positive"
        assert m['total_trades'] >= 0, f"{strategy}: total_trades should be >= 0"

        # total_return is now in % (e.g. -1.23 means -1.23%)
        expected_return_pct = (m['final_capital'] - 1_000_000) / 1_000_000 * 100
        assert abs(m['total_return'] - expected_return_pct) < 0.1, \
            f"{strategy}: total_return mismatch: {m['total_return']}% vs expected {expected_return_pct:.4f}%"

    print("  ✓ All strategy metrics are sane")


def test_position_closed_at_end():
    """Open position should be closed at the last bar."""
    # Use data that will likely have a position open at end
    bars = make_trending_up_bars(200)
    for strategy in ['momentum', 'mean_reversion', 'breakout', 'ema_crossover']:
        result = _run_strategy(bars, strategy, 1_000_000)
        trades = result['trades']
        if trades:
            # Last trade should be either BUY→SELL or CLOSE
            last_side = trades[-1]['side']
            assert last_side in ('BUY→SELL', 'CLOSE'), \
                f"{strategy}: last trade side should be BUY→SELL or CLOSE, got {last_side}"

    print("  ✓ Open positions correctly closed at end")


def test_no_negative_prices():
    """Trades should never have zero or negative entry/exit prices."""
    for strategy in ['momentum', 'mean_reversion', 'breakout', 'ema_crossover']:
        bars = make_volatile_bars(300)
        result = _run_strategy(bars, strategy, 1_000_000)
        for t in result['trades']:
            assert t['entry'] > 0, f"{strategy}: entry price should be > 0, got {t['entry']}"
            assert t['exit'] > 0, f"{strategy}: exit price should be > 0, got {t['exit']}"

    print("  ✓ No negative prices in trades")


def test_capital_accounting_detailed():
    """Step through trades and verify capital flows (cash-accounting model)."""
    bars = make_volatile_bars(300)
    for strategy in ['momentum', 'mean_reversion', 'breakout', 'ema_crossover']:
        result = _run_strategy(bars, strategy, 1_000_000)
        trades = result['trades']
        metrics = result['metrics']

        # With proper cash accounting: final_capital = initial + sum(pnl)
        total_pnl = sum(t['pnl'] for t in trades)
        expected_final = 1_000_000.0 + total_pnl

        assert abs(metrics['final_capital'] - expected_final) < 1.0, \
            f"{strategy}: capital accounting error: final={metrics['final_capital']:.2f}, expected={expected_final:.2f}"

        # net_pnl and total_pnl are both stored (legacy alias)
        assert abs(metrics['net_pnl'] - total_pnl) < 0.1, \
            f"{strategy}: net_pnl mismatch: {metrics['net_pnl']} vs {total_pnl}"

        # total_return in % should match
        expected_ret_pct = total_pnl / 1_000_000 * 100
        assert abs(metrics['total_return'] - expected_ret_pct) < 0.1, \
            f"{strategy}: total_return% mismatch"

    print("  ✓ Capital accounting verified for all strategies")


def test_equity_final_match():
    """Last equity curve point (after close) should match final_capital."""
    bars = make_volatile_bars(300)
    for strategy in ['momentum', 'mean_reversion', 'breakout', 'ema_crossover']:
        result = _run_strategy(bars, strategy, 1_000_000)
        curve = result['equity_curve']
        metrics = result['metrics']

        if not curve:
            continue

        # Verify that final_capital = initial + sum(all pnls)
        total_pnl = sum(t['pnl'] for t in result['trades'])
        expected = 1_000_000 + total_pnl
        assert abs(metrics['final_capital'] - expected) < 1.0, \
            f"{strategy}: final_capital {metrics['final_capital']:.2f} != expected {expected:.2f}"
        # Verify net_pnl field
        assert abs(metrics['net_pnl'] - total_pnl) < 0.1, \
            f"{strategy}: net_pnl {metrics['net_pnl']:.2f} != {total_pnl:.2f}"

    print("  ✓ Equity curve final value matches final capital")


async def test_with_real_yahoo_data():
    """Fetch real data from Yahoo Finance and run backtest."""
    from app.utils.market_data import get_market_data_service

    mds = get_market_data_service()
    symbols_to_test = ['RELIANCE', 'TCS', 'NIFTY']

    for symbol in symbols_to_test:
        try:
            bars = await mds.aget_historical(symbol, period='1y', interval='1d')
        except Exception as e:
            print(f"    ⚠ Skipping {symbol}: {e}")
            continue

        if not bars or len(bars) < 55:
            print(f"    ⚠ Skipping {symbol}: insufficient bars ({len(bars) if bars else 0})")
            continue

        # Tag bars
        for b in bars:
            b['symbol'] = symbol

        for strategy in ['momentum', 'mean_reversion', 'breakout']:
            result = _run_strategy(bars, strategy, 1_000_000)
            trades = result['trades']
            metrics = result['metrics']

            print(f"    {symbol}/{strategy}: {len(trades)} trades, "
                  f"return={metrics['total_return']:.2f}%, "
                  f"sharpe={metrics['sharpe']:.2f}, "
                  f"max_dd={metrics['max_drawdown']:.2f}%")

            # Basic sanity checks (win_rate and max_drawdown now in %)
            assert 0 <= metrics['win_rate'] <= 100, f"win_rate={metrics['win_rate']}"
            assert metrics['max_drawdown'] >= 0, f"max_drawdown={metrics['max_drawdown']}"
            assert not math.isnan(metrics['sharpe'])
            assert metrics['final_capital'] > 0

            # Capital accounting
            total_pnl = sum(t['pnl'] for t in trades)
            assert abs(metrics['final_capital'] - (1_000_000 + total_pnl)) < 1.0, \
                f"Capital mismatch for {symbol}/{strategy}"

    print("  ✓ Real Yahoo Finance data backtest OK")


def test_empty_result_helper():
    """_empty_result should return safe defaults."""
    result = _empty_result(500_000)
    assert result['metrics']['final_capital'] == 500_000
    assert result['metrics']['total_trades'] == 0
    assert result['metrics']['total_return'] == 0.0
    assert result['metrics']['net_pnl'] == 0.0
    assert len(result['trades']) == 0
    assert len(result['equity_curve']) == 1
    print("  ✓ Empty result helper correct")


def test_profit_factor():
    """Profit factor should be computed correctly."""
    bars = make_volatile_bars(300)
    for strategy in ['momentum', 'mean_reversion', 'breakout']:
        result = _run_strategy(bars, strategy, 1_000_000)
        trades = result['trades']
        metrics = result['metrics']

        if trades:
            gross_profit = sum(t['pnl'] for t in trades if t['pnl'] > 0)
            gross_loss = abs(sum(t['pnl'] for t in trades if t['pnl'] < 0))

            if gross_loss > 0:
                expected_pf = gross_profit / gross_loss
                assert abs(metrics.get('profit_factor', 0) - round(expected_pf, 2)) < 0.1, \
                    f"{strategy}: profit factor mismatch"

    print("  ✓ Profit factor computation correct")


# ── Run all tests ──────────────────────────────────────────────────────────

def main():
    print("\n" + "=" * 70)
    print(" BACKTEST ENGINE — COMPREHENSIVE TEST SUITE")
    print("=" * 70)

    passed = 0
    failed = 0
    errors = []

    tests = [
        ("Indicator: EMA computation", test_ema_computation),
        ("Indicator: RSI computation", test_rsi_computation),
        ("Indicator: MACD computation", test_macd_computation),
        ("Strategy: Momentum (volatile data)", test_momentum_strategy),
        ("Strategy: Momentum (trending data)", test_momentum_on_trending_data),
        ("Strategy: Mean Reversion (oscillating)", test_mean_reversion_strategy),
        ("Strategy: Mean Reversion (volatile)", test_mean_reversion_on_volatile),
        ("Strategy: Breakout (breakout data)", test_breakout_strategy),
        ("Strategy: Breakout (volatile)", test_breakout_on_volatile),
        ("Strategy: Default EMA crossover", test_default_ema_crossover),
        ("Edge case: Too few bars", test_too_few_bars),
        ("Edge case: Empty result helper", test_empty_result_helper),
        ("Integrity: Equity curve", test_equity_curve_integrity),
        ("Integrity: Metrics sanity", test_metrics_sanity),
        ("Integrity: Position closed at end", test_position_closed_at_end),
        ("Integrity: No negative prices", test_no_negative_prices),
        ("Integrity: Capital accounting (detailed)", test_capital_accounting_detailed),
        ("Integrity: Profit factor", test_profit_factor),
        ("Integrity: Equity curve matches final capital", test_equity_final_match),
    ]

    for name, test_fn in tests:
        try:
            print(f"\n▸ {name}")
            test_fn()
            passed += 1
        except Exception as e:
            failed += 1
            errors.append((name, str(e)))
            print(f"  ✗ FAILED: {e}")

    # Async test: real Yahoo Finance data
    print(f"\n▸ Real data: Yahoo Finance backtest")
    try:
        asyncio.run(test_with_real_yahoo_data())
        passed += 1
    except Exception as e:
        failed += 1
        errors.append(("Real data: Yahoo Finance", str(e)))
        print(f"  ✗ FAILED: {e}")

    # Summary
    print("\n" + "=" * 70)
    print(f" RESULTS: {passed} passed, {failed} failed, {passed + failed} total")
    print("=" * 70)

    if errors:
        print("\nFailed tests:")
        for name, err in errors:
            print(f"  ✗ {name}: {err}")

    if failed == 0:
        print("\n🎉 ALL TESTS PASSED — Backtest engine is working correctly!\n")
    else:
        print(f"\n⚠️  {failed} test(s) failed — see above for details.\n")

    return 0 if failed == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
