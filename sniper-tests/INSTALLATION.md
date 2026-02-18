# Installation Guide - Sniper Test Suite

Complete installation and setup instructions for the test suite.

## 📋 Prerequisites

- Python 3.11 or higher
- pip (Python package manager)
- Git (for version control)
- 8GB+ RAM (for performance tests)
- macOS, Linux, or Windows

## 🚀 Quick Installation

### 1. Navigate to test directory
```bash
cd /Users/pranavks/project/sniper-tests
```

### 2. Create virtual environment (recommended)
```bash
python3 -m venv venv
source venv/bin/activate  # On macOS/Linux
# or
venv\Scripts\activate  # On Windows
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Verify installation
```bash
pytest --version
```

Expected output:
```
pytest 7.4.3
```

## 📦 Dependencies

The test suite requires the following packages:

### Testing Framework
- `pytest==7.4.3` - Testing framework
- `pytest-asyncio==0.21.1` - Async test support
- `pytest-cov==4.1.0` - Coverage reporting
- `pytest-mock==3.12.0` - Mocking utilities

### Core Dependencies
- `numpy==1.24.3` - Numerical computing
- `pandas==2.0.3` - Data manipulation
- `scipy==1.11.4` - Scientific computing

### Machine Learning
- `scikit-learn==1.3.2` - ML algorithms
- `xgboost==2.0.3` - Gradient boosting
- `hmmlearn==0.3.0` - Hidden Markov Models
- `joblib==1.3.2` - Model persistence

### Testing Utilities
- `faker==20.1.0` - Fake data generation
- `locust==2.20.0` - Performance testing
- `coverage==7.3.4` - Code coverage
- `pytest-html==4.1.1` - HTML reports
- `pytest-json-report==1.5.0` - JSON reports

## 🔧 Configuration

### 1. Python Path Setup

The test suite automatically adds the backend to the Python path. If you encounter import errors, manually set:

```bash
export PYTHONPATH="${PYTHONPATH}:/Users/pranavks/project/sniper-platform/apps/sniper-backend"
```

Add to your `.bashrc` or `.zshrc` for persistence:
```bash
echo 'export PYTHONPATH="${PYTHONPATH}:/Users/pranavks/project/sniper-platform/apps/sniper-backend"' >> ~/.zshrc
```

### 2. Pytest Configuration

The `pytest.ini` file is pre-configured with:
- Test discovery patterns
- Markers for test categorization
- Coverage settings
- Output formatting

No additional configuration needed.

### 3. Environment Variables (Optional)

For advanced configuration:

```bash
# Set test data directory
export TEST_DATA_DIR="/path/to/test/data"

# Set log level
export LOG_LEVEL="DEBUG"

# Set number of parallel workers
export PYTEST_WORKERS=4
```

## ✅ Verify Installation

### Run a simple test
```bash
pytest unit/test_strategy_engine.py::TestHMMRegimeDetection::test_hmm_regime_detection_accuracy -v
```

Expected output:
```
======================== test session starts =========================
unit/test_strategy_engine.py::TestHMMRegimeDetection::test_hmm_regime_detection_accuracy PASSED [100%]

========================= 1 passed in 0.5s ==========================
```

### Run all unit tests
```bash
pytest unit/ -v
```

### Run with coverage
```bash
pytest unit/ --cov=app --cov-report=term
```

## 🐛 Troubleshooting

### Issue: Import errors for `app` modules

**Solution 1**: Verify Python path
```bash
echo $PYTHONPATH
```

**Solution 2**: Set Python path manually
```bash
export PYTHONPATH="${PYTHONPATH}:/Users/pranavks/project/sniper-platform/apps/sniper-backend"
```

**Solution 3**: Use mock components
The test suite includes mock implementations in `mocks/mock_components.py` that will be used as fallback if real components are not found.

### Issue: Missing dependencies

**Solution**: Reinstall dependencies
```bash
pip install --upgrade -r requirements.txt
```

### Issue: Tests running slowly

**Solution 1**: Run specific tests
```bash
pytest unit/test_strategy_engine.py -v
```

**Solution 2**: Use parallel execution
```bash
pip install pytest-xdist
pytest -n auto
```

**Solution 3**: Skip slow tests
```bash
pytest -m "not slow"
```

### Issue: Permission denied on `run_tests.sh`

**Solution**: Make script executable
```bash
chmod +x run_tests.sh
```

### Issue: Coverage report not generating

**Solution**: Install coverage plugin
```bash
pip install pytest-cov coverage
```

### Issue: Out of memory during tests

**Solution**: Run tests in smaller batches
```bash
pytest unit/ -v
pytest integration/ -v
pytest performance/ -v
pytest system/ -v
```

## 🔄 Updating Dependencies

### Update all packages
```bash
pip install --upgrade -r requirements.txt
```

### Update specific package
```bash
pip install --upgrade pytest
```

### Freeze current versions
```bash
pip freeze > requirements.txt
```

## 🧹 Cleanup

### Remove virtual environment
```bash
deactivate
rm -rf venv/
```

### Clear test cache
```bash
pytest --cache-clear
rm -rf .pytest_cache/
rm -rf __pycache__/
rm -rf htmlcov/
rm -f .coverage
rm -f report.html
rm -f report.json
```

## 📊 Post-Installation Checks

### 1. Run quick test suite
```bash
./run_tests.sh quick
```

### 2. Generate coverage report
```bash
pytest --cov=app --cov-report=html
open htmlcov/index.html
```

### 3. Run performance tests
```bash
pytest performance/test_latency.py -v -s
```

### 4. Verify all components
```bash
pytest --collect-only
```

Expected output:
```
collected 130+ items
```

## 🎯 Next Steps

1. ✅ Installation complete
2. ✅ Dependencies installed
3. ✅ Configuration verified
4. ✅ Tests validated

Now you can:
- Run the full test suite: `./run_tests.sh all`
- Read the quick start guide: `QUICKSTART.md`
- Review test documentation: `README.md`
- Check test summary: `TEST_SUMMARY.md`

## 📚 Additional Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [Coverage.py Documentation](https://coverage.readthedocs.io/)
- [NumPy Documentation](https://numpy.org/doc/)
- [Pandas Documentation](https://pandas.pydata.org/docs/)

## 🤝 Support

For installation issues:
1. Check error messages carefully
2. Verify Python version: `python --version`
3. Verify pip version: `pip --version`
4. Check virtual environment: `which python`
5. Review troubleshooting section above
6. Contact development team

## 📝 Notes

- Always use a virtual environment to avoid dependency conflicts
- Keep dependencies up to date for security patches
- Run tests before committing code changes
- Use coverage reports to identify untested code
- Performance tests may take longer to run

---

**Installation successful!** 🎉

You're now ready to run the complete test suite.
