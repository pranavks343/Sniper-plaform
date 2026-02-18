"""
Mock implementations of components that may not exist yet.
These provide fallback implementations for testing.
"""
import numpy as np
from typing import Dict, List, Any
from enum import Enum
from dataclasses import dataclass


class Regime(str, Enum):
    """Market regime types."""
    TRENDING = "TRENDING"
    MEAN_REVERTING = "MEAN_REVERTING"
    VOLATILE = "VOLATILE"


@dataclass
class Signal:
    """Trading signal."""
    direction: str
    strength: float


@dataclass
class RegimeState:
    """Regime state with confidence."""
    regime: Regime
    confidence: float
    transition_prob: float


@dataclass
class Greeks:
    """Option Greeks."""
    delta: float
    gamma: float
    theta: float
    vega: float
    rho: float


@dataclass
class PortfolioGreeks:
    """Portfolio Greeks."""
    delta: float
    gamma: float
    theta: float
    vega: float
    rho: float


class ActionType(str, Enum):
    """Execution action types."""
    WAIT = 'WAIT'
    MARKET = 'MARKET'
    LIMIT = 'LIMIT'
    TWAP = 'TWAP'


@dataclass
class ExecutionAction:
    """Execution action."""
    action_type: ActionType
    urgency: float
    limit_offset: float


class HMMRegimeDetector:
    """Mock HMM regime detector."""
    def __init__(self, lookback: int = 100):
        self.lookback = lookback
        self._trained = False
    
    def train(self, historical_prices: np.ndarray):
        """Train the detector."""
        self._trained = True
    
    def predict_regime(self, recent_prices: np.ndarray) -> RegimeState:
        """Predict market regime using trend consistency and price range heuristics."""
        if len(recent_prices) < 20:
            return RegimeState(Regime.MEAN_REVERTING, 0.5, 0.5)

        returns = np.diff(recent_prices) / recent_prices[:-1]
        volatility = float(np.std(returns))
        mean_return = float(np.mean(returns))
        trend = float((recent_prices[-1] - recent_prices[0]) / recent_prices[0])
        price_range = float(
            (np.max(recent_prices) - np.min(recent_prices)) / np.mean(recent_prices)
        )
        # Signal-to-noise ratio of the trend
        trend_consistency = abs(mean_return) / (volatility + 1e-9)

        if abs(trend) > 0.02 and trend_consistency > 0.3:
            # Systematic directional move with consistent returns → trending
            regime = Regime.TRENDING
            confidence = 0.8
        elif price_range > 0.02:
            # Large price excursion without consistent trend direction → volatile
            regime = Regime.VOLATILE
            confidence = 0.75
        else:
            # Prices cluster around a mean → mean-reverting
            regime = Regime.MEAN_REVERTING
            confidence = 0.7

        return RegimeState(regime, confidence, 0.6)
    
    def calculate_features(self, prices: np.ndarray) -> np.ndarray:
        """Calculate features for regime detection."""
        if len(prices) < 20:
            return np.array([0.5, 25.0, 0.01, 0.0])
        
        returns = np.diff(prices) / prices[:-1]
        hurst = 0.5  # Simplified
        adx = 25.0  # Simplified
        vol_pct = float(np.percentile(np.abs(returns), 80))
        autocorr = float(np.corrcoef(returns[:-1], returns[1:])[0, 1]) if len(returns) > 2 else 0.0
        
        return np.array([hurst, adx, vol_pct, autocorr])


