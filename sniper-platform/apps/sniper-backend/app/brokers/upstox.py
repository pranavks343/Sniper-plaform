from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from app.brokers.base import BaseBroker


class UpstoxBroker(BaseBroker):
    """Minimal Upstox broker adapter scaffold.

    This keeps a local order/position view and validates credentials so the
    execution layer can run with a real broker mode selected.
    """

    def __init__(self) -> None:
        self.connected = False
        self.orders: dict[str, dict] = {}
        self.positions: dict[str, dict] = {}
        self.access_token: str | None = None

    def connect(self, credentials: dict) -> None:
        api_key = credentials.get('api_key')
        api_secret = credentials.get('api_secret')
        self.access_token = credentials.get('access_token')
        # Real Upstox API calls are not hardwired in this scaffold yet.
        self.connected = bool(api_key and api_secret)

    def place_order(self, symbol: str, quantity: int, order_type: str, price: float | None = None, side: str = 'BUY') -> dict:
        if not self.connected:
            raise RuntimeError('Upstox broker not connected')

        order_id = str(uuid4())
        order = {
            'id': order_id,
            'symbol': symbol,
            'quantity': quantity,
            'order_type': order_type,
            'price': price,
            'side': side,
            'status': 'PENDING',
            'filled_qty': 0,
            'avg_price': None,
            'timestamp': datetime.utcnow().isoformat(),
        }
        self.orders[order_id] = order
        return order

    def modify_order(self, order_id: str, quantity: int | None = None, price: float | None = None) -> dict:
        order = self.orders[order_id]
        if quantity is not None:
            order['quantity'] = quantity
        if price is not None:
            order['price'] = price
        return order

    def cancel_order(self, order_id: str) -> dict:
        self.orders[order_id]['status'] = 'CANCELLED'
        return self.orders[order_id]

    def get_order_status(self, order_id: str) -> dict:
        return self.orders[order_id]

    def get_positions(self) -> list[dict]:
        return list(self.positions.values())

    def get_holdings(self) -> list[dict]:
        return []

    def get_margins(self) -> dict:
        return {'available': 0.0, 'utilized': 0.0}

    def subscribe_market_data(self, symbols: list[str], callback) -> None:
        for symbol in symbols:
            callback({'symbol': symbol, 'ltp': 100.0})

    def get_historical_data(self, symbol: str, start: datetime, end: datetime, interval: str) -> list[dict]:
        _ = symbol
        _ = start
        _ = end
        _ = interval
        return []
