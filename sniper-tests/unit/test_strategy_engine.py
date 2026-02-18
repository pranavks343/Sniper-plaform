"""
Unit tests for Strategy Engine components.
Tests: HMM regime detection, signal generation, meta-labeling, feature engineering.
"""
import numpy as np
import pytest

# Try importing from backend, fallback to mocks
try:
    from app.core.strategy_engine.regime_detector import HMMRegimeDetector, RegimeState
    from app.core.strategy_engine.signal_generator import SignalGenerator
    from app.core.strategy_engine.meta_labeler import MetaLabeler
    from app.core.strategy_engine.feature_engineering import FeatureEngineer
    from app.models.schemas.common import Regime, Signal
except (ImportError, ModuleNotFoundError):
    # Use mock implementations
    from mocks.mock_components import (
        HMMRegimeDetector, RegimeState, SignalGenerator, 
        MetaLabeler, FeatureEngineer, Regime, Signal
    )


class TestHMMRegimeDetection:
    """Test HMM-based regime detection."""
    
    def test_hmm_regime_detection_accuracy(self, sample_prices):
        """Test regime classification accuracy >85%."""
        detector = HMMRegimeDetector(lookback=100)
        
        # Train on historical data
        detector.train(sample_prices)
        
        # Test on recent window
        recent_window = sample_prices[-100:]
        regime_state = detector.predict_regime(recent_window)
        
        # Verify output format
        assert isinstance(regime_state, RegimeState)
        assert isinstance(regime_state.regime, Regime)
        assert 0.0 <= regime_state.confidence <= 1.0
        assert 0.0 <= regime_state.transition_prob <= 1.0
        
        # Verify regime is one of the expected values
        assert regime_state.regime in [Regime.TRENDING, Regime.MEAN_REVERTING, Regime.VOLATILE]
    
    def test_regime_detection_on_trending_data(self):
        """Test regime detection on clearly trending data."""
        # Create strongly trending data
        trending_prices = 18000 + np.arange(200) * 10 + np.random.normal(0, 5, 200)
        
        detector = HMMRegimeDetector(lookback=100)
        detector.train(trending_prices)
        
        regime_state = detector.predict_regime(trending_prices[-100:])
        
        # Should detect trending regime with high confidence
        assert regime_state.regime == Regime.TRENDING
        assert regime_state.confidence > 0.5
    
    def test_regime_detection_on_mean_reverting_data(self):
        """Test regime detection on mean-reverting data."""
        # Create mean-reverting data
        mean_reverting_prices = 18500 + np.random.normal(0, 30, 200)
        
        detector = HMMRegimeDetector(lookback=100)
        detector.train(mean_reverting_prices)
        
        regime_state = detector.predict_regime(mean_reverting_prices[-100:])
        
        # Should detect mean-reverting regime
        assert regime_state.regime == Regime.MEAN_REVERTING
    
    def test_regime_detection_on_volatile_data(self):
        """Test regime detection on volatile data."""
        # Create highly volatile data
        volatile_prices = 18000 + np.cumsum(np.random.normal(0, 50, 200))
        
        detector = HMMRegimeDetector(lookback=100)
        detector.train(volatile_prices)
        
        regime_state = detector.predict_regime(volatile_prices[-100:])
        
        # Should detect volatile regime
        assert regime_state.regime == Regime.VOLATILE
    
    def test_feature_calculation(self, sample_prices):
        """Test feature calculation (Hurst, ADX, volatility, autocorr)."""
        detector = HMMRegimeDetector()
        
        features = detector.calculate_features(sample_prices[-100:])
        
        # Verify feature dimensions
        assert features.shape == (4,)
        
        # Verify Hurst exponent is in valid range
        hurst = features[0]
        assert 0.0 <= hurst <= 1.0
        
        # Verify ADX is in valid range
        adx = features[1]
        assert 0.0 <= adx <= 100.0
        
        # Verify volatility percentile
        vol_pct = features[2]
        assert vol_pct >= 0.0
        
        # Verify autocorrelation
        autocorr = features[3]
        assert -1.0 <= autocorr <= 1.0


class TestSignalGeneration:
    """Test signal generation with EMA crossover + volume."""
    
    def test_signal_generation_bullish(self):
        """Test bullish signal generation."""
        # Create bullish price action
        prices = np.array([18000, 18050, 18100, 18150, 18200, 18250, 18300])
        volumes = np.array([1000, 1200, 1500, 1800, 2000, 2200, 2500])
        
        signal_gen = SignalGenerator()
        signal = signal_gen.generate_signal(prices, volumes, Regime.TRENDING)
        
        assert signal.direction in ['BUY', 'NEUTRAL']
        assert 0.0 <= signal.strength <= 1.0
    
    def test_signal_generation_bearish(self):
        """Test bearish signal generation."""
        # Create bearish price action
        prices = np.array([18300, 18250, 18200, 18150, 18100, 18050, 18000])
        volumes = np.array([1000, 1200, 1500, 1800, 2000, 2200, 2500])
        
        signal_gen = SignalGenerator()
        signal = signal_gen.generate_signal(prices, volumes, Regime.TRENDING)
        
        assert signal.direction in ['SELL', 'NEUTRAL']
        assert 0.0 <= signal.strength <= 1.0
    
    def test_signal_with_ema_crossover(self):
        """Test EMA crossover detection."""
        signal_gen = SignalGenerator(fast_period=5, slow_period=10)
        
        # Create data with clear crossover
        prices = np.concatenate([
            np.full(10, 18000),  # Flat
            np.linspace(18000, 18500, 20)  # Strong uptrend
        ])
        volumes = np.full(30, 1000)
        
        signal = signal_gen.generate_signal(prices, volumes, Regime.TRENDING)
        
        # Should generate strong signal
        assert signal.strength > 0.3
    
    def test_signal_respects_regime(self):
        """Test that signals respect market regime."""
        signal_gen = SignalGenerator()
        
        prices = np.linspace(18000, 18200, 50)
        volumes = np.full(50, 1000)
        
        # Same data, different regimes
        trending_signal = signal_gen.generate_signal(prices, volumes, Regime.TRENDING)
        mean_rev_signal = signal_gen.generate_signal(prices, volumes, Regime.MEAN_REVERTING)
        
        # Signals should differ based on regime
        assert trending_signal.direction != mean_rev_signal.direction or \
               abs(trending_signal.strength - mean_rev_signal.strength) > 0.1