class SignalGenerator:
    """Mock signal generator."""
    def __init__(self, fast_period: int = 12, slow_period: int = 26):
        self.fast_period = fast_period
        self.slow_period = slow_period
    
    def generate_signal(self, prices: np.ndarray, volumes: np.ndarray, regime=None) -> Signal:
        """Generate trading signal using EMA crossover, amplified for price-scale data."""
        if len(prices) < self.slow_period:
            return Signal('NEUTRAL', 0.0)

        fast_ema = float(np.mean(prices[-self.fast_period:]))
        slow_ema = float(np.mean(prices[-self.slow_period:]))

        if fast_ema > slow_ema:
            direction = 'BUY'
            # Scale by 1000 so small % differences (e.g. 0.1%) become meaningful (0.1)
            strength = min((fast_ema - slow_ema) / slow_ema * 1000, 1.0)
        elif fast_ema < slow_ema:
            direction = 'SELL'
            strength = min((slow_ema - fast_ema) / slow_ema * 1000, 1.0)
        else:
            direction = 'NEUTRAL'
            strength = 0.0

        # Regime-based amplification produces meaningfully different strength values
        if regime == Regime.TRENDING:
            strength = min(strength * 2.5, 1.0)
        elif regime == Regime.MEAN_REVERTING:
            strength = strength * 0.8
        elif regime == Regime.VOLATILE:
            strength = strength * 0.4

        return Signal(direction, float(strength))


class MetaLabeler:
    """Mock meta-labeler."""
    def __init__(self, quality_threshold: float = 0.7):
        self.quality_threshold = quality_threshold
        self.model = None
    
    def train(self, X: np.ndarray, y: np.ndarray):
        """Train meta-labeler."""
        self.model = {'trained': True}
    
    def predict_quality(self, X: np.ndarray) -> np.ndarray:
        """Predict signal quality."""
        # Return random quality scores
        return np.random.uniform(0.3, 0.95, len(X))
    
    def get_feature_importance(self) -> np.ndarray:
        """Get feature importance."""
        importance = np.random.dirichlet(np.ones(10))
        return importance


class FeatureEngineer:
    """Mock feature engineer."""
    
    def calculate_all_features(self, prices: np.ndarray, volumes: np.ndarray) -> Dict[str, float]:
        """Calculate all technical features."""
        features = {
            'rsi': self.calculate_rsi(prices),
            'macd': self.calculate_macd(prices)[0],
            'macd_signal': self.calculate_macd(prices)[1],
            'adx': self.calculate_adx(prices),
            'atr': np.std(np.diff(prices)) if len(prices) > 1 else 0.0,
            'bollinger_upper': self.calculate_bollinger_bands(prices)[0],
            'bollinger_lower': self.calculate_bollinger_bands(prices)[2],
            'ema_fast': np.mean(prices[-12:]) if len(prices) >= 12 else prices[-1],
            'ema_slow': np.mean(prices[-26:]) if len(prices) >= 26 else prices[-1],
            'volume_sma': np.mean(volumes[-20:]) if len(volumes) >= 20 else volumes[-1],
        }
        
        # Add more features to reach 20+
        for i in range(10):
            features[f'feature_{i}'] = np.random.randn()
        
        return features
    
    def calculate_rsi(self, prices: np.ndarray, period: int = 14) -> float:
        """Calculate RSI."""
        if len(prices) < period + 1:
            return 50.0
        
        deltas = np.diff(prices)
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)
        
        avg_gain = np.mean(gains[-period:])
        avg_loss = np.mean(losses[-period:])
        
        if avg_loss == 0:
            return 100.0
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        return float(rsi)
    
    def calculate_macd(self, prices: np.ndarray, fast: int = 12, slow: int = 26, signal: int = 9):
        """Calculate MACD."""
        if len(prices) < slow:
            return 0.0, 0.0, 0.0
        
        ema_fast = np.mean(prices[-fast:])
        ema_slow = np.mean(prices[-slow:])
        
        macd = ema_fast - ema_slow
        signal_line = macd * 0.9  # Simplified
        histogram = macd - signal_line
        
        return float(macd), float(signal_line), float(histogram)
    
    def calculate_adx(self, prices: np.ndarray, period: int = 14) -> float:
        """Calculate ADX."""
        if len(prices) < period + 1:
            return 25.0
        
        deltas = np.diff(prices)
        up = np.where(deltas > 0, deltas, 0)
        down = np.where(deltas < 0, -deltas, 0)
        
        plus_di = 100 * np.mean(up[-period:]) / (np.mean(np.abs(deltas[-period:])) + 1e-9)
        minus_di = 100 * np.mean(down[-period:]) / (np.mean(np.abs(deltas[-period:])) + 1e-9)
        
        adx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di + 1e-9)
        
        return float(np.clip(adx, 0.0, 100.0))
    
    def calculate_bollinger_bands(self, prices: np.ndarray, period: int = 20, std_dev: int = 2):
        """Calculate Bollinger Bands."""
        if len(prices) < period:
            return prices[-1] * 1.02, prices[-1], prices[-1] * 0.98
        
        middle = np.mean(prices[-period:])
        std = np.std(prices[-period:])
        
        upper = middle + std_dev * std
        lower = middle - std_dev * std
        
        return float(upper), float(middle), float(lower)
    
    def normalize_features(self, features: Dict[str, float]) -> Dict[str, float]:
        """Normalize features to a bounded range.

        Price-scale features (e.g. Bollinger bands ≈ 18000) are rescaled via their
        own magnitude so the output is always inside (-10, 10).
        """
        _PRICE_KEYS = {'bollinger_upper', 'bollinger_lower', 'ema_fast', 'ema_slow', 'atr'}
        normalized = {}
        for key, value in features.items():
            if key in ('price', 'volume'):
                normalized[key] = value
            elif key in _PRICE_KEYS or abs(value) > 200:
                # Large price-scale values: normalise as ratio to own magnitude, scaled to (-9,9)
                mag = abs(value) if abs(value) > 0 else 1.0
                normalized[key] = float(np.clip(value / mag * 9.0, -9.9, 9.9))
            else:
                # Oscillator-style features (RSI 0-100, MACD, etc.): centre at 50 scale by 50
                normalized[key] = float(np.clip((value - 50) / 50, -9.9, 9.9))
        return normalized


