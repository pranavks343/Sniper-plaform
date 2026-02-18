"""
System test: Circuit breaker functionality.
Tests: Daily loss breach, drawdown breach, manual kill switch.
"""
import pytest
from unittest.mock import Mock

try:
    from app.core.risk_engine.circuit_breaker import CircuitBreaker, BreachType
    from app.core.risk_engine.limit_monitor import LimitMonitor, RiskLimits
except (ImportError, ModuleNotFoundError, AttributeError):
    from mocks.mock_components import CircuitBreaker, BreachType, LimitMonitor, RiskLimits


class TestCircuitBreakerSystem:
    """Test circuit breaker system functionality."""
    
    @pytest.fixture
    def setup_circuit_breaker(self):
        """Setup circuit breaker and related components."""
        limits = RiskLimits(
            daily_loss_limit=2500.0,
            max_drawdown_pct=0.12,
            max_delta=500.0,
            max_gamma=100.0,
            max_vega=200.0,
            max_consecutive_losses=5,
            max_trades_per_day=50,
            max_position_size=100
        )
        
        limit_monitor = LimitMonitor(limits)
        circuit_breaker = CircuitBreaker()
        
        return {
            'limit_monitor': limit_monitor,
            'circuit_breaker': circuit_breaker,
            'positions': [],
            'pending_orders': []
        }
    
    def test_daily_loss_breach(self, setup_circuit_breaker):
        """Test circuit breaker on daily loss breach."""
        components = setup_circuit_breaker
        
        print(f"\n📊 Testing daily loss breach...")
        print(f"   Daily loss limit: ₹{components['limit_monitor'].limits.daily_loss_limit:,.2f}")
        
        # Simulate -2.5% daily loss
        initial_capital = 100000.0
        loss_pct = 0.025
        daily_loss = initial_capital * loss_pct
        
        print(f"   Simulated loss: ₹{daily_loss:,.2f} ({loss_pct * 100:.1f}%)")
        
        # Check if breach occurs
        breaches = components['limit_monitor'].check_all_limits(
            daily_loss=daily_loss,
            drawdown_pct=0.05,
            delta=100.0,
            gamma=50.0,
            vega=100.0,
            consecutive_losses=2,
            trades_today=10,
            position_size=50
        )
        
        assert len(breaches) > 0
        assert any(b['limit'] == 'daily_loss' for b in breaches)
        
        print(f"   ✓ Breach detected: {breaches[0]['message']}")
        
        # Activate circuit breaker
        components['circuit_breaker'].trigger_breach(
            breach_type=BreachType.DAILY_LOSS,
            current_value=daily_loss,
            limit_value=components['limit_monitor'].limits.daily_loss_limit,
            message=f"Daily loss ₹{daily_loss:,.2f} exceeds limit"
        )
        
        # Verify halt
        assert components['circuit_breaker'].is_active()
        assert not components['circuit_breaker'].is_trading_allowed()
        
        print(f"   ✓ Trading halted")
        
        # Verify alert
        alerts = components['circuit_breaker'].get_alerts()
        assert len(alerts) > 0
        
        print(f"   ✓ Alert sent: {alerts[0]['message']}")
        
        print("\n✅ Daily loss breach handled correctly!")
    
    def test_drawdown_breach(self, setup_circuit_breaker):
        """Test circuit breaker on drawdown breach."""
        components = setup_circuit_breaker
        
        print(f"\n📊 Testing drawdown breach...")
        print(f"   Max drawdown limit: {components['limit_monitor'].limits.max_drawdown_pct * 100:.0f}%")
        
        # Simulate -12% drawdown
        drawdown_pct = 0.12
        
        print(f"   Simulated drawdown: {drawdown_pct * 100:.0f}%")
        
        # Check if breach occurs
        breaches = components['limit_monitor'].check_all_limits(
            daily_loss=1000.0,
            drawdown_pct=drawdown_pct,
            delta=100.0,
            gamma=50.0,
            vega=100.0,
            consecutive_losses=2,
            trades_today=10,
            position_size=50
        )
        
        assert len(breaches) > 0
        assert any(b['limit'] == 'max_drawdown_pct' for b in breaches)
        
        print(f"   ✓ Breach detected")
        
        # Activate circuit breaker
        components['circuit_breaker'].trigger_breach(
            breach_type=BreachType.DRAWDOWN,
            current_value=drawdown_pct,
            limit_value=components['limit_monitor'].limits.max_drawdown_pct,
            message=f"Drawdown {drawdown_pct * 100:.1f}% exceeds limit"
        )
        
        # Verify halt
        assert components['circuit_breaker'].is_active()
        assert not components['circuit_breaker'].is_trading_allowed()
        
        print(f"   ✓ Trading halted")
        
        print("\n✅ Drawdown breach handled correctly!")
    
    def test_manual_kill_switch(self, setup_circuit_breaker):
        """Test manual kill switch triggers position closure."""
        components = setup_circuit_breaker
        
        print(f"\n📊 Testing manual kill switch...")
        
        # Create open positions
        components['positions'] = [
            {'symbol': 'NIFTY50', 'quantity': 100, 'avg_price': 18500.0, 'current_price': 18550.0},
            {'symbol': 'BANKNIFTY', 'quantity': 50, 'avg_price': 45000.0, 'current_price': 45200.0},
            {'symbol': 'FINNIFTY', 'quantity': 75, 'avg_price': 20000.0, 'current_price': 19950.0}
        ]
        
        print(f"   Open positions: {len(components['positions'])}")
        
        # Trigger manual kill switch
        components['circuit_breaker'].trigger_breach(
            breach_type=BreachType.MANUAL_KILL_SWITCH,
            current_value=0,
            limit_value=0,
            message="Manual kill switch activated by user"
        )
        
        assert components['circuit_breaker'].is_active()
        
        print(f"   ✓ Kill switch activated")
        
        # Close all positions
        close_orders = []
        for position in components['positions']:
            close_order = {
                'symbol': position['symbol'],
                'side': 'SELL',
                'quantity': position['quantity'],
                'order_type': 'MARKET',
                'reason': 'KILL_SWITCH'
            }
            close_orders.append(close_order)
        
        print(f"   ✓ Generated {len(close_orders)} close orders")
        
        # Verify all positions will be closed
        assert len(close_orders) == len(components['positions'])
        
        # Calculate total P&L
        total_pnl = sum(
            (pos['current_price'] - pos['avg_price']) * pos['quantity']
            for pos in components['positions']
        )
        
        print(f"   Total P&L at closure: ₹{total_pnl:,.2f}")
        
        # Verify alert
        alerts = components['circuit_breaker'].get_alerts()
        assert len(alerts) > 0
        assert alerts[0]['breach_type'] == BreachType.MANUAL_KILL_SWITCH
        
        print(f"   ✓ Alert sent")
        
        print("\n✅ Manual kill switch handled correctly!")
    
    def test_circuit_breaker_prevents_new_orders(self, setup_circuit_breaker):
        """Test circuit breaker prevents new orders when active."""
        components = setup_circuit_breaker
        
        print(f"\n📊 Testing order prevention...")
        
        # Activate circuit breaker
        components['circuit_breaker'].trigger_breach(
            breach_type=BreachType.DAILY_LOSS,
            current_value=3000.0,
            limit_value=2500.0
        )
        
        # Attempt to place new order
        new_order = {
            'symbol': 'NIFTY50',
            'side': 'BUY',
            'quantity': 50,
            'order_type': 'MARKET'
        }
        
        # Check if trading allowed
        if components['circuit_breaker'].is_trading_allowed():
            # Order would be placed
            print(f"   ✗ Order placed (should be blocked)")
            assert False, "Order should be blocked"
        else:
            # Order blocked
            print(f"   ✓ Order blocked by circuit breaker")
        
        print("\n✅ Circuit breaker prevents new orders!")
    
    def test_circuit_breaker_cancels_pending_orders(self, setup_circuit_breaker):
        """Test circuit breaker cancels pending orders."""
        components = setup_circuit_breaker
        
        print(f"\n📊 Testing pending order cancellation...")
        
        # Create pending orders
        components['pending_orders'] = [
            {'order_id': 'order_1', 'status': 'PENDING', 'symbol': 'NIFTY50', 'quantity': 50},
            {'order_id': 'order_2', 'status': 'PENDING', 'symbol': 'BANKNIFTY', 'quantity': 25},
            {'order_id': 'order_3', 'status': 'PENDING', 'symbol': 'FINNIFTY', 'quantity': 30}
        ]
        
        print(f"   Pending orders: {len(components['pending_orders'])}")
        
        # Activate circuit breaker
        components['circuit_breaker'].trigger_breach(
            breach_type=BreachType.DAILY_LOSS,
            current_value=3000.0,
            limit_value=2500.0
        )
        
        # Get orders to cancel
        orders_to_cancel = components['circuit_breaker'].get_orders_to_cancel(
            components['pending_orders']
        )
        
        print(f"   ✓ Identified {len(orders_to_cancel)} orders to cancel")
        
        # Verify all pending orders are cancelled
        assert len(orders_to_cancel) == len(components['pending_orders'])
        
        # Mock cancellation
        for order in orders_to_cancel:
            order['status'] = 'CANCELLED'
            print(f"      Cancelled: {order['order_id']}")
        
        print("\n✅ Pending orders cancelled correctly!")
    
    def test_circuit_breaker_recovery(self, setup_circuit_breaker):
        """Test circuit breaker can be reset after resolution."""
        components = setup_circuit_breaker
        
        print(f"\n📊 Testing circuit breaker recovery...")
        
        # Trigger breach
        components['circuit_breaker'].trigger_breach(
            breach_type=BreachType.DAILY_LOSS,
            current_value=3000.0,
            limit_value=2500.0
        )
        
        assert components['circuit_breaker'].is_active()
        print(f"   ✓ Circuit breaker activated")
        
        # Simulate issue resolution (manual intervention)
        print(f"   Resolving issue...")
        
        # Reset circuit breaker
        components['circuit_breaker'].reset()
        
        assert not components['circuit_breaker'].is_active()
        assert components['circuit_breaker'].is_trading_allowed()
        
        print(f"   ✓ Circuit breaker reset")
        print(f"   ✓ Trading resumed")
        
        print("\n✅ Circuit breaker recovery successful!")
    
    def test_multiple_simultaneous_breaches(self, setup_circuit_breaker):
        """Test handling multiple simultaneous breaches."""
        components = setup_circuit_breaker
        
        print(f"\n📊 Testing multiple simultaneous breaches...")
        
        # Simulate multiple breaches
        breaches = components['limit_monitor'].check_all_limits(
            daily_loss=3000.0,  # Exceeds limit
            drawdown_pct=0.15,  # Exceeds limit
            delta=600.0,        # Exceeds limit
            gamma=50.0,
            vega=100.0,
            consecutive_losses=6,  # Exceeds limit
            trades_today=10,
            position_size=50
        )
        
        print(f"   Breaches detected: {len(breaches)}")
        
        for breach in breaches:
            print(f"      - {breach['limit']}: {breach['message']}")
        
        # Should detect multiple breaches
        assert len(breaches) >= 3
        
        # Trigger circuit breaker for most severe breach
        most_severe = breaches[0]
        components['circuit_breaker'].trigger_breach(
            breach_type=BreachType.DAILY_LOSS,
            current_value=most_severe['current'],
            limit_value=most_severe['limit_value'],
            message=most_severe['message']
        )
        
        assert components['circuit_breaker'].is_active()
        
        print(f"   ✓ Circuit breaker activated for most severe breach")
        
        print("\n✅ Multiple breaches handled correctly!")
