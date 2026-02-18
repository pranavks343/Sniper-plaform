"""
Mock data generators for testing.
Generates realistic tick data, bar data, options chain data, and order book snapshots.
"""
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict


class TickDataGenerator:
    """Generate realistic tick data."""
    
    def __init__(self, base_price: float = 18500.0, volatility: float = 0.015):
        self.base_price = base_price
        self.volatility = volatility
        self.current_price = base_price
    
    def generate_tick(self, timestamp: datetime) -> Dict:
        """Generate a single tick."""
        # Random walk with drift
        price_change = np.random.normal(0, self.volatility * self.current_price)
        self.current_price += price_change
        
        # Bid-ask spread
        spread = self.current_price * 0.0001  # 1 basis point
        
        return {
            'symbol': 'NIFTY50',
            'timestamp': timestamp.isoformat(),
            'last_price': round(self.current_price, 2),
            'bid': round(self.current_price - spread / 2, 2),
            'ask': round(self.current_price + spread / 2, 2),
            'volume': np.random.randint(500, 2000),
            'oi': np.random.randint(40000, 60000)
        }
    
    def generate_ticks(self, num_ticks: int, start_time: datetime = None) -> List[Dict]:
        """Generate multiple ticks."""
        if start_time is None:
            start_time = datetime.now()
        
        ticks = []
        for i in range(num_ticks):
            timestamp = start_time + timedelta(seconds=i)
            tick = self.generate_tick(timestamp)
            ticks.append(tick)
        
        return ticks


class BarDataGenerator:
    """Generate realistic OHLCV bar data."""
    
    def __init__(self, base_price: float = 18500.0, volatility: float = 0.015):
        self.base_price = base_price
        self.volatility = volatility
        self.current_price = base_price
    
    def generate_bar(self, timestamp: datetime) -> Dict:
        """Generate a single OHLCV bar."""
        # Generate intrabar price movement
        open_price = self.current_price
        
        # Random high and low
        intrabar_volatility = self.volatility * self.current_price
        high = open_price + abs(np.random.normal(0, intrabar_volatility))
        low = open_price - abs(np.random.normal(0, intrabar_volatility))
        
        # Close price
        close_change = np.random.normal(0, intrabar_volatility)
        close_price = open_price + close_change
        self.current_price = close_price
        
        # Ensure high/low consistency
        high = max(high, open_price, close_price)
        low = min(low, open_price, close_price)
        
        return {
            'symbol': 'NIFTY50',
            'timestamp': timestamp.isoformat(),
            'open': round(open_price, 2),
            'high': round(high, 2),
            'low': round(low, 2),
            'close': round(close_price, 2),
            'volume': np.random.randint(30000, 100000)
        }
    
    def generate_bars(self, num_bars: int, interval: str = '1min', start_time: datetime = None) -> List[Dict]:
        """Generate multiple bars."""
        if start_time is None:
            start_time = datetime.now()
        
        # Parse interval
        if interval == '1min':
            delta = timedelta(minutes=1)
        elif interval == '5min':
            delta = timedelta(minutes=5)
        elif interval == '1hour':
            delta = timedelta(hours=1)
        elif interval == '1day':
            delta = timedelta(days=1)
        else:
            delta = timedelta(minutes=1)
        
        bars = []
        for i in range(num_bars):
            timestamp = start_time + delta * i
            bar = self.generate_bar(timestamp)
            bars.append(bar)
        
        return bars


