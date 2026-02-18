# Sniper Framework — Open Source Python Trading Package

**Status**: ✅ Separated into standalone GitHub repo, ready for public use

---

## 📦 What is Sniper Framework?

A **production-ready Python package** for algorithmic trading with:
- **Risk Engine**: Circuit breakers, Greeks calculation, limit monitoring
- **Execution Engine**: RL-based order routing (PPO), quantum hedging (QAOA)
- **Strategy Engine**: ML-based labeling (XGBoost), position sizing, regime detection
- **Data Pipeline**: WebSocket manager, bar aggregator, market simulator
- **Broker Adapters**: Zerodha, DhanHQ, paper trading
- **Backtesting**: Walk-forward engine, performance metrics
- **Orchestration**: Trading loop, lifecycle management, model loader
- **Utilities**: Logging, config, retry decorator, TTL cache

**56+ production-ready components** for building trading systems.

---

## 🎯 Separate Repository

The framework is now a **standalone GitHub repo** at:
```
https://github.com/pranavks343/sniper-framework
```

**Not bundled with sniper-platform anymore.**

---

## 📥 Installation

### For Users
```bash
pip install sniper-framework
```

With optional HMM regime detection:
```bash
pip install sniper-framework[hmm]
```

### For Developers
```bash
git clone https://github.com/pranavks343/sniper-framework.git
cd sniper-framework
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev,hmm]"
```

---

## 🚀 Quick Usage

### Risk Management
```python
from sniper import CircuitBreaker, GreeksCalculator

breaker = CircuitBreaker(max_daily_loss_pct=0.02)
if breaker.check_triggers(market_state, portfolio_state):
    # halt trading
    pass

calc = GreeksCalculator()
greeks = calc.calculate_greeks(
    option_type="CALL", spot=100, strike=105, 
    expiry_days=30, rate=0.05, volatility=0.25
)
```

### ML-Based Execution
```python
from sniper import MetaLabeler, PPOExecutionAgent

labeler = MetaLabeler(model_type="xgboost")
label = labeler.generate_label(features=...)

executor = PPOExecutionAgent()
action = executor.decide(market_state, order, portfolio_state)
```

### Backtesting
```python
from sniper import BacktestEngine, PerformanceCalculator

engine = BacktestEngine(starting_capital=1_000_000)
results = await engine.run(strategy=my_strategy, data=ohlcv_data)

metrics = PerformanceCalculator.calculate(results)
print(f"Sharpe: {metrics.sharpe_ratio}, Win Rate: {metrics.win_rate}")
```

---

## 📚 Documentation Files

In the sniper-framework repo:

| File | Purpose |
|------|---------|
| `README.md` | Quick overview & features |
| `README_PYPI.md` | Full PyPI-formatted README |
| `INSTALLATION.md` | Installation guide for all platforms |
| `CONTRIBUTING.md` | Contribution guidelines |
| `CHANGELOG.md` | Version history & roadmap |
| `PUBLISH.md` | PyPI publishing guide (for maintainers) |

---

## 🔗 Integration with Sniper Platform

The main **sniper-platform** (frontend + backend) now uses sniper-framework as:

**Method 1: From PyPI (Recommended)**
```bash
pip install sniper-framework
```

**Method 2: From source (Development)**
```toml
# In sniper-platform/apps/sniper-backend/pyproject.toml
dependencies = [
    "sniper-framework @ git+https://github.com/pranavks343/sniper-framework.git@main",
]
```

**Method 3: Local file (Development)**
```toml
dependencies = [
    "sniper-framework @ file:///path/to/sniper-framework",
]
```

---

## 🌍 Open Source Benefits

✅ **Community-Driven**
- Anyone can contribute
- Issues & PRs welcome
- MIT License — use commercially

✅ **Transparency**
- Full source code public
- Battle-tested implementations
- Real trading support

✅ **Reusability**
- Not tied to sniper-platform
- Use in your own projects
- Any Python environment

✅ **Distribution**
- Available on PyPI
- Install with `pip`
- Version management automatic

---

## 📊 Repository Structure

```
sniper-framework/
├── sniper/
│   ├── __init__.py           # 56+ exports
│   ├── core/                 # Risk, Execution, Strategy, Quantum engines
│   ├── brokers/              # Zerodha, DhanHQ, Paper trading
│   ├── backtest/             # Backtesting engine & metrics
│   ├── data/                 # WebSocket, bar aggregator, market sim
│   ├── events/               # Event bus (pub/sub)
│   ├── state/                # State manager & crash recovery
│   ├── orchestration/        # Trading loop, lifecycle, model loader
│   ├── utils/                # Logging, config, retry, cache
│   └── schemas/              # Common data models
├── README.md                 # Main readme
├── README_PYPI.md            # PyPI-formatted readme
├── INSTALLATION.md           # Setup guide
├── CONTRIBUTING.md           # Contribution guidelines
├── CHANGELOG.md              # Version history
├── PUBLISH.md                # Publishing guide
├── pyproject.toml            # Package metadata
├── LICENSE                   # MIT License
└── .github/
    └── workflows/            # CI/CD (optional)
```

---

## 🎯 What's Different from Sniper Platform?

### Sniper Framework
- **Pure Python package** (no UI, no HTTP server)
- **Library/components only**
- **Framework-agnostic** (use with FastAPI, Flask, Celery, async, etc.)
- **Open source on PyPI**
- **Reusable in any project**

### Sniper Platform
- **Full trading application** (frontend + backend)
- **FastAPI backend** + **Next.js frontend**
- **Complete system ready to deploy**
- **Uses sniper-framework internally**
- **College demo/production ready**

---

## 📈 Who Should Use This?

✅ **Quant traders** — Build custom trading systems
✅ **Fintech companies** — Add risk & execution components
✅ **Research teams** — Backtest strategies, test models
✅ **Developers** — Integrate trading logic into apps
✅ **Students** — Learn algorithmic trading architecture

---

## 🚀 Next Steps

### To Use in Your Project:
```bash
pip install sniper-framework
```

### To Contribute:
1. Fork: https://github.com/pranavks343/sniper-framework
2. Create feature branch: `git checkout -b feature/your-feature`
3. Submit PR

### To Deploy with Sniper Platform:
```bash
pip install sniper-framework  # Backend will use this
```

---

## 📞 Support

- **GitHub Issues**: https://github.com/pranavks343/sniper-framework/issues
- **GitHub Discussions**: https://github.com/pranavks343/sniper-framework/discussions
- **Documentation**: See INSTALLATION.md, CONTRIBUTING.md in repo

---

## 📝 License

**MIT License** — Use commercially, modify freely, distribute as needed.

---

## 🎓 Learning Path

1. **Quick Start** → Read README_PYPI.md
2. **Installation** → Follow INSTALLATION.md
3. **Examples** → Check examples/ directory
4. **Deep Dive** → Read source code + docstrings
5. **Contribute** → See CONTRIBUTING.md

---

**Status**: ✅ Open sourced, PyPI-ready, production tested

Built for the trading community. 🚀
