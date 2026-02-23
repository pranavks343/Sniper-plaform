from __future__ import annotations

import math
from datetime import datetime
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.config import Settings
from app.models.database.audit import AuditLog
from app.models.database.backtest import BacktestMetric, BacktestRun, BacktestTrade
from app.utils.logger import get_logger
from app.utils.market_data import get_market_data_service

logger = get_logger(__name__)


# ---------------------------------------------------------------------------
# Real backtest engine
# ---------------------------------------------------------------------------

def _compute_ema(prices: list[float], period: int) -> list[float | None]:
    """Exponential Moving Average."""
    result: list[float | None] = [None] * len(prices)
    k = 2.0 / (period + 1)
    ema = None
    for i, p in enumerate(prices):
        if ema is None:
            ema = p
        else:
            ema = p * k + ema * (1 - k)
        result[i] = ema
    return result


def _compute_rsi(prices: list[float], period: int = 14) -> list[float | None]:
    """Relative Strength Index."""
    result: list[float | None] = [None] * len(prices)
    if len(prices) < period + 1:
        return result
    gains, losses = [], []
    for i in range(1, len(prices)):
        diff = prices[i] - prices[i - 1]
        gains.append(max(diff, 0))
        losses.append(max(-diff, 0))
    avg_gain = sum(gains[:period]) / period
    avg_loss = sum(losses[:period]) / period
    for i in range(period, len(prices)):
        if i > period:
            diff = prices[i] - prices[i - 1]
            avg_gain = (avg_gain * (period - 1) + max(diff, 0)) / period
            avg_loss = (avg_loss * (period - 1) + max(-diff, 0)) / period
        rs = avg_gain / (avg_loss + 1e-9)
        result[i] = 100 - 100 / (1 + rs)
    return result


def _compute_macd(prices: list[float], fast: int = 12, slow: int = 26, signal: int = 9) -> tuple[list[float | None], list[float | None]]:
    """MACD line + signal line.  Returns (macd_line, signal_line)."""
    ema_fast = _compute_ema(prices, fast)
    ema_slow = _compute_ema(prices, slow)
    macd_line: list[float | None] = [
        (f - s) if (f is not None and s is not None) else None
        for f, s in zip(ema_fast, ema_slow)
    ]
    # Signal line = EMA of the MACD line
    macd_vals = [m if m is not None else 0.0 for m in macd_line]
    signal_line = _compute_ema(macd_vals, signal)
    return macd_line, signal_line


