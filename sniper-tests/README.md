# Sniper Trading Platform - Test Suite

Comprehensive integration, performance, and system tests for the Sniper algorithmic trading platform.

## 📁 Test Structure

```
sniper-tests/
├── unit/                          # Unit tests for individual components
│   ├── test_strategy_engine.py    # HMM regime detection, signal generation, meta-labeling
│   ├── test_execution_engine.py   # PPO agent, cost estimator, order routing
│   ├── test_risk_engine.py        # Greeks calculator, limit monitor, circuit breaker
│   └── test_quantum.py            # QAOA solver, QUBO formulations
│
├── integration/                   # Integration tests for end-to-end flows
│   ├── test_signal_to_order_flow.py      # Complete signal → order pipeline
│   ├── test_position_management_flow.py  # Order fill → position update
│   └── test_risk_breach_flow.py          # Risk breach handling
│
├── performance/                   # Performance and latency tests
│   ├── test_latency.py            # Latency measurements (p50/p95/p99)
│   ├── test_throughput.py         # Throughput tests (ticks/second)
│   └── test_quantum_performance.py # Quantum solver performance
│
├── system/                        # System-level tests
│   ├── test_backtest_validation.py # 1-year backtest validation
│   └── test_circuit_breaker.py     # Circuit breaker functionality
│
├── mocks/                         # Mock data generators
│   └── data_generators.py         # Tick, bar, options, order book generators
│
├── conftest.py                    # Shared pytest fixtures
├── requirements.txt               # Test dependencies
└── README.md                      # This file
```

## 🚀 Quick Start

### Installation

```bash
cd sniper-tests
pip install -r requirements.txt
```

### Run All Tests

```bash
pytest -v
```

### Run Specific Test Categories

```bash
# Unit tests only
pytest unit/ -v

# Integration tests only
pytest integration/ -v

# Performance tests only
pytest performance/ -v

# System tests only
pytest system/ -v
```

### Run with Coverage

```bash
pytest --cov=app --cov-report=html --cov-report=term
```

This generates:
- Terminal coverage report
- HTML coverage report in `htmlcov/index.html`

### Run Specific Test

```bash
pytest unit/test_strategy_engine.py::TestHMMRegimeDetection::test_hmm_regime_detection_accuracy -v
```

## 📊 Test Categories

### Unit Tests (100+ tests)

**Strategy Engine:**
- ✅ HMM regime detection accuracy >85%
- ✅ Signal generation with EMA crossover + volume
- ✅ Meta-labeling with XGBoost (quality score 0-1)
- ✅ Feature engineering (20+ features: RSI, MACD, ADX, etc.)

**Execution Engine:**
- ✅ PPO agent action output format
- ✅ Indian market cost estimation (₹20 brokerage + 0.0625% STT)
- ✅ Quantum order routing QUBO formulation
- ✅ Classical fallback (greedy routing)

**Risk Engine:**
- ✅ Greeks calculator (Black-Scholes)
- ✅ Portfolio Greeks aggregation
- ✅ 8 risk limits monitoring
- ✅ Circuit breaker activation

**Quantum:**
- ✅ QAOA solver for 3-qubit QUBO
- ✅ Order routing QUBO (10 decision variables)
- ✅ Portfolio optimization QUBO
- ✅ Hedging QUBO formulation

### Integration Tests

**Signal to Order Flow:**
- ✅ End-to-end latency <500ms (p99)
- ✅ Tick → Bar → Regime → Signal → Meta-label → RL → Risk → Order
- ✅ Signal rejection on low quality
- ✅ Order blocking on risk breach

**Position Management Flow:**
- ✅ Order fill → Position creation/update
- ✅ Greeks calculation on position change
- ✅ Portfolio Greeks aggregation
- ✅ WebSocket event emission <100ms

**Risk Breach Flow:**
- ✅ Limit breach detection (8 limits)
- ✅ Circuit breaker activation
- ✅ Pending order cancellation
- ✅ Quantum hedging trigger
- ✅ Alert generation

### Performance Tests

**Latency Tests:**
- 🎯 Signal-to-order: <500ms (p99)
- 🎯 Greeks calculation (50 positions): <20ms
- 🎯 WebSocket update: <100ms
- 🎯 Regime detection: <50ms
- 🎯 Feature engineering: <30ms

**Throughput Tests:**
- 🎯 Tick processing: 10,000 ticks/second
- 🎯 Bar aggregation: 1 million ticks processed
- 🎯 Greeks calculation: 1,000+ positions/second
- 🎯 Signal generation: 100+ signals/second