class OptionsChainGenerator:
    """Generate realistic options chain data."""
    
    def __init__(self, spot_price: float = 18500.0, expiry_days: int = 30):
        self.spot_price = spot_price
        self.expiry_days = expiry_days
        self.expiry = expiry_days / 365.0
    
    def generate_option(self, strike: float, option_type: str) -> Dict:
        """Generate option data for a single strike."""
        # Calculate implied volatility (smile effect)
        moneyness = strike / self.spot_price
        base_iv = 0.18
        
        # Volatility smile: higher IV for OTM options
        if moneyness < 0.95 or moneyness > 1.05:
            iv = base_iv + 0.05
        else:
            iv = base_iv
        
        # Add some randomness
        iv += np.random.uniform(-0.02, 0.02)
        
        # Mock option price (simplified Black-Scholes)
        if option_type == 'CALL':
            intrinsic = max(0, self.spot_price - strike)
            time_value = strike * iv * np.sqrt(self.expiry) * 0.4
        else:  # PUT
            intrinsic = max(0, strike - self.spot_price)
            time_value = strike * iv * np.sqrt(self.expiry) * 0.4
        
        price = intrinsic + time_value
        
        return {
            'strike': strike,
            'option_type': option_type,
            'spot': self.spot_price,
            'expiry': self.expiry,
            'volatility': round(iv, 4),
            'price': round(price, 2),
            'bid': round(price * 0.98, 2),
            'ask': round(price * 1.02, 2),
            'volume': np.random.randint(100, 5000),
            'oi': np.random.randint(1000, 50000)
        }
    
    def generate_chain(self, num_strikes: int = 20) -> List[Dict]:
        """Generate complete options chain."""
        chain = []
        
        # Generate strikes around spot price
        strike_interval = 50
        start_strike = self.spot_price - (num_strikes // 2) * strike_interval
        
        for i in range(num_strikes):
            strike = start_strike + i * strike_interval
            
            # Generate both call and put
            call = self.generate_option(strike, 'CALL')
            put = self.generate_option(strike, 'PUT')
            
            chain.append(call)
            chain.append(put)
        
        return chain


class OrderBookGenerator:
    """Generate realistic order book snapshots."""
    
    def __init__(self, mid_price: float = 18500.0):
        self.mid_price = mid_price
    
    def generate_order_book(self, depth: int = 5) -> Dict:
        """Generate order book with specified depth."""
        spread = self.mid_price * 0.0001  # 1 basis point
        
        bids = []
        asks = []
        
        for i in range(depth):
            # Bids (decreasing price)
            bid_price = self.mid_price - spread / 2 - i * spread
            bid_quantity = np.random.randint(50, 500)
            bids.append({
                'price': round(bid_price, 2),
                'quantity': bid_quantity
            })
            
            # Asks (increasing price)
            ask_price = self.mid_price + spread / 2 + i * spread
            ask_quantity = np.random.randint(50, 500)
            asks.append({
                'price': round(ask_price, 2),
                'quantity': ask_quantity
            })
        
        return {
            'symbol': 'NIFTY50',
            'timestamp': datetime.now().isoformat(),
            'bids': bids,
            'asks': asks,
            'mid_price': self.mid_price,
            'spread': round(spread, 2)
        }
    
    def generate_order_book_snapshots(self, num_snapshots: int, interval_ms: int = 100) -> List[Dict]:
        """Generate multiple order book snapshots."""
        snapshots = []
        
        for i in range(num_snapshots):
            # Simulate price movement
            price_change = np.random.normal(0, self.mid_price * 0.0001)
            self.mid_price += price_change
            
            snapshot = self.generate_order_book()
            snapshots.append(snapshot)
        
        return snapshots


class HistoricalDataGenerator:
    """Generate historical data with specific regime characteristics."""
    
    @staticmethod
    def generate_trending_data(num_days: int = 100, base_price: float = 18000.0) -> np.ndarray:
        """Generate trending market data."""
        drift = 0.001  # Positive drift
        volatility = 0.01
        
        returns = np.random.normal(drift, volatility, num_days)
        prices = base_price * np.exp(np.cumsum(returns))
        
        return prices
    
    @staticmethod
    def generate_mean_reverting_data(num_days: int = 100, mean_price: float = 18500.0) -> np.ndarray:
        """Generate mean-reverting market data."""
        prices = []
        current_price = mean_price
        
        for _ in range(num_days):
            # Mean reversion force
            reversion = 0.1 * (mean_price - current_price)
            noise = np.random.normal(0, 30)
            current_price += reversion + noise
            prices.append(current_price)
        
        return np.array(prices)
    
    @staticmethod
    def generate_volatile_data(num_days: int = 100, base_price: float = 18300.0) -> np.ndarray:
        """Generate volatile market data."""
        volatility = 0.03  # High volatility
        
        returns = np.random.normal(0, volatility, num_days)
        prices = base_price * np.exp(np.cumsum(returns))
        
        return prices
    
    @staticmethod
    def generate_mixed_regime_data(num_days: int = 252) -> np.ndarray:
        """Generate data with mixed regimes."""
        prices = []
        
        # Divide into three regimes
        regime_length = num_days // 3
        
        # Trending regime
        trending = HistoricalDataGenerator.generate_trending_data(regime_length, 18000.0)
        prices.extend(trending)
        
        # Mean-reverting regime
        mean_reverting = HistoricalDataGenerator.generate_mean_reverting_data(
            regime_length, trending[-1]
        )
        prices.extend(mean_reverting)
        
        # Volatile regime
        volatile = HistoricalDataGenerator.generate_volatile_data(
            num_days - 2 * regime_length, mean_reverting[-1]
        )
        prices.extend(volatile)
        
        return np.array(prices)
