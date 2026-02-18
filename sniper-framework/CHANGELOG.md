# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2025-02-18

### Added
- **Position Sizer**: Kelly Criterion, Fixed Fractional, and Volatility-Adjusted sizing strategies
- **Meta Labeler**: XGBoost + logistic regression fallback for ML-based labeling
- **PPO Execution Agent**: Stable-Baselines3 with heuristic fallback for optimal execution
- **Greeks Calculator**: Full Black-Scholes implementation with Newton-Raphson IV solver
- **QAOA Order Router**: Qiskit-based quantum order routing with classical QUBO fallback
- **QAOA Hedger**: Quantum portfolio hedging with greedy fallback
- **Event Bus**: Asyncio pub/sub system for trading events
- **State Manager**: Thread-safe JSON snapshot persistence with crash recovery
- **WebSocket Manager**: Async WebSocket client with reconnect & heartbeat
- **Bar Aggregator**: OHLCV aggregation with VWAP calculation
- **Market Simulator**: GBM-based synthetic market data generator
- **Zerodha Broker**: Full Kite Connect API adapter
- **Dhan Broker**: Full DhanHQ API adapter
- **Backtest Engine**: Walk-forward backtesting with slippage & market impact
- **Performance Metrics**: Sharpe, Sortino, Calmar, win rate, expectancy, CAGR
- **Trading Loop**: Main async orchestration loop
- **Strategy Lifecycle**: State machine lifecycle management
- **Model Loader**: HMM/XGBoost/PPO model initialization
- **Utilities**: Structured logging, config management, retry decorator, TTL cache

### Changed
- Increased exports from 17 to 56 core symbols
- Enhanced documentation with comprehensive examples
- Improved error handling with heuristic fallbacks

### Fixed
- JSON parse robustness in data feeds
- Async/await patterns in all event handlers
- Memory leaks in long-running strategies

## [1.0.0] - 2025-02-15

### Added
- Initial release
- **Risk Engine**: CircuitBreaker, LimitMonitor
- **Execution Engine**: SmartOrderRouter, CostEstimator
- **Strategy Engine**: SignalGenerator, HMMRegimeDetector
- **Brokers**: BaseBroker interface, PaperTradingBroker
- MIT License
- Initial documentation

---

## Versioning

- **Major (X.0.0)**: Breaking API changes
- **Minor (0.X.0)**: New features (backward compatible)
- **Patch (0.0.X)**: Bug fixes (backward compatible)

## Roadmap

### Upcoming (1.2.0)
- [ ] Reinforcement learning strategy optimization
- [ ] Portfolio rebalancing automation
- [ ] Advanced regime detection (LSTM)
- [ ] Real-time backtest performance streaming

### Planned (2.0.0)
- [ ] Distributed backtesting
- [ ] GPU acceleration
- [ ] WebAssembly bindings
- [ ] REST API server

---

## How to Report Issues

Found a bug? Please open an issue on [GitHub](https://github.com/pranavks343/sniper-framework/issues) with:
- Python version
- Error message & traceback
- Minimal reproduction code

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.
