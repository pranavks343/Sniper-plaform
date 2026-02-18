# Sniper Framework

**Open-source backend logic for algorithmic trading.** Risk engine, execution engine, strategy engine, and broker abstractions. Use with FastAPI, Celery, or any Python service.

Anyone can use, modify, and distribute this framework under the [MIT License](LICENSE).

---

## Install

```bash
pip install sniper-framework
```

Optional: regime detection with HMM (e.g. trending / mean-reverting / volatile):

```bash
pip install sniper-framework[hmm]
```

---

## What’s included (backend only)

| Layer | Components |
|-------|------------|
| **Risk engine** | `CircuitBreaker` — halt/resume on loss/drawdown/VIX; `LimitMonitor` — pre-trade and portfolio limits (delta, gamma, margin) |
| **Execution engine** | `SmartOrderRouter` — routing decisions (timing, order type, splits); `CostEstimator` — brokerage, STT, slippage, market impact (India-oriented) |
| **Strategy engine** | `SignalGenerator` — EMA, RSI, MACD-based signals; `HMMRegimeDetector` — regime from price features (optional `hmmlearn`) |
| **Brokers** | `BaseBroker` interface; `PaperTradingBroker` for backtesting and dev |

All logic is framework-only: no UI, no HTTP server. You wire it into your own API or jobs.

---

## Usage

```python
from sniper import (
    CircuitBreaker,
    LimitMonitor,
    SmartOrderRouter,
    CostEstimator,
    SignalGenerator,
    HMMRegimeDetector,
    PaperTradingBroker,
    Regime,
)

# Risk: circuit breaker + limit monitor
breaker = CircuitBreaker(admin_secret="your-secret")
if breaker.check_triggers(market_state, portfolio_state):
    breaker.activate_breaker("daily_loss_exceeded")

monitor = LimitMonitor(limits={"max_daily_loss_pct": 0.02, "max_delta": 1000.0})
status = monitor.check_all_limits(portfolio_state)
if not status.trading_allowed:
    # halt new orders
    pass

# Execution: route order and estimate cost
router = SmartOrderRouter()
decision = router.route(order, market_state)  # timing, order_type, splits, expected_cost

cost_estimator = CostEstimator()
cost = cost_estimator.estimate_total_cost(
    symbol="NIFTY", quantity=100, order_type="MARKET",
    urgency=0.5, market_state=market_state, side="BUY"
)

# Strategy: regime + signals
detector = HMMRegimeDetector(lookback=100)
detector.train(historical_prices)
regime_state = detector.predict_regime(recent_prices)

generator = SignalGenerator()
signals = generator.generate_signals(ohlcv_bars, regime_state.regime)

# Broker: paper trading for backtests
broker = PaperTradingBroker(starting_capital=1_000_000)
broker.connect({})
broker.place_order("NIFTY", 10, "MARKET", price=22450.0, side="BUY")
```

---

## Repository

- **Code:** [github.com/pranavks343/Sniper-framework](https://github.com/pranavks343/Sniper-framework)
- **License:** [MIT](LICENSE) — use commercially and privately.

---

## Contributing

Open an issue or submit a pull request. Contributions are licensed under the same MIT License.