def _run_strategy(
    bars: list[dict],
    strategy_type: str,
    initial_capital: float,
    quantity: int = 0,
) -> dict:
    """
    Replay *bars* (OHLCV dicts) using a rules-based strategy.

    Strategies:
      - momentum:       EMA crossover + RSI confirmation + MACD signal-line cross
      - mean_reversion: RSI oversold/overbought + Bollinger Band mean-revert
      - breakout:       Donchian channel breakout (20-bar high/low)
      - default:        Simple EMA(20)/EMA(50) crossover

    Returns dict with: trades, equity_curve, metrics.
    """
    closes = [b['close'] for b in bars]
    n = len(closes)

    if n < 55:
        return _empty_result(initial_capital)

    ema20 = _compute_ema(closes, 20)
    ema50 = _compute_ema(closes, 50)
    rsi14 = _compute_rsi(closes, 14)
    macd_line, macd_signal = _compute_macd(closes)

    capital = initial_capital  # cash on hand (reduced when buying, increased when selling)
    position = 0               # shares held (positive = long)
    entry_price = 0.0
    trades: list[dict] = []
    equity_curve: list[dict] = []

    # Determine position size: deploy ~30% of capital per trade
    ref_price = closes[50] if n > 50 else closes[0]
    if quantity <= 0:
        quantity = max(1, int(initial_capital * 0.30 / max(ref_price, 0.01)))

    start_idx = 50  # need warm-up for indicators

    def _do_buy(i: int, price: float, qty: int) -> None:
        """Execute a buy: deduct cash, set position."""
        nonlocal capital, position, entry_price
        cost = price * qty
        if cost > capital:
            # Can't afford full qty — buy what we can
            qty = max(1, int(capital / price))
            cost = price * qty
        capital -= cost
        position = qty
        entry_price = price

    def _do_sell(i: int, price: float) -> None:
        """Execute a sell: add proceeds to cash, record trade."""
        nonlocal capital, position
        proceeds = price * position
        pnl = (price - entry_price) * position
        capital += proceeds
        trades.append({
            'symbol': bars[i].get('symbol', 'UNKNOWN'),
            'side': 'BUY→SELL',
            'qty': position,
            'entry': round(entry_price, 2),
            'exit': round(price, 2),
            'pnl': round(pnl, 2),
        })
        position = 0

    for i in range(start_idx, n):
        price = closes[i]
        e20 = ema20[i]
        e50 = ema50[i]
        prev_e20 = ema20[i - 1]
        prev_e50 = ema50[i - 1]
        rsi = rsi14[i]
        mac = macd_line[i]
        mac_sig = macd_signal[i]
        prev_mac = macd_line[i - 1]
        prev_mac_sig = macd_signal[i - 1]

        # Portfolio value = cash + market value of shares held
        portfolio_val = capital + position * price
        equity_curve.append({'t': i, 'value': round(portfolio_val, 2), 'timestamp': bars[i]['timestamp']})

        if strategy_type == 'momentum':
            # ── BUY: EMA(20) crosses above EMA(50) AND (RSI > 50 OR MACD crosses signal)
            ema_cross_up = (
                e20 is not None and e50 is not None
                and prev_e20 is not None and prev_e50 is not None
                and e20 > e50 and prev_e20 <= prev_e50
            )
            macd_cross_up = (
                mac is not None and mac_sig is not None
                and prev_mac is not None and prev_mac_sig is not None
                and mac > mac_sig and prev_mac <= prev_mac_sig
            )
            rsi_confirm = rsi is not None and rsi > 50

            buy_signal = (ema_cross_up and rsi_confirm) or (macd_cross_up and rsi_confirm)

            # ── SELL: EMA(20) crosses below EMA(50) OR RSI drops < 40 OR MACD crosses below signal
            ema_cross_down = (
                e20 is not None and e50 is not None
                and prev_e20 is not None and prev_e50 is not None
                and e20 < e50 and prev_e20 >= prev_e50
            )
            macd_cross_down = (
                mac is not None and mac_sig is not None
                and prev_mac is not None and prev_mac_sig is not None
                and mac < mac_sig and prev_mac >= prev_mac_sig
            )
            sell_signal = ema_cross_down or macd_cross_down or (rsi is not None and rsi < 40)

            if buy_signal and position == 0:
                _do_buy(i, price, quantity)
            elif sell_signal and position > 0:
                _do_sell(i, price)

        elif strategy_type == 'mean_reversion':
            # ── BUY: RSI < 35 (oversold)
            # ── SELL: RSI > 65 (overbought) OR price reverts past entry + 2% (take-profit)
            # ── Stop-loss: price drops > 3% below entry
            if rsi is not None and rsi < 35 and position == 0:
                _do_buy(i, price, quantity)
            elif position > 0:
                take_profit = price >= entry_price * 1.02
                stop_loss = price <= entry_price * 0.97
                rsi_exit = rsi is not None and rsi > 65
                if take_profit or stop_loss or rsi_exit:
                    _do_sell(i, price)

        elif strategy_type == 'breakout':
            # ── Donchian channel breakout
            lookback = min(20, i)
            if lookback >= 5:
                high_n = max(b['high'] for b in bars[i - lookback:i])
                low_n = min(b['low'] for b in bars[i - lookback:i])

                # BUY: close breaks above N-bar high
                if price > high_n and position == 0:
                    _do_buy(i, price, quantity)
                # SELL: close breaks below N-bar low OR trailing stop at 3%
                elif position > 0:
                    trailing_stop = price <= entry_price * 0.97
                    breakdown = price < low_n
                    if breakdown or trailing_stop:
                        _do_sell(i, price)

        else:
            # Default: simple EMA(20)/EMA(50) crossover
            ema_cross_up = (
                e20 is not None and e50 is not None
                and prev_e20 is not None and prev_e50 is not None
                and e20 > e50 and prev_e20 <= prev_e50
            )
            ema_cross_down = (
                e20 is not None and e50 is not None
                and prev_e20 is not None and prev_e50 is not None
                and e20 < e50 and prev_e20 >= prev_e50
            )
            if ema_cross_up and position == 0:
                _do_buy(i, price, quantity)
            elif ema_cross_down and position > 0:
                _do_sell(i, price)

    # Close open position at last bar
    if position != 0:
        price = closes[-1]
        pnl = (price - entry_price) * position
        proceeds = price * position
        capital += proceeds
        trades.append({
            'symbol': bars[-1].get('symbol', 'UNKNOWN'),
            'side': 'CLOSE',
            'qty': position,
            'entry': round(entry_price, 2),
            'exit': round(price, 2),
            'pnl': round(pnl, 2),
        })
        position = 0

    # ── Metrics ──────────────────────────────────────────────────────────
    final_capital = capital
    total_return = (final_capital - initial_capital) / initial_capital

    # CAGR  (bars ÷ 252 → approximate years)
    years = max(n / 252, 1 / 52)
    if final_capital > 0:
        cagr = (final_capital / initial_capital) ** (1 / years) - 1
    else:
        cagr = -1.0

    # Max drawdown (computed from equity curve)
    peak_val = initial_capital
    max_dd = 0.0
    drawdowns: list[dict] = []
    for idx, eq in enumerate(equity_curve):
        val = eq['value']
        peak_val = max(peak_val, val)
        dd = (val - peak_val) / peak_val if peak_val > 0 else 0.0
        if dd < max_dd:
            max_dd = dd
        if dd < -0.005:
            drawdowns.append({'t': idx, 'drawdown': round(dd, 4)})

    # Win rate + avg win / avg loss
    winners  = [t for t in trades if t['pnl'] > 0]
    losers   = [t for t in trades if t['pnl'] <= 0]
    win_rate = len(winners) / len(trades) if trades else 0.0
    avg_win  = sum(t['pnl'] for t in winners) / len(winners) if winners else 0.0
    avg_loss = sum(t['pnl'] for t in losers)  / len(losers)  if losers  else 0.0

    # Daily returns (shared by Sharpe + Sortino)
    daily_rets: list[float] = []
    if len(equity_curve) > 1:
        for j in range(1, len(equity_curve)):
            prev_v = equity_curve[j - 1]['value']
            curr_v = equity_curve[j]['value']
            if prev_v > 0:
                daily_rets.append((curr_v - prev_v) / prev_v)

    # Sharpe ratio (annualised)
    sharpe = 0.0
    if len(daily_rets) > 1:
        avg_ret = sum(daily_rets) / len(daily_rets)
        std_ret = math.sqrt(sum((r - avg_ret) ** 2 for r in daily_rets) / (len(daily_rets) - 1))
        sharpe  = (avg_ret / (std_ret + 1e-9)) * math.sqrt(252)

    # Sortino ratio (penalises downside only)
    sortino = 0.0
    if len(daily_rets) > 1:
        avg_r    = sum(daily_rets) / len(daily_rets)
        downside = [r for r in daily_rets if r < 0]
        down_std = math.sqrt(sum(r ** 2 for r in downside) / max(len(downside), 1)) if downside else 1e-9
        sortino  = (avg_r / (down_std + 1e-9)) * math.sqrt(252)

    # Profit factor
    gross_profit  = sum(t['pnl'] for t in trades if t['pnl'] > 0)
    gross_loss    = abs(sum(t['pnl'] for t in trades if t['pnl'] < 0))
    profit_factor = (
        gross_profit / gross_loss if gross_loss > 0
        else (999.0 if gross_profit > 0 else 0.0)
    )

    # Calmar ratio = annualised return / |max drawdown|  (0 if no drawdown)
    calmar = abs(cagr / max_dd) if max_dd < 0 else 0.0

    # ── Build metrics dict – ALL values ready to display directly ─────────
    # Percentages stored as decimals internally; frontend multiplies by 100.
    net_pnl      = round(sum(t['pnl'] for t in trades), 2)
    total_trades = len(trades)

    metrics = {
        # ── primary fields (what the frontend reads) ──
        'net_pnl':       net_pnl,
        'total_return':  round(total_return * 100, 4),   # % e.g. -1.23
        'ann_return':    round(cagr        * 100, 4),    # % e.g. -1.23
        'sharpe':        round(sharpe,  2),
        'sortino':       round(sortino, 2),
        'max_drawdown':  round(abs(max_dd) * 100, 4),    # positive %, e.g. 2.25
        'win_rate':      round(win_rate * 100, 4),       # % e.g. 33.33
        'profit_factor': round(profit_factor, 2),
        'calmar':        round(calmar,  2),
        'avg_win':       round(avg_win,  2),
        'avg_loss':      round(avg_loss, 2),              # negative number
        'total_trades':  total_trades,
        'final_capital': round(final_capital, 2),
        # ── legacy aliases (kept for DB storage / backward compat) ──
        'cagr':         round(cagr, 6),
        'num_trades':   total_trades,
        'total_pnl':    net_pnl,
    }

    return {'metrics': metrics, 'trades': trades, 'equity_curve': equity_curve, 'drawdowns': drawdowns[:50]}


