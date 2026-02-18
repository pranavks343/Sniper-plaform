# Installation Guide

## Prerequisites

- Python 3.10 or higher
- pip (Python package manager)
- Virtual environment (recommended)

## Quick Start

### 1. Basic Installation

```bash
pip install sniper-framework
```

### 2. With Optional Dependencies

```bash
# For HMM regime detection (requires hmmlearn)
pip install sniper-framework[hmm]

# For development (includes testing tools)
pip install sniper-framework[dev]
```

### 3. Installation from Source (Development)

```bash
git clone https://github.com/pranavks343/sniper-framework.git
cd sniper-framework

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install in development mode with all extras
pip install -e ".[dev,hmm]"
```

## Verify Installation

```python
import sniper
print(sniper.__version__)

# Quick test
from sniper import CircuitBreaker
breaker = CircuitBreaker()
print("✅ Sniper Framework installed successfully!")
```

## System Requirements

| Component | Requirement |
|-----------|-------------|
| Python | 3.10+ |
| NumPy | 1.24+ |
| Pydantic | 2.0+ |
| hmmlearn | 0.3.0+ (optional) |

## Platform Support

- ✅ macOS (Intel & Apple Silicon)
- ✅ Linux (Ubuntu 20.04+, Debian, RHEL)
- ✅ Windows (10, 11)

## Troubleshooting

### "ModuleNotFoundError: No module named 'sniper'"

**Solution**: Ensure you're in the activated virtual environment
```bash
source .venv/bin/activate  # macOS/Linux
# or
.venv\Scripts\activate     # Windows
```

### "No module named 'hmmlearn'"

**Solution**: Install optional dependencies
```bash
pip install sniper-framework[hmm]
```

### Import errors in IDE

**Solution**: Configure IDE to use virtual environment
- VS Code: Select interpreter from `.venv/bin/python`
- PyCharm: Settings → Project → Python Interpreter → `.venv`

### Permission denied error

**Solution**: Use user installation
```bash
pip install --user sniper-framework
```

## Upgrade

```bash
pip install --upgrade sniper-framework
```

## Uninstall

```bash
pip uninstall sniper-framework
```

## Next Steps

After installation, check out:
- [README.md](README.md) - Overview and quick start
- [examples/](examples/) - Usage examples
- [API Documentation](https://github.com/pranavks343/sniper-framework/wiki) - Full API reference

---

Need help? Open an issue on [GitHub](https://github.com/pranavks343/sniper-framework/issues)