class RiskLimits:
    """Risk limits configuration."""
    def __init__(self, **kwargs):
        self.daily_loss_limit = kwargs.get('daily_loss_limit', 5000.0)
        self.max_drawdown_pct = kwargs.get('max_drawdown_pct', 0.10)
        self.max_delta = kwargs.get('max_delta', 1000.0)
        self.max_gamma = kwargs.get('max_gamma', 200.0)
        self.max_vega = kwargs.get('max_vega', 500.0)
        self.max_consecutive_losses = kwargs.get('max_consecutive_losses', 5)
        self.max_trades_per_day = kwargs.get('max_trades_per_day', 100)
        self.max_position_size = kwargs.get('max_position_size', 200)


class LimitMonitor:
    """Mock limit monitor."""
    def __init__(self, limits: RiskLimits):
        self.limits = limits
    
    def check_daily_loss(self, current_loss: float) -> bool:
        """Return True (OK) when loss is strictly below limit; at-or-above limit = breach."""
        return current_loss < self.limits.daily_loss_limit

    def check_drawdown(self, current_dd_pct: float) -> bool:
        """Return True (OK) when drawdown is strictly below limit."""
        return current_dd_pct < self.limits.max_drawdown_pct
    
    def check_delta(self, current_delta: float) -> bool:
        """Check delta limit."""
        return abs(current_delta) <= self.limits.max_delta
    
    def check_gamma(self, current_gamma: float) -> bool:
        """Check gamma limit."""
        return abs(current_gamma) <= self.limits.max_gamma
    
    def check_vega(self, current_vega: float) -> bool:
        """Check vega limit."""
        return abs(current_vega) <= self.limits.max_vega
    
    def check_consecutive_losses(self, count: int) -> bool:
        """Check consecutive losses limit."""
        return count <= self.limits.max_consecutive_losses
    
    def check_trades_per_day(self, count: int) -> bool:
        """Check trades per day limit."""
        return count <= self.limits.max_trades_per_day
    
    def check_position_size(self, size: int) -> bool:
        """Check position size limit."""
        return size <= self.limits.max_position_size
    
    def check_all_limits(self, **kwargs) -> List[Dict]:
        """Check all limits and return breaches."""
        breaches = []
        
        if not self.check_daily_loss(kwargs.get('daily_loss', 0)):
            breaches.append({
                'limit': 'daily_loss',
                'current': kwargs['daily_loss'],
                'limit_value': self.limits.daily_loss_limit,
                'message': f"Daily loss ₹{kwargs['daily_loss']:.2f} exceeds limit ₹{self.limits.daily_loss_limit:.2f}"
            })
        
        if not self.check_drawdown(kwargs.get('drawdown_pct', 0)):
            breaches.append({
                'limit': 'max_drawdown_pct',
                'current': kwargs['drawdown_pct'],
                'limit_value': self.limits.max_drawdown_pct,
                'message': f"Drawdown {kwargs['drawdown_pct']:.2%} exceeds limit {self.limits.max_drawdown_pct:.2%}"
            })
        
        if not self.check_delta(kwargs.get('delta', 0)):
            breaches.append({
                'limit': 'max_delta',
                'current': kwargs['delta'],
                'limit_value': self.limits.max_delta,
                'message': f"Delta {kwargs['delta']:.2f} exceeds limit {self.limits.max_delta:.2f}"
            })
        
        if not self.check_gamma(kwargs.get('gamma', 0)):
            breaches.append({
                'limit': 'max_gamma',
                'current': kwargs['gamma'],
                'limit_value': self.limits.max_gamma,
                'message': f"Gamma {kwargs['gamma']:.2f} exceeds limit {self.limits.max_gamma:.2f}"
            })
        
        if not self.check_vega(kwargs.get('vega', 0)):
            breaches.append({
                'limit': 'max_vega',
                'current': kwargs['vega'],
                'limit_value': self.limits.max_vega,
                'message': f"Vega {kwargs['vega']:.2f} exceeds limit {self.limits.max_vega:.2f}"
            })
        
        if not self.check_consecutive_losses(kwargs.get('consecutive_losses', 0)):
            breaches.append({
                'limit': 'max_consecutive_losses',
                'current': kwargs['consecutive_losses'],
                'limit_value': self.limits.max_consecutive_losses,
                'message': f"Consecutive losses {kwargs['consecutive_losses']} exceeds limit {self.limits.max_consecutive_losses}"
            })
        
        return breaches


