#!/usr/bin/env python3
"""Quick test to verify imports work."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "mocks"))

print("Testing imports...")

try:
    from mocks.mock_components import (
        Regime, Signal, RegimeState, Greeks, PortfolioGreeks,
        ActionType, ExecutionAction, HMMRegimeDetector,
        SignalGenerator, MetaLabeler, FeatureEngineer,
        PPOExecutionAgent, GreeksCalculator,
        LimitMonitor, RiskLimits, CircuitBreaker, BreachType,
        ClassicalOrderRouter, CostEstimator
    )
    print("✅ All mock imports successful!")
    
    # Test basic functionality
    print("\nTesting basic functionality...")
    
    import numpy as np
    
    # Test regime detector
    detector = HMMRegimeDetector()
    prices = np.array([18000 + i * 10 for i in range(100)])
    detector.train(prices)
    regime_state = detector.predict_regime(prices[-50:])
    print(f"✅ Regime detector works: {regime_state.regime}")
    
    # Test signal generator
    signal_gen = SignalGenerator()
    volumes = np.full(50, 1000)
    signal = signal_gen.generate_signal(prices[-50:], volumes, Regime.TRENDING)
    print(f"✅ Signal generator works: {signal.direction} ({signal.strength:.2f})")
    
    # Test PPO agent
    agent = PPOExecutionAgent()
    state = np.random.randn(9)
    action = agent.predict_action(state)
    print(f"✅ PPO agent works: {action.action_type}")
    
    # Test Greeks calculator
    calc = GreeksCalculator()
    greeks = calc.calculate_single_option(
        spot=18500.0, strike=18500.0, expiry=0.0833,
        volatility=0.18, option_type='CALL', risk_free_rate=0.06
    )
    print(f"✅ Greeks calculator works: delta={greeks.delta:.4f}")
    
    print("\n🎉 All tests passed! Mocks are working correctly.")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
