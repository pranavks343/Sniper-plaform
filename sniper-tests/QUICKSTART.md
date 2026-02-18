# Quick Start Guide - Sniper Test Suite

Get up and running with the test suite in 5 minutes.

## 🚀 Installation

```bash
cd /Users/pranavks/project/sniper-tests
pip install -r requirements.txt
```

## ⚡ Run Tests

### Option 1: Using the test runner script (Recommended)

```bash
# Run all tests
./run_tests.sh all

# Run with coverage
./run_tests.sh all coverage

# Run specific test category
./run_tests.sh unit
./run_tests.sh integration
./run_tests.sh performance
./run_tests.sh system

# Quick test (unit + integration only)
./run_tests.sh quick

# Re-run failed tests only
./run_tests.sh failed
```

### Option 2: Using pytest directly

```bash
# Run all tests
pytest -v

# Run specific test file
pytest unit/test_strategy_engine.py -v

# Run specific test
pytest unit/test_strategy_engine.py::TestHMMRegimeDetection::test_hmm_regime_detection_accuracy -v

# Run with coverage
pytest --cov=app --cov-report=html --cov-report=term

# Run with HTML report
pytest --html=report.html --self-contained-html
```

## 📊 View Results

### Coverage Report
```bash
# Generate coverage report
pytest --cov=app --cov-report=html

# Open in browser
open htmlcov/index.html
```

### Test Report
```bash
# Generate HTML test report
pytest --html=report.html --self-contained-html

# Open in browser
open report.html
```

## 🎯 Common Test Scenarios

### Test a specific component
```bash
# Test strategy engine
pytest unit/test_strategy_engine.py -v

# Test execution engine
pytest unit/test_execution_engine.py -v

# Test risk engine
pytest unit/test_risk_engine.py -v

# Test quantum components
pytest unit/test_quantum.py -v
```

### Test end-to-end flows
```bash
# Test signal to order flow
pytest integration/test_signal_to_order_flow.py -v

# Test position management
pytest integration/test_position_management_flow.py -v

# Test risk breach handling
pytest integration/test_risk_breach_flow.py -v
```

### Test performance
```bash
# Test latency
pytest performance/test_latency.py -v -s

# Test throughput
pytest performance/test_throughput.py -v -s

# Test quantum performance
pytest performance/test_quantum_performance.py -v -s
```

### Test system functionality
```bash
# Test backtest validation
pytest system/test_backtest_validation.py -v -s

# Test circuit breaker
pytest system/test_circuit_breaker.py -v -s
```

## 🐛 Debugging

### Run with verbose output
```bash
pytest -vv
```

### Run with print statements visible
```bash
pytest -s
```

### Run with debugger
```bash
pytest --pdb
```

### Run only failed tests
```bash
pytest --lf
```

### Run tests matching a pattern
```bash
pytest -k "regime" -v
pytest -k "greeks" -v
pytest -k "quantum" -v
```

## 📈 Expected Results

When all tests pass, you should see:

```
✅ Unit Tests: 100+ tests passed
✅ Integration Tests: 10+ tests passed
✅ Performance Tests: 15+ tests passed
✅ System Tests: 5+ tests passed

Key Metrics:
- End-to-end latency: <500ms (p99)
- Greeks calculation: <20ms
- WebSocket latency: <100ms
- Tick throughput: 10,000/sec
- Backtest win rate: 70-85%
- Max drawdown: <10%
- Sharpe ratio: >1.5
- Code coverage: >80%
```

## 🔧 Troubleshooting

### Import Errors
If you see import errors, make sure the backend path is correct:
```bash
export PYTHONPATH="${PYTHONPATH}:/Users/pranavks/project/sniper-platform/apps/sniper-backend"
```

### Missing Dependencies
```bash
pip install -r requirements.txt
```

### Tests Running Slowly
Use the quick test suite:
```bash
./run_tests.sh quick
```

Or run specific tests:
```bash
pytest unit/test_strategy_engine.py::TestHMMRegimeDetection -v
```

## 📚 Next Steps

1. **Review test results** - Check which tests passed/failed
2. **Check coverage** - Aim for >80% code coverage
3. **Run performance tests** - Verify latency and throughput targets
4. **Run backtest validation** - Ensure strategy meets success criteria
5. **Fix any failures** - Debug and fix failing tests
6. **Add new tests** - Write tests for new features

## 💡 Tips

- Run quick tests frequently during development
- Run full test suite before committing
- Use coverage reports to find untested code
- Use performance tests to catch regressions
- Use system tests to validate end-to-end functionality

## 🤝 Getting Help

- Check the main README.md for detailed documentation
- Review test files for examples
- Check conftest.py for available fixtures
- Check mocks/data_generators.py for mock data utilities

## 📞 Support

For issues or questions:
1. Check test output for error messages
2. Review test logs
3. Check coverage reports for missing tests
4. Contact the development team
