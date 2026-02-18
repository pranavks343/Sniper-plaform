"""
Dhan HQ Broker Adapter
Implements BaseBroker against the official dhanhq Python SDK.

Requires: pip install dhanhq
"""
from __future__ import annotations

import logging
from typing import Any

from sniper.brokers.base import BaseBroker

logger = logging.getLogger("sniper.brokers.dhan")


class DhanBroker(BaseBroker):
    """
    Dhan HQ adapter.

    credentials dict keys:
        client_id:   Dhan client ID
        access_token: Dhan access token
    """

    def connect(self, credentials: dict) -> None:
        try:
            from dhanhq import dhanhq  # type: ignore

            self._dhan = dhanhq(
                client_id=credentials["client_id"],
                access_token=credentials["access_token"],
            )
            logger.info("Dhan connected — client: %s", credentials["client_id"])
        except ImportError:
            raise RuntimeError("dhanhq not installed. pip install dhanhq")

    def place_order(
        self,
        symbol: str,
        quantity: int,
        order_type: str,
        price: float,
        side: str,
    ) -> str:
        from dhanhq import dhanhq  # type: ignore

        transaction_type = dhanhq.BUY if side.upper() == "BUY" else dhanhq.SELL
        dhan_order_type  = dhanhq.MARKET if order_type.upper() == "MARKET" else dhanhq.LIMIT

        response = self._dhan.place_order(
            security_id=symbol,
            exchange_segment=dhanhq.NSE_EQ,
            transaction_type=transaction_type,
            quantity=quantity,
            order_type=dhan_order_type,
            product_type=dhanhq.INTRA,
            price=price if dhan_order_type == dhanhq.LIMIT else 0,
        )
        order_id = str(response.get("data", {}).get("orderId", "UNKNOWN"))
        logger.info("Dhan order placed: %s — %s %s %d @ %s", order_id, side, symbol, quantity, price)
        return order_id

    def modify_order(self, order_id: str, quantity: int, price: float) -> bool:
        try:
            self._dhan.modify_order(
                order_id=order_id,
                order_type="LIMIT",
                leg_name="ENTRY_LEG",
                quantity=quantity,
                price=price,
                trigger_price=0,
                disclosed_quantity=0,
                validity="DAY",
            )
            return True
        except Exception as exc:
            logger.error("Dhan modify order %s failed: %s", order_id, exc)
            return False

    def cancel_order(self, order_id: str) -> bool:
        try:
            self._dhan.cancel_order(order_id=order_id)
            return True
        except Exception as exc:
            logger.error("Dhan cancel order %s failed: %s", order_id, exc)
            return False

    def get_order_status(self, order_id: str) -> dict:
        try:
            resp = self._dhan.get_order_by_id(order_id=order_id)
            data = resp.get("data", {})
            return {
                "order_id": order_id,
                "status":   data.get("orderStatus", "UNKNOWN"),
                "filled":   data.get("filledQty", 0),
                "pending":  data.get("remainingQuantity", 0),
                "price":    data.get("price", 0.0),
            }
        except Exception as exc:
            logger.error("Dhan get order %s failed: %s", order_id, exc)
            return {"order_id": order_id, "status": "ERROR"}

    def get_positions(self) -> list[dict]:
        try:
            resp = self._dhan.get_positions()
            result = []
            for p in resp.get("data", []):
                qty = p.get("netQty", 0)
                if qty != 0:
                    result.append({
                        "symbol":    p.get("tradingSymbol", ""),
                        "qty":       qty,
                        "avg_price": p.get("buyAvg", 0.0) if qty > 0 else p.get("sellAvg", 0.0),
                        "pnl":       p.get("unrealizedProfit", 0.0),
                        "side":      "BUY" if qty > 0 else "SELL",
                    })
            return result
        except Exception as exc:
            logger.error("Dhan get positions failed: %s", exc)
            return []

    def get_holdings(self) -> list[dict]:
        try:
            resp = self._dhan.get_holdings()
            return [
                {"symbol": h.get("tradingSymbol"), "qty": h.get("totalQty", 0), "avg_price": h.get("avgCostPrice", 0.0)}
                for h in resp.get("data", [])
            ]
        except Exception:
            return []

    def get_margins(self) -> dict:
        try:
            resp = self._dhan.get_fund_limits()
            data = resp.get("data", {})
            return {
                "available": data.get("availabelBalance", 0.0),
                "used":      data.get("utilizedAmount", 0.0),
            }
        except Exception:
            return {"available": 0.0, "used": 0.0}

    def subscribe_market_data(self, symbols: list[str], callback: Any) -> None:
        """Dhan live feed via DhanFeed (WebSocket)."""
        try:
            from dhanhq import marketfeed  # type: ignore
            from threading import Thread

            instruments = [(marketfeed.NSE, s, marketfeed.Ticker) for s in symbols]

            async def _run() -> None:
                async with marketfeed.DhanFeed(
                    client_id=self._dhan.client_id,
                    access_token=self._dhan.access_token,
                    instruments=instruments,
                ) as feed:
                    async for msg in feed:
                        callback(msg)

            import asyncio
            t = Thread(target=lambda: asyncio.run(_run()), daemon=True)
            t.start()
        except ImportError:
            logger.error("dhanhq marketfeed not available")

    def get_historical_data(
        self, symbol: str, start: str, end: str, interval: str
    ) -> list[dict]:
        try:
            resp = self._dhan.historical_daily_data(
                symbol=symbol,
                exchange_segment="NSE_EQ",
                instrument_type="EQUITY",
                from_date=start,
                to_date=end,
            )
            return resp.get("data", [])
        except Exception as exc:
            logger.error("Dhan historical data failed: %s", exc)
            return []
