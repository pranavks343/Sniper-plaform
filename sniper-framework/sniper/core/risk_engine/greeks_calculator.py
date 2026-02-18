"""
Black-Scholes Greeks Calculator
Computes delta, gamma, theta, vega, rho for European options (calls & puts).
Also computes portfolio-level aggregated Greeks.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field


@dataclass
class Greeks:
    delta: float
    gamma: float
    theta: float    # per calendar day
    vega: float     # per 1% move in IV
    rho: float      # per 1% move in rate
    iv: float       # implied vol used
    intrinsic: float
    time_value: float


@dataclass
class PortfolioGreeks:
    net_delta: float
    net_gamma: float
    net_theta: float
    net_vega: float
    net_rho: float
    positions: list[dict] = field(default_factory=list)


class GreeksCalculator:
    """
    Black-Scholes Greeks for European options.
    Input units: prices in INR, time in years, vol as decimal (0.20 = 20%).
    """

    # ------------------------------------------------------------------
    # Single-option Greeks
    # ------------------------------------------------------------------

    def calculate(
        self,
        S: float,          # spot price
        K: float,          # strike price
        T: float,          # time to expiry (years)
        r: float,          # risk-free rate (decimal)
        sigma: float,      # implied volatility (decimal)
        option_type: str,  # "call" | "put"
        quantity: int = 1,
    ) -> Greeks:
        """
        Args:
            S:           Spot price (e.g. 24500)
            K:           Strike price (e.g. 24000)
            T:           Time to expiry in years (e.g. 0.0767 ≈ 28 days)
            r:           Risk-free rate (e.g. 0.065 for 6.5%)
            sigma:       Implied volatility (e.g. 0.18 for 18%)
            option_type: "call" or "put"
            quantity:    Number of lots (positive = long, negative = short)
        """
        if T <= 0:
            return self._expired(S, K, option_type, quantity)

        d1 = (math.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * math.sqrt(T))
        d2 = d1 - sigma * math.sqrt(T)

        nd1  = self._norm_cdf(d1)
        nd2  = self._norm_cdf(d2)
        npd1 = self._norm_pdf(d1)

        if option_type.lower() == "call":
            price    = S * nd1 - K * math.exp(-r * T) * nd2
            delta    = nd1
            rho_val  = K * T * math.exp(-r * T) * nd2 / 100
        else:
            nd1_neg  = self._norm_cdf(-d1)
            nd2_neg  = self._norm_cdf(-d2)
            price    = K * math.exp(-r * T) * nd2_neg - S * nd1_neg
            delta    = nd1 - 1
            rho_val  = -K * T * math.exp(-r * T) * nd2_neg / 100

        gamma = npd1 / (S * sigma * math.sqrt(T))
        theta = (
            -(S * npd1 * sigma) / (2 * math.sqrt(T))
            - r * K * math.exp(-r * T) * (self._norm_cdf(d2) if option_type.lower() == "call" else self._norm_cdf(-d2))
        ) / 365
        vega  = S * npd1 * math.sqrt(T) / 100   # per 1% move

        intrinsic = max(0.0, S - K if option_type.lower() == "call" else K - S)
        time_value = max(0.0, price - intrinsic)

        sign = 1 if quantity > 0 else -1

        return Greeks(
            delta=round(delta * quantity, 6),
            gamma=round(gamma * abs(quantity), 6),
            theta=round(theta * quantity, 4),
            vega=round(vega * quantity, 4),
            rho=round(rho_val * quantity, 4),
            iv=sigma,
            intrinsic=round(intrinsic, 2),
            time_value=round(time_value, 2),
        )

    def implied_volatility(
        self,
        market_price: float,
        S: float,
        K: float,
        T: float,
        r: float,
        option_type: str,
        tol: float = 1e-5,
        max_iter: int = 100,
    ) -> float:
        """Newton-Raphson IV solver."""
        if T <= 0 or market_price <= 0:
            return 0.0

        sigma = 0.2   # initial guess
        for _ in range(max_iter):
            g = self.calculate(S, K, T, r, sigma, option_type)
            price_model = self._bs_price(S, K, T, r, sigma, option_type)
            vega = g.vega * 100  # undo per-1% scaling
            if abs(vega) < 1e-10:
                break
            diff = price_model - market_price
            if abs(diff) < tol:
                break
            sigma -= diff / vega
            sigma = max(0.001, min(sigma, 5.0))

        return round(sigma, 6)

    # ------------------------------------------------------------------
    # Portfolio aggregation
    # ------------------------------------------------------------------

    def portfolio_greeks(self, positions: list[dict]) -> PortfolioGreeks:
        """
        Args:
            positions: list of {S, K, T, r, sigma, option_type, quantity}
        Returns:
            Aggregated net Greeks.
        """
        net = PortfolioGreeks(0.0, 0.0, 0.0, 0.0, 0.0)
        details: list[dict] = []

        for p in positions:
            g = self.calculate(
                S=p["S"], K=p["K"], T=p["T"],
                r=p.get("r", 0.065),
                sigma=p["sigma"],
                option_type=p["option_type"],
                quantity=p.get("quantity", 1),
            )
            net.net_delta += g.delta
            net.net_gamma += g.gamma
            net.net_theta += g.theta
            net.net_vega  += g.vega
            net.net_rho   += g.rho
            details.append({
                "symbol":      p.get("symbol", "?"),
                "delta":       g.delta,
                "gamma":       g.gamma,
                "theta":       g.theta,
                "vega":        g.vega,
            })

        net.positions   = details
        net.net_delta   = round(net.net_delta, 4)
        net.net_gamma   = round(net.net_gamma, 6)
        net.net_theta   = round(net.net_theta, 4)
        net.net_vega    = round(net.net_vega, 4)
        net.net_rho     = round(net.net_rho, 4)
        return net

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _bs_price(self, S: float, K: float, T: float, r: float, sigma: float, option_type: str) -> float:
        d1 = (math.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * math.sqrt(T))
        d2 = d1 - sigma * math.sqrt(T)
        if option_type.lower() == "call":
            return S * self._norm_cdf(d1) - K * math.exp(-r * T) * self._norm_cdf(d2)
        return K * math.exp(-r * T) * self._norm_cdf(-d2) - S * self._norm_cdf(-d1)

    @staticmethod
    def _expired(S: float, K: float, option_type: str, quantity: int) -> Greeks:
        intrinsic = max(0.0, S - K if option_type.lower() == "call" else K - S)
        delta = 1.0 if (option_type.lower() == "call" and S > K) else (-1.0 if (option_type.lower() == "put" and S < K) else 0.0)
        return Greeks(
            delta=delta * quantity, gamma=0.0, theta=0.0, vega=0.0, rho=0.0,
            iv=0.0, intrinsic=intrinsic, time_value=0.0,
        )

    @staticmethod
    def _norm_cdf(x: float) -> float:
        """Cumulative standard normal distribution."""
        return (1.0 + math.erf(x / math.sqrt(2))) / 2.0

    @staticmethod
    def _norm_pdf(x: float) -> float:
        """Standard normal PDF."""
        return math.exp(-0.5 * x * x) / math.sqrt(2 * math.pi)