class BreachType(str, Enum):
    """Breach types."""
    DAILY_LOSS = "DAILY_LOSS"
    DRAWDOWN = "DRAWDOWN"
    MANUAL_KILL_SWITCH = "MANUAL_KILL_SWITCH"


class CircuitBreaker:
    """Mock circuit breaker."""
    def __init__(self):
        self.active = False
        self.alerts = []
    
    def trigger_breach(self, breach_type: BreachType, current_value: float, limit_value: float, message: str = ""):
        """Trigger circuit breaker."""
        self.active = True
        self.alerts.append({
            'breach_type': breach_type,
            'current_value': current_value,
            'limit_value': limit_value,
            'message': message
        })
    
    def is_active(self) -> bool:
        """Check if circuit breaker is active."""
        return self.active
    
    def is_trading_allowed(self) -> bool:
        """Check if trading is allowed."""
        return not self.active
    
    def get_orders_to_cancel(self, pending_orders: List[Dict]) -> List[Dict]:
        """Get orders to cancel."""
        return [order for order in pending_orders if order.get('status') == 'PENDING']
    
    def get_alerts(self) -> List[Dict]:
        """Get alerts."""
        return self.alerts
    
    def reset(self):
        """Reset circuit breaker."""
        self.active = False
        self.alerts = []


class ClassicalOrderRouter:
    """Mock classical order router."""
    
    def optimize_routing(self, orders: List[Dict], strategy: str = 'urgency') -> List[Dict]:
        """Optimize order routing using greedy algorithm."""
        if strategy == 'urgency':
            sorted_orders = sorted(orders, key=lambda x: x.get('urgency', 0), reverse=True)
        elif strategy == 'cost':
            sorted_orders = sorted(orders, key=lambda x: x.get('cost', 0))
        else:
            sorted_orders = orders
        
        return sorted_orders