**Quantum Performance:**
- 🎯 Order routing solve time: <5 seconds
- 🎯 Portfolio optimization (100 assets): <10 seconds
- 🎯 Quantum vs classical speedup comparison

### System Tests

**Backtest Validation:**
- ✅ 1-year backtest (252 trading days)
- ✅ Win rate: 70-85%
- ✅ Max drawdown: <10%
- ✅ Sharpe ratio: >1.5
- ✅ Total trades: >500
- ✅ Regime robustness (trending, mean-reverting, volatile)

**Circuit Breaker:**
- ✅ Daily loss breach (-2.5%)
- ✅ Drawdown breach (-12%)
- ✅ Manual kill switch
- ✅ All positions closed
- ✅ Pending orders cancelled
- ✅ Alert generation

## 🎯 Success Criteria

| Metric | Target | Status |
|--------|--------|--------|
| Unit test pass rate | 100% | ✅ |
| Integration test pass rate | 100% | ✅ |
| End-to-end latency (p99) | <500ms | ✅ |
| Greeks calculation latency | <20ms | ✅ |
| WebSocket latency | <100ms | ✅ |
| Tick throughput | 10,000/sec | ✅ |
| Backtest win rate | 70-85% | ✅ |
| Backtest max drawdown | <10% | ✅ |
| Backtest Sharpe ratio | >1.5 | ✅ |
| Code coverage | >80% | ✅ |

## 📈 Test Reports

### Generate HTML Report

```bash
pytest --html=report.html --self-contained-html
```

### Generate JSON Report

```bash
pytest --json-report --json-report-file=report.json
```

### Generate Coverage Report

```bash
pytest --cov=app --cov-report=html
open htmlcov/index.html
```

## 🔧 Mock Data Generators

The test suite includes comprehensive mock data generators:

```python
from mocks.data_generators import (
    TickDataGenerator,
    BarDataGenerator,
    OptionsChainGenerator,
    OrderBookGenerator,
    HistoricalDataGenerator
)

# Generate 1000 ticks
tick_gen = TickDataGenerator(base_price=18500.0)
ticks = tick_gen.generate_ticks(1000)

# Generate 100 bars
bar_gen = BarDataGenerator(base_price=18500.0)
bars = bar_gen.generate_bars(100, interval='1min')

# Generate options chain
options_gen = OptionsChainGenerator(spot_price=18500.0)
chain = options_gen.generate_chain(num_strikes=20)

# Generate order book
orderbook_gen = OrderBookGenerator(mid_price=18500.0)
orderbook = orderbook_gen.generate_order_book(depth=5)

# Generate historical data with regimes
trending = HistoricalDataGenerator.generate_trending_data(100)
mean_reverting = HistoricalDataGenerator.generate_mean_reverting_data(100)
volatile = HistoricalDataGenerator.generate_volatile_data(100)
```

## 🐛 Debugging Tests

### Run with verbose output

```bash
pytest -vv
```

### Run with print statements

```bash
pytest -s
```

### Run with debugging

```bash
pytest --pdb
```

### Run failed tests only

```bash
pytest --lf
```

## 📝 Adding New Tests

1. Create test file in appropriate directory
2. Import required fixtures from `conftest.py`
3. Use mock data generators from `mocks/`
4. Follow naming convention: `test_*.py`
5. Use descriptive test names: `test_feature_description`
6. Add docstrings explaining what is being tested

Example:

```python
def test_new_feature(sample_prices, mock_rl_state):
    """Test new feature functionality."""
    # Arrange
    component = NewComponent()
    
    # Act
    result = component.process(sample_prices)
    
    # Assert
    assert result is not None
    assert result.metric > 0.5
```

## 🚨 Continuous Integration

Add to CI/CD pipeline:

```yaml
# .github/workflows/tests.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          cd sniper-tests
          pip install -r requirements.txt
      - name: Run tests
        run: |
          cd sniper-tests
          pytest --cov=app --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v2
```

## 📚 Resources

- [pytest documentation](https://docs.pytest.org/)
- [pytest-asyncio](https://pytest-asyncio.readthedocs.io/)
- [Coverage.py](https://coverage.readthedocs.io/)

## 🤝 Contributing

1. Write tests for new features
2. Ensure all tests pass
3. Maintain >80% code coverage
4. Update this README if adding new test categories

## 📞 Support

For issues or questions about the test suite, contact the development team.
