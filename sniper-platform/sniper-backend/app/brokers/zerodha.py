from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from app.brokers.base import BaseBroker


class ZerodhaBroker(BaseBroker):
    def __init__(self) -> None:
        self.connected = False
        self.orders: dict[str, dict] = {}
        self.positions: dict[str, dict] = {}

    def connect(self, credentials: dict) -> None:
        self.connected = bool(credentials.get('api_key') and credentials.get('api_secret'))

    def place_order(self, symbol: str, quantity: int, order_type: str, price: float | None = None, side: str = 'BUY') -> dict:
        if not self.connected:
            raise RuntimeError('Zerodha broker not connected')
        order_id = str(uuid4())
        order = {
            'id': order_id,
            'symbol': symbol,
            'quantity': quantity,
            'order_type': order_type,
            'price': price,
            'side': side,
            'status': 'PENDING',
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
        _ = symbols
        _ = callback

    def get_historical_data(self, symbol: str, start: datetime, end: datetime, interval: str) -> list[dict]:
        _ = symbol
        _ = start
        _ = end
        _ = interval
        return []