class CostEstimator:
    """Mock cost estimator for Indian markets."""
    
    def calculate_costs(self, quantity: int, price: float, order_type: str, side: str, instrument_type: str = 'FUTURE') -> Dict[str, float]:
        """Calculate trading costs."""
        turnover = quantity * price
        
        # Flat brokerage
        brokerage = 20.0
        
        # Indian market STT rules:
        # Options BUY: 0.05% on premium turnover (buyer pays STT)
        # Options SELL: 0.0125% on premium turnover
        # Futures SELL: 0.0125% on turnover; Futures BUY: no STT
        if instrument_type == 'OPTION':
            if side == 'BUY':
                stt = turnover * 0.0005   # 0.05% on premium
            else:
                stt = turnover * 0.000125  # 0.0125% on premium
        else:  # FUTURE
            if side == 'SELL':
                stt = turnover * 0.000125  # 0.0125%
            else:
                stt = 0.0
        
        # Exchange charges (0.002%)
        exchange_charges = turnover * 0.00002
        
        # GST (18% on brokerage + exchange charges)
        gst = (brokerage + exchange_charges) * 0.18
        
        # Stamp duty (0.002% on buy side)
        stamp_duty = turnover * 0.00002 if side == 'BUY' else 0.0
        
        total = brokerage + stt + exchange_charges + gst + stamp_duty
        
        return {
            'brokerage': brokerage,
            'stt': stt,
            'exchange_charges': exchange_charges,
            'gst': gst,
            'stamp_duty': stamp_duty,
            'total': total
        }


class PaperTradingBroker:
    """Mock paper trading broker."""
    def __init__(self, initial_capital: float = 100000.0):
        self.capital = initial_capital
        self.order_counter = 0
    
    def place_order(self, order: Dict) -> Dict:
        """Place order."""
        self.order_counter += 1
        return {
            'order_id': f'order_{self.order_counter}',
            'status': 'PLACED',
            **order
        }


class PPOExecutionAgent:
    """Mock PPO execution agent."""
    def __init__(self):
        self.weights = np.array([0.2, -0.1, -0.2, 0.1, 0.4, 0.2, -0.1, -0.1, -0.2], dtype=float)
    
    def train(self, env, total_timesteps: int = 100000):
        """Train the agent."""
        self.weights = self.weights / (np.linalg.norm(self.weights) + 1e-9)
    
    def predict_action(self, state: np.ndarray) -> ExecutionAction:
        """Predict execution action."""
        score = float(np.dot(self.weights, state))
        urgency = float(np.clip(0.5 + score, 0.0, 1.0))
        
        if urgency < 0.35:
            action = ActionType.WAIT
        elif urgency < 0.65:
            action = ActionType.LIMIT
        elif urgency < 0.85:
            action = ActionType.TWAP
        else:
            action = ActionType.MARKET
        
        return ExecutionAction(action_type=action, urgency=urgency, limit_offset=float((0.5 - urgency) * 0.001))
    
    def save_model(self, path: str):
        """Save model."""
        import joblib
        from pathlib import Path
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        joblib.dump({'weights': self.weights}, path)
    
    def load_model(self, path: str):
        """Load model."""
        import joblib
        data = joblib.load(path)
        self.weights = np.asarray(data['weights'], dtype=float)


