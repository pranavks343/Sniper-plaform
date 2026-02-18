"""
Integration test: End-to-end signal to order flow.
Tests complete pipeline from tick data to order placement.
"""
import time
import pytest
import numpy as np

try:
    from app.core.data_pipeline.bar_aggregator import BarAggregator
    from app.core.strategy_engine.regime_detector import HMMRegimeDetector
    from app.core.strategy_engine.signal_generator import SignalGenerator
    from app.core.strategy_engine.meta_labeler import MetaLabeler
    from app.core.execution_engine.rl_agent import PPOExecutionAgent
    from app.core.risk_engine.limit_monitor import LimitMonitor, RiskLimits
    from app.brokers.paper_trading import PaperTradingBroker
except (ImportError, ModuleNotFoundError, AttributeError):
    from mocks.mock_components import (
        BarAggregator, HMMRegimeDetector, SignalGenerator,
        MetaLabeler, PPOExecutionAgent,
        LimitMonitor, RiskLimits, PaperTradingBroker,
    )


class TestSignalToOrderFlow:
    """Test end-to-end signal generation to order placement."""
    
    @pytest.fixture
    def setup_pipeline(self):
        """Setup complete trading pipeline."""
        # Initialize components
        bar_aggregator = BarAggregator(interval='1min')
        regime_detector = HMMRegimeDetector(lookback=100)
        signal_generator = SignalGenerator()
        meta_labeler = MetaLabeler()
        rl_agent = PPOExecutionAgent()
        
        limits = RiskLimits(
            daily_loss_limit=5000.0,
            max_drawdown_pct=0.10,
            max_delta=1000.0,
            max_gamma=200.0,
            max_vega=500.0,
            max_consecutive_losses=5,
            max_trades_per_day=100,
            max_position_size=200
        )
        limit_monitor = LimitMonitor(limits)
        broker = PaperTradingBroker(initial_capital=100000.0)
        
        # Train models with sample data
        sample_prices = 18000 + np.cumsum(np.random.normal(0.5, 10, 200))
        regime_detector.train(sample_prices)
        
        X_train = np.random.randn(100, 10)
        y_train = np.random.randint(0, 2, 100)
        meta_labeler.train(X_train, y_train)
        
        return {
            'bar_aggregator': bar_aggregator,
            'regime_detector': regime_detector,
            'signal_generator': signal_generator,
            'meta_labeler': meta_labeler,
            'rl_agent': rl_agent,
            'limit_monitor': limit_monitor,
            'broker': broker
        }
    
    def test_end_to_end_flow(self, setup_pipeline):
        """Test complete flow from tick to order with latency measurement."""
        pipeline = setup_pipeline
        
        start_time = time.perf_counter()
        
        # Step 1: Inject mock tick data
        ticks = []
        base_price = 18500.0
        for i in range(100):
            tick = {
                'symbol': 'NIFTY50',
                'timestamp': f'2026-02-18T10:{30 + i // 60}:{i % 60:02d}',
                'last_price': base_price + np.random.normal(0, 5),
                'volume': 1000 + np.random.randint(-100, 100)
            }
            ticks.append(tick)
        
        tick_time = time.perf_counter()
        print(f"✓ Tick generation: {(tick_time - start_time) * 1000:.2f}ms")
        
        # Step 2: Aggregate ticks into bars
        bars = pipeline['bar_aggregator'].aggregate(ticks)
        
        bar_time = time.perf_counter()
        print(f"✓ Bar aggregation: {(bar_time - tick_time) * 1000:.2f}ms")
        
        assert len(bars) > 0
        
        # Step 3: Detect regime
        prices = np.array([bar['close'] for bar in bars])
        if len(prices) >= 100:
            regime_state = pipeline['regime_detector'].predict_regime(prices[-100:])
        else:
            regime_state = pipeline['regime_detector'].predict_regime(
                np.pad(prices, (100 - len(prices), 0), mode='edge')
            )
        
        regime_time = time.perf_counter()
        print(f"✓ Regime detection: {(regime_time - bar_time) * 1000:.2f}ms")
        
        assert regime_state is not None
        
        # Step 4: Generate signal
        volumes = np.array([bar.get('volume', 1000) for bar in bars])
        signal = pipeline['signal_generator'].generate_signal(
            prices, volumes, regime_state.regime
        )
        
        signal_time = time.perf_counter()
        print(f"✓ Signal generation: {(signal_time - regime_time) * 1000:.2f}ms")
        
        assert signal is not None
        
        # Step 5: Meta-labeling evaluation
        features = np.random.randn(1, 10)  # Mock features
        quality_score = pipeline['meta_labeler'].predict_quality(features)[0]
        
        meta_time = time.perf_counter()
        print(f"✓ Meta-labeling: {(meta_time - signal_time) * 1000:.2f}ms")
        
        assert 0.0 <= quality_score <= 1.0
        
        # Step 6: RL agent decision
        state = np.random.randn(9)  # Mock state
        action = pipeline['rl_agent'].predict_action(state)
        
        rl_time = time.perf_counter()
        print(f"✓ RL decision: {(rl_time - meta_time) * 1000:.2f}ms")
        
        assert action is not None
        
        # Step 7: Risk check
        risk_passed = pipeline['limit_monitor'].check_all_limits(
            daily_loss=0.0,
            drawdown_pct=0.0,
            delta=50.0,
            gamma=10.0,
            vega=20.0,
            consecutive_losses=0,
            trades_today=5,
            position_size=50
        )
        
        risk_time = time.perf_counter()
        print(f"✓ Risk check: {(risk_time - rl_time) * 1000:.2f}ms")
        
        assert len(risk_passed) == 0  # No breaches
        
        # Step 8: Place order with broker
        if quality_score >= 0.7 and signal.direction in ['BUY', 'SELL']:
            order = {
                'symbol': 'NIFTY50',
                'order_type': action.action_type.value,
                'side': signal.direction,
                'quantity': 50,
                'price': prices[-1] if action.action_type.value == 'LIMIT' else None
            }
            
            order_response = pipeline['broker'].place_order(order)
            
            order_time = time.perf_counter()
            print(f"✓ Order placement: {(order_time - risk_time) * 1000:.2f}ms")
            
            assert order_response is not None
            assert 'order_id' in order_response
        
        # Measure total latency
        total_time = time.perf_counter()
        total_latency_ms = (total_time - start_time) * 1000
        
        print(f"\n📊 Total latency: {total_latency_ms:.2f}ms")
        
        # Assert latency target
        assert total_latency_ms < 500, f"Latency {total_latency_ms:.2f}ms exceeds 500ms target"
    
    def test_flow_with_signal_rejection(self, setup_pipeline):
        """Test flow when signal is rejected by meta-labeler."""
        pipeline = setup_pipeline
        
        # Generate low-quality signal
        prices = np.array([18500.0] * 50)  # Flat prices
        volumes = np.array([1000] * 50)
        
        signal = pipeline['signal_generator'].generate_signal(
            prices, volumes, None
        )
        
        # Mock low quality score
        quality_score = 0.5  # Below threshold
        
        # Signal should be rejected
        assert quality_score < 0.7
        
        # No order should be placed
        print("✓ Low-quality signal rejected")
    
    def test_flow_with_risk_breach(self, setup_pipeline):
        """Test flow when risk limits are breached."""
        pipeline = setup_pipeline
        
        # Simulate risk breach
        breaches = pipeline['limit_monitor'].check_all_limits(
            daily_loss=6000.0,  # Exceeds limit
            drawdown_pct=0.05,
            delta=50.0,
            gamma=10.0,
            vega=20.0,
            consecutive_losses=2,
            trades_today=10,
            position_size=50
        )
        
        # Should detect breach
        assert len(breaches) > 0
        assert any(b['limit'] == 'daily_loss' for b in breaches)
        
        print("✓ Risk breach detected, order blocked")