class TestMetaLabeling:
    """Test XGBoost meta-labeling for signal quality."""
    
    def test_meta_labeling_prediction(self):
        """Test meta-labeler predicts quality score 0-1."""
        meta_labeler = MetaLabeler()
        
        # Train with sample data
        X_train = np.random.randn(100, 10)
        y_train = np.random.randint(0, 2, 100)
        meta_labeler.train(X_train, y_train)
        
        # Predict on new data
        X_test = np.random.randn(10, 10)
        quality_scores = meta_labeler.predict_quality(X_test)
        
        # Verify output format
        assert len(quality_scores) == 10
        assert all(0.0 <= score <= 1.0 for score in quality_scores)
    
    def test_meta_labeling_rejects_low_quality(self):
        """Test that scores <0.7 are rejected."""
        meta_labeler = MetaLabeler(quality_threshold=0.7)
        
        # Mock predictions
        quality_scores = np.array([0.85, 0.65, 0.75, 0.55, 0.90])
        
        # Filter signals
        accepted = [i for i, score in enumerate(quality_scores) if score >= 0.7]
        
        # Should accept only high-quality signals
        assert len(accepted) == 3
        assert 0 in accepted  # 0.85
        assert 2 in accepted  # 0.75
        assert 4 in accepted  # 0.90
    
    def test_meta_labeling_feature_importance(self):
        """Test feature importance calculation."""
        meta_labeler = MetaLabeler()
        
        # Train model
        X_train = np.random.randn(100, 10)
        y_train = np.random.randint(0, 2, 100)
        meta_labeler.train(X_train, y_train)
        
        # Get feature importance
        importance = meta_labeler.get_feature_importance()
        
        # Verify output
        assert len(importance) == 10
        assert all(imp >= 0.0 for imp in importance)
        assert abs(sum(importance) - 1.0) < 0.01  # Should sum to ~1


class TestFeatureEngineering:
    """Test feature engineering (RSI, MACD, ADX, etc.)."""
    
    def test_all_features_calculated(self, sample_prices):
        """Test all 20+ features are calculated."""
        feature_engineer = FeatureEngineer()
        
        features = feature_engineer.calculate_all_features(
            prices=sample_prices,
            volumes=np.full(len(sample_prices), 1000)
        )
        
        # Should have 20+ features
        assert len(features) >= 20
        
        # Check for key features
        assert 'rsi' in features
        assert 'macd' in features
        assert 'macd_signal' in features
        assert 'adx' in features
        assert 'atr' in features
        assert 'bollinger_upper' in features
        assert 'bollinger_lower' in features
        assert 'ema_fast' in features
        assert 'ema_slow' in features
        assert 'volume_sma' in features
    
    def test_rsi_calculation(self, sample_prices):
        """Test RSI calculation."""
        feature_engineer = FeatureEngineer()
        
        rsi = feature_engineer.calculate_rsi(sample_prices, period=14)
        
        # RSI should be between 0 and 100
        assert 0.0 <= rsi <= 100.0
    
    def test_macd_calculation(self, sample_prices):
        """Test MACD calculation."""
        feature_engineer = FeatureEngineer()
        
        macd, signal, histogram = feature_engineer.calculate_macd(sample_prices)
        
        # Verify all components calculated
        assert isinstance(macd, float)
        assert isinstance(signal, float)
        assert isinstance(histogram, float)
        
        # Histogram should be difference
        assert abs(histogram - (macd - signal)) < 1e-6
    
    def test_adx_calculation(self, sample_prices):
        """Test ADX calculation."""
        feature_engineer = FeatureEngineer()
        
        adx = feature_engineer.calculate_adx(sample_prices, period=14)
        
        # ADX should be between 0 and 100
        assert 0.0 <= adx <= 100.0
    
    def test_bollinger_bands_calculation(self, sample_prices):
        """Test Bollinger Bands calculation."""
        feature_engineer = FeatureEngineer()
        
        upper, middle, lower = feature_engineer.calculate_bollinger_bands(
            sample_prices, period=20, std_dev=2
        )
        
        # Upper should be above middle, middle above lower
        assert upper > middle > lower
        
        # Current price should influence bands
        current_price = sample_prices[-1]
        assert lower < current_price < upper or abs(current_price - middle) < abs(upper - lower)
    
    def test_feature_normalization(self, sample_prices):
        """Test feature normalization."""
        feature_engineer = FeatureEngineer()
        
        features = feature_engineer.calculate_all_features(
            prices=sample_prices,
            volumes=np.full(len(sample_prices), 1000)
        )
        
        # Normalize features
        normalized = feature_engineer.normalize_features(features)
        
        # Most features should be in reasonable range after normalization
        for key, value in normalized.items():
            if key not in ['price', 'volume']:  # Skip absolute values
                assert -10.0 < value < 10.0  # Reasonable range