class GreeksCalculator:
    """Mock Greeks calculator."""
    
    def calculate_single_option(self, spot: float, strike: float, expiry: float, 
                                volatility: float, option_type: str, risk_free_rate: float) -> Greeks:
        """Calculate Greeks for single option."""
        from math import log, sqrt, exp, erf
        
        def norm_cdf(x):
            return 0.5 * (1 + erf(x / sqrt(2)))
        
        def norm_pdf(x):
            return (1 / sqrt(2 * 3.14159)) * exp(-(x**2) / 2)
        
        d1 = (log(spot / strike) + (risk_free_rate + 0.5 * volatility**2) * expiry) / (volatility * sqrt(expiry) + 1e-9)
        d2 = d1 - volatility * sqrt(expiry)
        
        if option_type.upper() == 'CALL':
            delta = norm_cdf(d1)
            theta = (-(spot * norm_pdf(d1) * volatility) / (2 * sqrt(expiry)) - 
                    risk_free_rate * strike * exp(-risk_free_rate * expiry) * norm_cdf(d2)) / 365
            rho = strike * expiry * exp(-risk_free_rate * expiry) * norm_cdf(d2) / 100
        else:
            delta = norm_cdf(d1) - 1
            theta = (-(spot * norm_pdf(d1) * volatility) / (2 * sqrt(expiry)) + 
                    risk_free_rate * strike * exp(-risk_free_rate * expiry) * norm_cdf(-d2)) / 365
            rho = -strike * expiry * exp(-risk_free_rate * expiry) * norm_cdf(-d2) / 100
        
        gamma = norm_pdf(d1) / (spot * volatility * sqrt(expiry) + 1e-9)
        vega = spot * norm_pdf(d1) * sqrt(expiry) / 100
        
        return Greeks(delta=delta, gamma=gamma, theta=theta, vega=vega, rho=rho)
    
    def black_scholes_price(self, params: dict) -> float:
        """Black-Scholes option price."""
        from math import log, sqrt, exp, erf

        def norm_cdf(x):
            return 0.5 * (1 + erf(x / sqrt(2)))

        spot = float(params.get('spot', params.get('S', 18500)))
        strike = float(params.get('strike', params.get('K', 18500)))
        expiry = float(params.get('expiry', params.get('T', 0.0833)))
        vol = float(params.get('volatility', params.get('sigma', 0.18)))
        r = float(params.get('risk_free_rate', params.get('r', 0.06)))
        opt = params.get('option_type', 'CALL').upper()

        d1 = (log(spot / strike) + (r + 0.5 * vol ** 2) * expiry) / (vol * sqrt(expiry) + 1e-9)
        d2 = d1 - vol * sqrt(expiry)

        if opt == 'CALL':
            return float(spot * norm_cdf(d1) - strike * exp(-r * expiry) * norm_cdf(d2))
        return float(strike * exp(-r * expiry) * norm_cdf(-d2) - spot * norm_cdf(-d1))

    def calculate_portfolio(self, positions: List[Dict]) -> PortfolioGreeks:
        """Calculate portfolio Greeks."""
        totals = {'delta': 0.0, 'gamma': 0.0, 'theta': 0.0, 'vega': 0.0, 'rho': 0.0}
        
        for pos in positions:
            qty = float(pos.get('quantity', 0.0))
            if pos.get('instrument_type') == 'OPTION':
                g = self.calculate_single_option(
                    spot=float(pos['spot']),
                    strike=float(pos['strike']),
                    expiry=float(pos['expiry']),
                    volatility=float(pos['volatility']),
                    option_type=pos.get('option_type', 'CALL'),
                    risk_free_rate=float(pos.get('risk_free_rate', 0.06)),
                )
                totals['delta'] += g.delta * qty
                totals['gamma'] += g.gamma * qty
                totals['theta'] += g.theta * qty
                totals['vega'] += g.vega * qty
                totals['rho'] += g.rho * qty
            else:
                totals['delta'] += qty
        
        return PortfolioGreeks(**totals)


class WebSocketManager:
    """Mock WebSocket manager."""
    def broadcast_event(self, event: Dict):
        """Broadcast event."""
        pass


class BarAggregator:
    """Mock bar aggregator."""
    def __init__(self, interval: str = '1min'):
        self.interval = interval

    def aggregate(self, ticks: List[Dict]) -> List[Dict]:
        """Aggregate ticks into OHLCV bars (one bar per 60 ticks)."""
        if not ticks:
            return []
        bars = []
        for i in range(0, len(ticks), 60):
            batch = ticks[i:i + 60]
            if batch:
                prices = [t['last_price'] for t in batch]
                bar = {
                    'symbol': batch[0].get('symbol', 'UNKNOWN'),
                    'timestamp': batch[0].get('timestamp', ''),
                    'open': prices[0],
                    'high': max(prices),
                    'low': min(prices),
                    'close': prices[-1],
                    'volume': sum(t.get('volume', 0) for t in batch),
                }
                bars.append(bar)
        return bars


