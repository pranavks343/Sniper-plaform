"""In-memory paper trading broker for backtesting and development."""
from __future__ import annotations

import random
import time
from datetime import datetime
from uuid import uuid4

from sniper.brokers.base import BaseBroker


class PaperTradingBroker(BaseBroker):
    def __init__(self, starting_capital: float = 1_000_000.0) -> None:
        self.connected = False
        self.cash = starting_capital
        self.orders: dict[str, dict] = {}
        self.positions: dict[str, dict] = {}

    def connect(self, credentials: dict) -> None:
        _ = credentials
        self.connected = True

    def place_order(
        self,
        symbol: str,
        quantity: int,
        order_type: str,
        price: float | None = None,
        side: str = "BUY",
    ) -> dict:
        if not self.connected:
            raise RuntimeError("paper broker not connected")

        order_id = str(uuid4())
        latency = random.uniform(0.05, 0.2)
        time.sleep(latency)

        fill_price = float(price or 0.0)
        if order_type.upper() == "MARKET":
            fill_price = fill_price * (
                1 + random.uniform(0.0, 0.0005)
                if side == "BUY"
                else 1 - random.uniform(0.0, 0.0005)
            )

        order = {
            "id": order_id,
            "symbol": symbol,
            "quantity": quantity,
            "order_type": order_type,
            "side": side,
            "price": price,
            "status": "COMPLETE",
            "filled_qty": quantity,
            "avg_price": fill_price,
            "timestamp": datetime.utcnow().isoformat(),
        }
        self.orders[order_id] = order

        signed_qty = quantity if side == "BUY" else -quantity
        pos = self.positions.setdefault(
            symbol,
            {
                "symbol": symbol,
                "quantity": 0,
                "avg_price": 0.0,
                "current_price": fill_price,
                "pnl": 0.0,
            },
        )
        old_qty = int(pos["quantity"])
        old_avg = float(pos["avg_price"])
        new_qty = old_qty + signed_qty

        if old_qty == 0 or (old_qty > 0 and signed_qty > 0) or (old_qty < 0 and signed_qty < 0):
            total_abs = abs(old_qty) + abs(signed_qty)
            pos["avg_price"] = (
                (old_avg * abs(old_qty)) + (fill_price * abs(signed_qty))
            ) / max(total_abs, 1)
        else:
            if abs(signed_qty) > abs(old_qty):
                pos["avg_price"] = fill_price
            elif abs(signed_qty) == abs(old_qty):
                self.positions.pop(symbol, None)
                return order

        pos["quantity"] = new_qty
        pos["current_price"] = fill_price
        pos["pnl"] = (pos["current_price"] - pos["avg_price"]) * pos["quantity"]
        if pos["quantity"] == 0:
            self.positions.pop(symbol, None)
        return order

    def modify_order(
        self,
        order_id: str,
        quantity: int | None = None,
        price: float | None = None,
    ) -> dict:
        order = self.orders[order_id]
        if quantity is not None:
            order["quantity"] = quantity
        if price is not None:
            order["price"] = price
        return order

    def cancel_order(self, order_id: str) -> dict:
        order = self.orders[order_id]
        order["status"] = "CANCELLED"
        return order

    def get_order_status(self, order_id: str) -> dict:
        return self.orders[order_id]

    def get_positions(self) -> list[dict]:
        return [pos for pos in self.positions.values() if int(pos.get("quantity", 0)) != 0]

    def get_holdings(self) -> list[dict]:
        return []

    def get_margins(self) -> dict:
        return {"available": self.cash, "utilized": 0.0}

    def subscribe_market_data(
        self, symbols: list[str], callback: Callable[[dict], None]
    ) -> None:
        for symbol in symbols:
            callback({"symbol": symbol, "ltp": 100.0})

    def get_historical_data(
        self,
        symbol: str,
        start: datetime,
        end: datetime,
        interval: str,
    ) -> list[dict]:
        _ = symbol
        _ = start
        _ = end
        _ = interval
        return []
