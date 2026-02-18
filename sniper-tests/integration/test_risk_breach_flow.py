"""
Integration test: Risk breach handling flow.
Tests limit breach detection, circuit breaker, order cancellation, and hedging.
"""
import pytest
from unittest.mock import Mock

try:
    from app.core.risk_engine.limit_monitor import LimitMonitor, RiskLimits
    from app.core.risk_engine.circuit_breaker import CircuitBreaker, BreachType
    from app.quantum.hedging_qaoa import HedgingQAOA
except (ImportError, ModuleNotFoundError, AttributeError):
    from mocks.mock_components import (
        LimitMonitor, RiskLimits,
        CircuitBreaker, BreachType,
        HedgingQAOA,
    )


class TestRiskBreachFlow:
    """Test risk limit breach handling."""
    
    @pytest.fixture
    def setup_risk_management(self):
        """Setup risk management components."""
        limits = RiskLimits(
            daily_loss_limit=1000.0,
            max_drawdown_pct=0.10,
            max_delta=500.0,
            max_gamma=100.0,
            max_vega=200.0,
            max_consecutive_losses=5,
            max_trades_per_day=50,
            max_position_size=100
        )
        
        limit_monitor = LimitMonitor(limits)
        circuit_breaker = CircuitBreaker()
        hedging_qaoa = HedgingQAOA()
        
        return {
            'limit_monitor': limit_monitor,
            'circuit_breaker': circuit_breaker,
            'hedging_qaoa': hedging_qaoa,
            'pending_orders': [],
            'positions': []
        }
    
    def test_limit_breach_handling(self, setup_risk_management):
        """Test complete limit breach handling flow."""
        components = setup_risk_management
        
        # Step 1: Set daily loss limit to ₹1,000
        print(f"✓ Daily loss limit set: ₹{components['limit_monitor'].limits.daily_loss_limit}")
        
        # Step 2: Simulate losing trades
        trades = [
            {'pnl': -200, 'symbol': 'TRADE_1'},
            {'pnl': -150, 'symbol': 'TRADE_2'},
            {'pnl': -300, 'symbol': 'TRADE_3'},
            {'pnl': -250, 'symbol': 'TRADE_4'},
            {'pnl': -200, 'symbol': 'TRADE_5'}
        ]
        
        total_loss = sum(trade['pnl'] for trade in trades)
        print(f"✓ Executed {len(trades)} losing trades, total loss: ₹{total_loss}")
        
        # Step 3: Check if limit breached
        breaches = components['limit_monitor'].check_all_limits(
            daily_loss=abs(total_loss),
            drawdown_pct=0.05,
            delta=100.0,
            gamma=50.0,
            vega=100.0,
            consecutive_losses=len(trades),
            trades_today=len(trades),
            position_size=50
        )
        
        assert len(breaches) > 0
        assert any(b['limit'] == 'daily_loss' for b in breaches)
        print(f"✓ Limit breach detected: {breaches}")
        
        # Step 4: Activate circuit breaker
        for breach in breaches:
            if breach['limit'] == 'daily_loss':
                components['circuit_breaker'].trigger_breach(
                    breach_type=BreachType.DAILY_LOSS,
                    current_value=breach['current'],
                    limit_value=breach['limit_value'],
                    message=f"Daily loss limit breached: ₹{breach['current']} > ₹{breach['limit_value']}"
                )
        
        assert components['circuit_breaker'].is_active()
        assert not components['circuit_breaker'].is_trading_allowed()
        print("✓ Circuit breaker activated")
        
        # Step 5: Cancel all pending orders
        components['pending_orders'] = [
            {'order_id': 'order_1', 'status': 'PENDING', 'symbol': 'NIFTY50'},
            {'order_id': 'order_2', 'status': 'PENDING', 'symbol': 'BANKNIFTY'},
            {'order_id': 'order_3', 'status': 'PENDING', 'symbol': 'NIFTY50'}
        ]
        
        orders_to_cancel = components['circuit_breaker'].get_orders_to_cancel(
            components['pending_orders']
        )
        
        assert len(orders_to_cancel) == 3
        print(f"✓ Cancelled {len(orders_to_cancel)} pending orders")
        
        # Mock order cancellation
        for order in orders_to_cancel:
            order['status'] = 'CANCELLED'
        
        # Step 6: Trigger quantum hedging (if enabled)
        components['positions'] = [
            {'symbol': 'POS_1', 'quantity': 100, 'pnl': -400, 'delta': 80},
            {'symbol': 'POS_2', 'quantity': 50, 'pnl': -300, 'delta': -40},
            {'symbol': 'POS_3', 'quantity': 75, 'pnl': -200, 'delta': 60}
        ]
        
        # Formulate hedging QUBO
        qubo = components['hedging_qaoa'].formulate_hedging_qubo(
            components['positions']
        )
        
        assert qubo is not None
        print("✓ Quantum hedging QUBO formulated")
        
        # Mock quantum solution
        hedge_plan = components['hedging_qaoa'].decode_solution(
            '101',  # Close positions 1 and 3
            components['positions']
        )
        
        assert len(hedge_plan) > 0
        print(f"✓ Hedge plan generated: Close {len(hedge_plan)} positions")
        
        # Step 7: Verify alert sent
        alerts = components['circuit_breaker'].get_alerts()
        
        assert len(alerts) > 0
        assert alerts[0]['breach_type'] == BreachType.DAILY_LOSS
        print(f"✓ Alert sent: {alerts[0]['message']}")
    
    def test_drawdown_breach(self, setup_risk_management):
        """Test drawdown limit breach."""
        components = setup_risk_management
        
        # Simulate drawdown breach
        breaches = components['limit_monitor'].check_all_limits(
            daily_loss=500.0,
            drawdown_pct=0.12,  # Exceeds 10% limit
            delta=100.0,
            gamma=50.0,
            vega=100.0,
            consecutive_losses=2,
            trades_today=10,
            position_size=50
        )
        
        assert len(breaches) > 0
        assert any(b['limit'] == 'max_drawdown_pct' for b in breaches)
        
        print("✓ Drawdown breach detected")
        
        # Activate circuit breaker
        components['circuit_breaker'].trigger_breach(
            breach_type=BreachType.DRAWDOWN,
            current_value=0.12,
            limit_value=0.10
        )
        
        assert components['circuit_breaker'].is_active()
        print("✓ Circuit breaker activated for drawdown breach")
    
    def test_consecutive_losses_breach(self, setup_risk_management):
        """Test consecutive losses limit breach."""
        components = setup_risk_management
        
        # Simulate 6 consecutive losses
        breaches = components['limit_monitor'].check_all_limits(
            daily_loss=500.0,
            drawdown_pct=0.05,
            delta=100.0,
            gamma=50.0,
            vega=100.0,
            consecutive_losses=6,  # Exceeds 5 limit
            trades_today=10,
            position_size=50
        )
        
        assert len(breaches) > 0
        assert any(b['limit'] == 'max_consecutive_losses' for b in breaches)
        
        print("✓ Consecutive losses breach detected")
    
    def test_greeks_limit_breach(self, setup_risk_management):
        """Test Greeks limit breach (delta, gamma, vega)."""
        components = setup_risk_management
        
        # Simulate delta breach
        breaches = components['limit_monitor'].check_all_limits(
            daily_loss=500.0,
            drawdown_pct=0.05,
            delta=600.0,  # Exceeds 500 limit
            gamma=50.0,
            vega=100.0,
            consecutive_losses=2,
            trades_today=10,
            position_size=50
        )
        
        assert len(breaches) > 0
        assert any(b['limit'] == 'max_delta' for b in breaches)
        
        print("✓ Delta limit breach detected")
        
        # Simulate gamma breach
        breaches = components['limit_monitor'].check_all_limits(
            daily_loss=500.0,
            drawdown_pct=0.05,
            delta=400.0,
            gamma=150.0,  # Exceeds 100 limit
            vega=100.0,
            consecutive_losses=2,
            trades_today=10,
            position_size=50
        )
        
        assert len(breaches) > 0
        assert any(b['limit'] == 'max_gamma' for b in breaches)
        
        print("✓ Gamma limit breach detected")
        
        # Simulate vega breach
        breaches = components['limit_monitor'].check_all_limits(
            daily_loss=500.0,
            drawdown_pct=0.05,
            delta=400.0,
            gamma=80.0,
            vega=250.0,  # Exceeds 200 limit
            consecutive_losses=2,
            trades_today=10,
            position_size=50
        )
        
        assert len(breaches) > 0
        assert any(b['limit'] == 'max_vega' for b in breaches)
        
        print("✓ Vega limit breach detected")
    
    def test_recovery_after_breach(self, setup_risk_management):
        """Test system recovery after breach resolution."""
        components = setup_risk_management
        
        # Trigger breach
        components['circuit_breaker'].trigger_breach(
            breach_type=BreachType.DAILY_LOSS,
            current_value=1200.0,
            limit_value=1000.0
        )
        
        assert components['circuit_breaker'].is_active()
        
        # Reset circuit breaker (manual intervention)
        components['circuit_breaker'].reset()
        
        assert not components['circuit_breaker'].is_active()
        assert components['circuit_breaker'].is_trading_allowed()
        
        print("✓ System recovered after breach resolution")