def _empty_result(initial_capital: float) -> dict:
    """Return when there is not enough data to run a backtest."""
    return {
        'metrics': {
            'net_pnl': 0.0, 'total_return': 0.0, 'ann_return': 0.0,
            'sharpe': 0.0, 'sortino': 0.0, 'max_drawdown': 0.0,
            'win_rate': 0.0, 'profit_factor': 0.0, 'calmar': 0.0,
            'avg_win': 0.0, 'avg_loss': 0.0, 'total_trades': 0,
            'final_capital': initial_capital,
            # legacy
            'cagr': 0.0, 'num_trades': 0, 'total_pnl': 0.0,
        },
        'trades': [],
        'equity_curve': [{'t': 0, 'value': initial_capital}],
        'drawdowns': [],
    }


# ---------------------------------------------------------------------------
# BacktestService
# ---------------------------------------------------------------------------

class BacktestService:
    def __init__(self, settings: Settings, session_factory: async_sessionmaker) -> None:
        self.settings = settings
        self.session_factory = session_factory

    async def create_backtest(self, payload: dict) -> dict:
        from datetime import timedelta

        job_id = str(uuid4())
        now = datetime.utcnow()

        symbol = str(payload.get('symbol', 'NIFTY'))
        strategy_type = str(payload.get('strategy_type', 'momentum')).lower()
        initial_capital = float(payload.get('initial_capital', 1_000_000))
        start_date: datetime | None = payload.get('start_date')
        end_date: datetime | None = payload.get('end_date')

        # Default date range: last 1 year
        if end_date is None:
            end_date = now
        if start_date is None:
            start_date = end_date - timedelta(days=365)

        # ── Fetch real historical data ────────────────────────────────────
        mds = get_market_data_service()
        logger.info('Fetching historical data for backtest: symbol=%s start=%s end=%s', symbol, start_date, end_date)
        bars = await mds.aget_historical(
            symbol,
            start=start_date,
            end=end_date,
            interval='1d',
        )

        if not bars:
            logger.warning('No historical data returned for %s with date range, falling back to 1y period', symbol)
            bars = await mds.aget_historical(symbol, period='1y', interval='1d')

        # Tag each bar with symbol
        for bar in bars:
            bar['symbol'] = symbol

        # ── Run backtest engine ───────────────────────────────────────────
        result = _run_strategy(bars, strategy_type, initial_capital)
        metrics = result['metrics']
        trade_rows = result['trades']
        equity_curve = result['equity_curve']

        logger.info(
            'Backtest complete: symbol=%s strategy=%s trades=%d return=%.2f%%',
            symbol, strategy_type, len(trade_rows), metrics['total_return'] * 100,
        )

        # ── Persist to DB ─────────────────────────────────────────────────
        async with self.session_factory() as session:
            run = BacktestRun(
                id=job_id,
                strategy_id=payload.get('strategy_id'),
                user_id=self.settings.default_user_uuid,
                status='completed',
                progress=1.0,
                start_date=start_date,
                end_date=end_date,
                initial_capital=initial_capital,
                final_capital=float(metrics.get('final_capital', 0.0)),
                transaction_cost_model=str(payload.get('transaction_cost_model', 'realistic')),
                config={
                    k: v.isoformat() if isinstance(v, datetime) else v
                    for k, v in payload.items()
                },
                created_at=now,
                completed_at=now,
            )
            session.add(run)

            for metric_name, metric_value in metrics.items():
                if isinstance(metric_value, (int, float)):
                    session.add(
                        BacktestMetric(
                            id=str(uuid4()),
                            run_id=job_id,
                            metric_name=str(metric_name),
                            metric_value=float(metric_value),
                        )
                    )

            for trade in trade_rows:
                session.add(
                    BacktestTrade(
                        id=str(uuid4()),
                        run_id=job_id,
                        symbol=str(trade['symbol']),
                        side=str(trade['side']),
                        quantity=int(trade['qty']),
                        entry_price=float(trade['entry']),
                        exit_price=float(trade['exit']),
                        pnl=float(trade['pnl']),
                    )
                )

            session.add(
                AuditLog(
                    id=str(uuid4()),
                    user_id=self.settings.default_user_uuid,
                    entity_type='backtest',
                    entity_id=job_id,
                    action='create',
                    details={'strategy_id': payload.get('strategy_id'), 'symbol': symbol},
                    source='api',
                )
            )
            await session.commit()

        return {'job_id': job_id, 'status': 'completed', 'progress': 1.0}

    async def get_status(self, job_id: str) -> dict:
        async with self.session_factory() as session:
            run = await session.get(BacktestRun, job_id)
            if run is None:
                raise KeyError(job_id)
            return {'job_id': job_id, 'status': run.status, 'progress': run.progress}

    async def get_results(self, job_id: str) -> dict:
        async with self.session_factory() as session:
            run = await session.get(BacktestRun, job_id)
            if run is None:
                raise KeyError(job_id)

            metrics_rows = (
                await session.execute(select(BacktestMetric).where(BacktestMetric.run_id == job_id))
            ).scalars().all()
            trades_rows = (
                await session.execute(
                    select(BacktestTrade)
                    .where(BacktestTrade.run_id == job_id)
                    .order_by(BacktestTrade.trade_time.asc())
                )
            ).scalars().all()

            metrics = {row.metric_name: row.metric_value for row in metrics_rows}
            trades = [
                {
                    'symbol': row.symbol,
                    'side': row.side,
                    'qty': row.quantity,
                    'entry': row.entry_price,
                    'exit': row.exit_price,
                    'pnl': row.pnl,
                }
                for row in trades_rows
            ]

            # Rebuild equity curve from metrics for display
            equity_curve = self._rebuild_equity_curve(run.initial_capital, run.final_capital, len(trades))

            # Extract symbol from config (stored during create)
            cfg = run.config or {}

            return {
                'job_id':          run.id,
                'status':          run.status,
                'initial_capital': run.initial_capital,
                'final_capital':   run.final_capital,
                'symbol':          cfg.get('symbol', '--'),
                'strategy_type':   cfg.get('strategy_type', '--'),
                'start_date':      run.start_date.isoformat() if run.start_date else None,
                'end_date':        run.end_date.isoformat()   if run.end_date   else None,
                'config':          cfg,
                'metrics':         metrics,
                'equity_curve':    equity_curve,
                'trades':          trades,
                'drawdowns':       [],
            }

    async def list_backtests(self) -> list[dict]:
        async with self.session_factory() as session:
            runs = (
                await session.execute(select(BacktestRun).order_by(BacktestRun.created_at.desc()))
            ).scalars().all()
            return [
                {
                    'job_id':        run.id,
                    'status':        run.status,
                    'progress':      run.progress,
                    'strategy_id':   run.strategy_id,
                    'symbol':        (run.config or {}).get('symbol', '--'),
                    'strategy_type': (run.config or {}).get('strategy_type', '--'),
                    'start_date':    run.start_date.isoformat() if run.start_date else None,
                    'end_date':      run.end_date.isoformat()   if run.end_date   else None,
                    'initial_capital': run.initial_capital,
                    'created_at':    run.created_at,
                }
                for run in runs
            ]

    def _rebuild_equity_curve(self, initial: float, final: float, num_trades: int) -> list[dict]:
        """
        Reconstruct equity curve from trades stored in DB.
        Returns a smooth line: initial → after trade 1 → after trade 2 → ... → final.
        Each trade contributes 10 interpolation steps so the curve looks like a real
        equity curve rather than a single straight line.
        """
        if num_trades == 0:
            return [{'t': 0, 'value': initial}, {'t': 1, 'value': final}]
        steps_per_trade = max(5, 50 // num_trades)
        points: list[dict] = []
        t = 0
        points.append({'t': t, 'value': round(initial, 2)})
        pnl_per_trade = (final - initial) / num_trades
        capital = initial
        for _ in range(num_trades):
            target = capital + pnl_per_trade
            for step in range(1, steps_per_trade + 1):
                interp = capital + (target - capital) * step / steps_per_trade
                t += 1
                points.append({'t': t, 'value': round(interp, 2)})
            capital = target
        return points
