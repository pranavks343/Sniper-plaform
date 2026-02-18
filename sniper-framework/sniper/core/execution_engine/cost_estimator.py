"""Transaction cost estimation: brokerage, taxes, slippage, market impact."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class CostBreakdown:
    brokerage: float
    stt: float
    exchange: float
    gst: float
    sebi: float
    stamp_duty: float
    slippage: float
    market_impact: float
    total: float


class CostEstimator:
    """Estimates total cost of a trade (India-oriented: STT, exchange, GST, SEBI, stamp duty)."""

    BROKERAGE_PER_ORDER = 20.0

    def calculate_slippage(self, quantity: int, spread: float, urgency: float) -> float:
        return quantity * spread * (0.25 + urgency)

    def calculate_market_impact(
        self, quantity: int, avg_daily_volume: int
    ) -> float:
        participation = quantity / max(avg_daily_volume, 1)
        return 0.0005 * (participation**0.5) * quantity

    def estimate_total_cost(
        self,
        symbol: str,
        quantity: int,
        order_type: str,
        urgency: float,
        market_state: dict,
        side: str = "BUY",
    ) -> CostBreakdown:
        _ = symbol
        _ = order_type

        price = float(market_state.get("price", 0.0))
        turnover = price * quantity
        spread = float(market_state.get("spread", max(price * 0.0005, 0.01)))
        adv = int(market_state.get("avg_daily_volume", 1_000_000))
        exchange_rate = float(market_state.get("exchange_rate", 0.000019))

        brokerage = self.BROKERAGE_PER_ORDER
        stt_rate = (
            0.000125
            if market_state.get("instrument_type", "FUT") == "FUT"
            else 0.000625
        )
        stt = turnover * stt_rate if side.upper() == "SELL" else 0.0
        exchange = turnover * exchange_rate
        gst = 0.18 * (brokerage + exchange)
        sebi = turnover * (10 / 10_000_000)
        stamp_duty = turnover * 0.00003 if side.upper() == "BUY" else 0.0
        slippage = self.calculate_slippage(quantity, spread, urgency)
        market_impact = self.calculate_market_impact(quantity, adv)

        total = (
            brokerage + stt + exchange + gst + sebi + stamp_duty + slippage + market_impact
        )
        return CostBreakdown(
            brokerage=brokerage,
            stt=stt,
            exchange=exchange,
            gst=gst,
            sebi=sebi,
            stamp_duty=stamp_duty,
            slippage=slippage,
            market_impact=market_impact,
            total=total,
        )
