"""
Pytest configuration and shared fixtures for the sniper trading platform test suite.
"""
import sys
from pathlib import Path

import numpy as np
import pytest

# Add mocks to path FIRST (so they're used as fallback)
mocks_path = Path(__file__).parent / "mocks"
sys.path.insert(0, str(mocks_path))

# Add the backend app to the Python path
backend_path = Path(__file__).parent.parent / "sniper-platform" / "apps" / "sniper-backend"
sys.path.insert(0, str(backend_path))


@pytest.fixture
def sample_prices():
    """Generate sample price data for testing."""
    np.random.seed(42)
    base_price = 18000.0
    returns = np.random.normal(0.0005, 0.02, 252)
    prices = base_price * np.exp(np.cumsum(returns))
    return prices


@pytest.fixture
def sample_tick_data():
    """Generate sample tick data."""
    return {
        'symbol': 'NIFTY50',
        'timestamp': '2026-02-18T10:30:00',
        'last_price': 18500.0,
        'bid': 18499.5,
        'ask': 18500.5,
        'volume': 1000,
        'oi': 50000
    }


@pytest.fixture
def sample_bar_data():
    """Generate sample OHLCV bar data."""
    return {
        'symbol': 'NIFTY50',
        'timestamp': '2026-02-18T10:30:00',
        'open': 18480.0,
        'high': 18520.0,
        'low': 18470.0,
        'close': 18500.0,
        'volume': 50000
    }


@pytest.fixture
def sample_option_position():
    """Generate sample option position for Greeks calculation."""
    return {
        'instrument_type': 'OPTION',
        'spot': 18500.0,
        'strike': 18500.0,
        'expiry': 0.0833,  # ~1 month
        'volatility': 0.18,
        'option_type': 'CALL',
        'risk_free_rate': 0.06,
        'quantity': 100.0
    }


@pytest.fixture
def sample_portfolio():
    """Generate sample portfolio with multiple positions."""
    return [
        {
            'instrument_type': 'OPTION',
            'spot': 18500.0,
            'strike': 18500.0,
            'expiry': 0.0833,
            'volatility': 0.18,
            'option_type': 'CALL',
            'risk_free_rate': 0.06,
            'quantity': 100.0
        },
        {
            'instrument_type': 'OPTION',
            'spot': 18500.0,
            'strike': 18600.0,
            'expiry': 0.0833,
            'volatility': 0.19,
            'option_type': 'PUT',
            'risk_free_rate': 0.06,
            'quantity': -50.0
        },
        {
            'instrument_type': 'FUTURE',
            'quantity': 25.0
        }
    ]


@pytest.fixture
def sample_qubo():
    """Generate sample QUBO problem."""
    return {
        'Q': {
            (0, 0): -1.0,
            (1, 1): -1.5,
            (2, 2): -2.0,
            (0, 1): 0.5,
            (1, 2): 0.3
        },
        'num_vars': 3
    }


@pytest.fixture
def mock_rl_state():
    """Generate mock RL agent state."""
    return np.array([
        0.5,   # normalized price
        0.3,   # volatility
        0.6,   # volume
        0.4,   # spread
        0.7,   # momentum
        0.2,   # time urgency
        0.5,   # position size
        0.3,   # market impact
        0.4    # risk score
    ], dtype=float)


@pytest.fixture
def regime_labeled_data():
    """Generate historical data with regime labels."""
    np.random.seed(42)
    
    # Trending regime
    trending_prices = 18000 + np.cumsum(np.random.normal(5, 10, 100))
    
    # Mean reverting regime
    mean_reverting_prices = 18500 + np.random.normal(0, 50, 100)
    
    # Volatile regime
    volatile_prices = 18300 + np.cumsum(np.random.normal(0, 30, 100))
    
    return {
        'trending': trending_prices,
        'mean_reverting': mean_reverting_prices,
        'volatile': volatile_prices
    }


@pytest.fixture
def mock_order():
    """Generate mock order."""
    return {
        'symbol': 'NIFTY50',
        'order_type': 'MARKET',
        'side': 'BUY',
        'quantity': 50,
        'price': None,
        'strategy_id': 'test_strategy_1'
    }


@pytest.fixture
def mock_position():
    """Generate mock position."""
    return {
        'symbol': 'NIFTY50',
        'quantity': 100,
        'avg_price': 18450.0,
        'current_price': 18500.0,
        'pnl': 5000.0,
        'instrument_type': 'FUTURE'
    }
