# Contributing to Sniper Framework

Thanks for your interest in contributing! We welcome all types of contributions: bug fixes, feature additions, documentation improvements, and more.

## How to Contribute

### 1. Fork & Clone
```bash
git clone https://github.com/YOUR_USERNAME/sniper-framework.git
cd sniper-framework
```

### 2. Create a Feature Branch
```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/your-bug-fix
```

### 3. Set Up Development Environment
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -e ".[dev]"
```

### 4. Make Your Changes
- Follow PEP 8 style guide
- Add docstrings to all functions/classes
- Include type hints (Python 3.10+)
- Write tests for new features

### 5. Test Your Changes
```bash
pytest sniper/tests/
```

### 6. Commit with Clear Messages
```bash
git commit -m "feat: add new feature" -m "Detailed description of what changed and why"
```

Commit format:
- `feat:` new feature
- `fix:` bug fix
- `docs:` documentation
- `test:` tests
- `refactor:` code refactoring
- `perf:` performance improvement

### 7. Push & Create Pull Request
```bash
git push origin feature/your-feature-name
```
Then create a PR on GitHub with:
- Clear title
- Description of changes
- Reference any related issues (#123)

## Code Style

### Python
- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/)
- Use type hints: `def process(data: list[float]) -> float:`
- Max line length: 100 characters
- Use docstrings for all public functions:

```python
def calculate_greeks(option_price: float, spot: float) -> GreekValues:
    """
    Calculate option Greeks.

    Args:
        option_price: Current option price
        spot: Spot price of underlying

    Returns:
        GreekValues containing delta, gamma, theta, vega, rho

    Raises:
        ValueError: If spot price is negative
    """
    pass
```

## Testing

- Write tests in `sniper/tests/`
- One test file per module: `sniper/core/risk.py` → `sniper/tests/test_risk.py`
- Use pytest fixtures for setup

```python
import pytest
from sniper import CircuitBreaker

def test_circuit_breaker_activation():
    """Test that breaker activates on loss threshold."""
    breaker = CircuitBreaker()
    # ... test code
    assert breaker.is_active
```

## Documentation

- Update README.md if adding new public APIs
- Add examples for new features
- Include docstrings in code

## Areas We Need Help

- [ ] More broker integrations (Kraken, Binance, etc.)
- [ ] Machine learning models for regime detection
- [ ] Performance optimizations
- [ ] More comprehensive examples
- [ ] Trading strategy templates
- [ ] Better error handling
- [ ] Documentation improvements

## Questions?

- Open an issue for discussion
- Check existing issues before creating new ones
- Be respectful and constructive

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Happy coding! 🚀