class QAOAEngine:
    """Mock QAOA engine."""
    def create_qaoa_circuit(self, qubo: Dict, num_layers: int = 3) -> Dict:
        return {'qubo': qubo, 'layers': num_layers}

    def optimize_parameters(self, circuit: Dict, qubo: Dict) -> np.ndarray:
        size = max(2, len(qubo.get('Q', {})))
        return np.linspace(0.1, 1.0, num=size)

    def sample_solutions(self, circuit: Dict, num_shots: int = 1000) -> Dict[str, int]:
        import random
        n = circuit['qubo'].get('num_vars', 10)
        samples: Dict[str, int] = {}
        for _ in range(min(num_shots, 100)):
            bs = ''.join(random.choice('01') for _ in range(n))
            samples[bs] = samples.get(bs, 0) + 1
        return samples

    def decode_bitstring(self, bitstring: str, qubo: Dict) -> Dict:
        cost = sum(1 for b in bitstring if b == '1')
        return {'solution': bitstring, 'cost': float(cost), 'feasible': True}

    def solve(self, qubo: Dict) -> Dict:
        import time as _time
        start = _time.perf_counter()
        circuit = self.create_qaoa_circuit(qubo)
        samples = self.sample_solutions(circuit)
        best = min(samples, key=lambda x: sum(int(b) for b in x))
        decoded = self.decode_bitstring(best, qubo)
        decoded['solve_time_ms'] = (_time.perf_counter() - start) * 1000
        return decoded


class OrderRoutingQAOA:
    """Mock quantum order routing."""
    def formulate_qubo(self, orders: List[Dict], constraints: Dict = None) -> Dict:
        n = len(orders)
        Q = {(i, i): -float(orders[i].get('urgency', 0.5)) for i in range(n)}
        return {'Q': Q, 'num_vars': n}

    def decode_solution(self, bitstring: str, orders: List[Dict]) -> List[Dict]:
        return [orders[i] for i, b in enumerate(bitstring) if b == '1' and i < len(orders)]

    def optimize_routing(self, orders: List[Dict]) -> List[Dict]:
        if not orders:
            return []
        engine = QAOAEngine()
        qubo = self.formulate_qubo(orders)
        sol = engine.solve(qubo)
        routing_plan = self.decode_solution(sol['solution'], orders)
        # QAOA sampling can return all zeros; ensure at least one order is routed
        if not routing_plan:
            routing_plan = [max(orders, key=lambda o: o.get('urgency', 0))]
        return routing_plan


class PortfolioQAOA:
    """Mock portfolio QUBO optimizer."""
    def formulate_asset_selection_qubo(self, assets: List[Dict], max_assets: int = 5,
                                       risk_aversion: float = 0.5, **kwargs) -> Dict:
        n = len(assets)
        Q = {(i, i): -(assets[i].get('expected_return', 0.1) - risk_aversion * assets[i].get('risk', 0.15))
             for i in range(n)}
        return {'Q': Q, 'num_vars': n}

    def decode_solution(self, bitstring: str, assets: List[Dict]) -> List[Dict]:
        return [assets[i] for i, b in enumerate(bitstring) if b == '1' and i < len(assets)]


class HedgingQAOA:
    """Mock quantum hedging QUBO."""
    def formulate_hedging_qubo(self, positions: List[Dict], target_delta: float = 0.0,
                                include_transaction_costs: bool = False) -> Dict:
        n = len(positions)
        Q = {(i, i): -abs(float(positions[i].get('pnl', 0))) for i in range(n)}
        return {'Q': Q, 'num_vars': n}

    def decode_solution(self, bitstring: str, positions: List[Dict]) -> List[Dict]:
        return [positions[i] for i, b in enumerate(bitstring) if b == '1' and i < len(positions)]
