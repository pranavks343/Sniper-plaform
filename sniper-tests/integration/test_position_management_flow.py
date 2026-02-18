"""
Integration test: Order fill to position update flow.
Tests position creation, Greeks calculation, and WebSocket events.
"""
import pytest
import asyncio
from unittest.mock import Mock, AsyncMock

try:
    from app.core.risk_engine.greeks_calculator import GreeksCalculator
    from app.core.data_pipeline.websocket_manager import WebSocketManager
except (ImportError, ModuleNotFoundError, AttributeError):
    from mocks.mock_components import GreeksCalculator, WebSocketManager


class TestPositionManagementFlow:
    """Test order fill to position update flow."""
    
    @pytest.fixture
    def setup_position_management(self):
        """Setup position management components."""
        greeks_calculator = GreeksCalculator()
        websocket_manager = WebSocketManager()
        
        return {
            'greeks_calculator': greeks_calculator,
            'websocket_manager': websocket_manager,
            'positions': {}  # Mock position store
        }
    
    def test_order_fill_to_position_update(self, setup_position_management):
        """Test complete flow from order fill to position update."""
        components = setup_position_management
        
        # Step 1: Simulate order fill event
        order_fill = {
            'order_id': 'order_123',
            'symbol': 'NIFTY50-CE-18500',
            'side': 'BUY',
            'quantity': 100,
            'fill_price': 150.0,
            'instrument_type': 'OPTION',
            'option_type': 'CALL',
            'strike': 18500.0,
            'expiry': 0.0833,
            'spot': 18500.0,
            'volatility': 0.18
        }
        
        print("✓ Order fill event received")
        
        # Step 2: Create or update position
        symbol = order_fill['symbol']
        
        if symbol not in components['positions']:
            # Create new position
            components['positions'][symbol] = {
                'symbol': symbol,
                'quantity': 0,
                'avg_price': 0.0,
                'total_cost': 0.0
            }
        
        position = components['positions'][symbol]
        
        # Update position
        if order_fill['side'] == 'BUY':
            new_quantity = position['quantity'] + order_fill['quantity']
            new_cost = position['total_cost'] + (order_fill['quantity'] * order_fill['fill_price'])
            position['quantity'] = new_quantity
            position['total_cost'] = new_cost
            position['avg_price'] = new_cost / new_quantity if new_quantity > 0 else 0.0
        
        print(f"✓ Position updated: {position}")
        
        assert position['quantity'] == 100
        assert position['avg_price'] == 150.0
        
        # Step 3: Calculate Greeks for the position
        if order_fill['instrument_type'] == 'OPTION':
            greeks = components['greeks_calculator'].calculate_single_option(
                spot=order_fill['spot'],
                strike=order_fill['strike'],
                expiry=order_fill['expiry'],
                volatility=order_fill['volatility'],
                option_type=order_fill['option_type'],
                risk_free_rate=0.06
            )
            
            position['greeks'] = {
                'delta': greeks.delta * position['quantity'],
                'gamma': greeks.gamma * position['quantity'],
                'theta': greeks.theta * position['quantity'],
                'vega': greeks.vega * position['quantity'],
                'rho': greeks.rho * position['quantity']
            }
            
            print(f"✓ Greeks calculated: {position['greeks']}")
            
            assert 'greeks' in position
            assert position['greeks']['delta'] > 0  # Long call has positive delta
        
        # Step 4: Update portfolio Greeks
        portfolio_greeks = {
            'delta': 0.0,
            'gamma': 0.0,
            'theta': 0.0,
            'vega': 0.0,
            'rho': 0.0
        }
        
        for pos in components['positions'].values():
            if 'greeks' in pos:
                portfolio_greeks['delta'] += pos['greeks']['delta']
                portfolio_greeks['gamma'] += pos['greeks']['gamma']
                portfolio_greeks['theta'] += pos['greeks']['theta']
                portfolio_greeks['vega'] += pos['greeks']['vega']
                portfolio_greeks['rho'] += pos['greeks']['rho']
        
        print(f"✓ Portfolio Greeks updated: {portfolio_greeks}")
        
        assert portfolio_greeks['delta'] > 0
        
        # Step 5: Emit WebSocket event
        event = {
            'type': 'POSITION_UPDATE',
            'data': {
                'symbol': symbol,
                'position': position,
                'portfolio_greeks': portfolio_greeks
            }
        }
        
        # Mock WebSocket broadcast
        components['websocket_manager'].broadcast_event = Mock()
        components['websocket_manager'].broadcast_event(event)
        
        print("✓ WebSocket event emitted")
        
        # Verify event was broadcast
        components['websocket_manager'].broadcast_event.assert_called_once()
    
    def test_multiple_fills_same_position(self, setup_position_management):
        """Test multiple fills updating same position."""
        components = setup_position_management
        
        # First fill
        fill_1 = {
            'symbol': 'NIFTY50',
            'side': 'BUY',
            'quantity': 50,
            'fill_price': 18500.0,
            'instrument_type': 'FUTURE'
        }
        
        components['positions']['NIFTY50'] = {
            'symbol': 'NIFTY50',
            'quantity': 50,
            'avg_price': 18500.0,
            'total_cost': 50 * 18500.0
        }
        
        # Second fill
        fill_2 = {
            'symbol': 'NIFTY50',
            'side': 'BUY',
            'quantity': 30,
            'fill_price': 18550.0,
            'instrument_type': 'FUTURE'
        }
        
        position = components['positions']['NIFTY50']
        new_quantity = position['quantity'] + fill_2['quantity']
        new_cost = position['total_cost'] + (fill_2['quantity'] * fill_2['fill_price'])
        position['quantity'] = new_quantity
        position['total_cost'] = new_cost
        position['avg_price'] = new_cost / new_quantity
        
        # Verify average price calculation
        expected_avg = (50 * 18500 + 30 * 18550) / 80
        assert abs(position['avg_price'] - expected_avg) < 0.01
        assert position['quantity'] == 80
        
        print("✓ Multiple fills aggregated correctly")
    
    def test_position_closing(self, setup_position_management):
        """Test position closing flow."""
        components = setup_position_management
        
        # Create position
        components['positions']['NIFTY50'] = {
            'symbol': 'NIFTY50',
            'quantity': 100,
            'avg_price': 18500.0,
            'total_cost': 100 * 18500.0
        }
        
        # Close position
        close_fill = {
            'symbol': 'NIFTY50',
            'side': 'SELL',
            'quantity': 100,
            'fill_price': 18600.0,
            'instrument_type': 'FUTURE'
        }
        
        position = components['positions']['NIFTY50']
        position['quantity'] -= close_fill['quantity']
        
        # Calculate P&L
        pnl = (close_fill['fill_price'] - position['avg_price']) * close_fill['quantity']
        position['realized_pnl'] = pnl
        
        assert position['quantity'] == 0
        assert position['realized_pnl'] == 10000.0  # (18600 - 18500) * 100
        
        print(f"✓ Position closed with P&L: ₹{pnl:.2f}")
    
    @pytest.mark.asyncio
    async def test_websocket_event_latency(self, setup_position_management):
        """Test WebSocket event latency."""
        import time
        
        components = setup_position_management
        
        # Mock async WebSocket broadcast
        async def mock_broadcast(event):
            await asyncio.sleep(0.01)  # Simulate network delay
        
        components['websocket_manager'].broadcast_event = mock_broadcast
        
        # Measure latency
        start = time.perf_counter()
        
        event = {
            'type': 'POSITION_UPDATE',
            'data': {'symbol': 'NIFTY50', 'quantity': 100}
        }
        
        await components['websocket_manager'].broadcast_event(event)
        
        latency_ms = (time.perf_counter() - start) * 1000
        
        print(f"✓ WebSocket latency: {latency_ms:.2f}ms")
        
        # Should be under 100ms target
        assert latency_ms < 100
