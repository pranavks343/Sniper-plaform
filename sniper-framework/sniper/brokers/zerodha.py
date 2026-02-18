"""
Zerodha Kite Connect Broker Adapter
Implements BaseBroker against the official kiteconnect Python SDK.

Requires: pip install kiteconnect
"""
from __future__ import annotations

import logging
from typing import Any

from sniper.brokers.base import BaseBroker

logger = logging.getLogger("sniper.brokers.zerodha")


class ZerodhaBroker(BaseBroker):
    """
    Zerodha Kite Connect adapter.

    credentials dict keys:
        api_key:      Kite API key
        access_token: Session access token (refresh daily)
    """

    def connect(self, credentials: dict) -> None:
        try:
            from kiteconnect import KiteConnect  # type: ignore

            self._kite = KiteConnect(api_key=credentials["api_key"])
            self._kite.set_access_token(credentials["access_token"])
            profile = self._kite.profile()
            logger.info("Zerodha connected — user: %s", profile.get("user_id", "?"))
        except ImportError:
            raise RuntimeError("kiteconnect not installed. pip install kiteconnect")

    def place_order(
        self,
        symbol: str,
        quantity: int,
        order_type: str,
        price: float,
        side: str,
    ) -> str:
        variety = self._kite.VARIETY_REGULAR
        exchange = "NSE"
        kite_side = self._kite.TRANSACTION_TYPE_BUY if side.upper() == "BUY" else self._kite.TRANSACTION_TYPE_SELL
        kite_type = self._kite.ORDER_TYPE_MARKET if order_type.upper() == "MARKET" else self._kite.ORDER_TYPE_LIMIT

        order_id = self._kite.place_order(
            variety=variety,
            exchange=exchange,
            tradingsymbol=symbol,
            transaction_type=kite_side,
            quantity=quantity,
            product=self._kite.PRODUCT_MIS,
            order_type=kite_type,
            price=price if kite_type == self._kite.ORDER_TYPE_LIMIT else None,
        )
        logger.info("Zerodha order placed: %s — %s %s %d @ %s", order_id, side, symbol, quantity, price)
        return str(order_id)

    def modify_order(self, order_id: str, quantity: int, price: float) -> bool:
        try:
            self._kite.modify_order(
                variety=self._kite.VARIETY_REGULAR,
                order_id=order_id,
                quantity=quantity,
                price=price,
            )
            return True
        except Exception as exc:
            logger.error("Modify order %s failed: %s", order_id, exc)
            return False

    def cancel_order(self, order_id: str) -> bool:
        try:
            self._kite.cancel_order(variety=self._kite.VARIETY_REGULAR, order_id=order_id)
            return True
        except Exception as exc:
            logger.error("Cancel order %s failed: %s", order_id, exc)
            return False

    def get_order_status(self, order_id: str) -> dict:
        orders = self._kite.orders()
        for o in orders:
            if str(o["order_id"]) == str(order_id):
                return {
                    "order_id": order_id,
                    "status":   o.get("status", "UNKNOWN"),
                    "filled":   o.get("filled_quantity", 0),
                    "pending":  o.get("pending_quantity", 0),
                    "price":    o.get("average_price", 0.0),
                }
        return {"order_id": order_id, "status": "NOT_FOUND"}

    def get_positions(self) -> list[dict]:
        raw = self._kite.positions()
        result = []
        for p in raw.get("net", []):
            if p.get("quantity", 0) != 0:
                result.append({
                    "symbol":    p["tradingsymbol"],
                    "qty":       p["quantity"],
                    "avg_price": p["average_price"],
                    "pnl":       p["pnl"],
                    "side":      "BUY" if p["quantity"] > 0 else "SELL",
                })
        return result

    def get_holdings(self) -> list[dict]:
        return [
            {"symbol": h["tradingsymbol"], "qty": h["quantity"], "avg_price": h["average_price"]}
            for h in self._kite.holdings()
        ]

    def get_margins(self) -> dict:
        m = self._kite.margins()
        equity = m.get("equity", {})
        return {
            "available": equity.get("available", {}).get("live_balance", 0.0),
            "used":      equity.get("utilised", {}).get("debits", 0.0),
        }

    def subscribe_market_data(self, symbols: list[str], callback: Any) -> None:
        """Requires KiteTicker — run in a separate thread."""
        try:
            from kiteconnect import KiteTicker  # type: ignore
            from threading import Thread

            api_key     = self._kite.api_key
            access_token = self._kite.access_token

            tokens = [int(s) for s in symbols if s.isdigit()]  # instrument tokens

            ticker = KiteTicker(api_key, access_token)
            ticker.on_ticks = lambda ws, ticks: [callback(t) for t in ticks]
            ticker.on_connect = lambda ws, response: ws.subscribe(tokens)

            t = Thread(target=ticker.connect, daemon=True)
            t.start()
        except ImportError:
            logger.error("kiteconnect not installed for ticker")

    def get_historical_data(
        self, symbol: str, start: str, end: str, interval: str
    ) -> list[dict]:
        # instrument_token lookup would be needed in real usage
        logger.warning("get_historical_data: requires instrument token for %s", symbol)
        return []
