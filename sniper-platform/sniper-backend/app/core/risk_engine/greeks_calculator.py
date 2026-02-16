from __future__ import annotations

from dataclasses import dataclass
from math import erf, exp, log, pi, sqrt


def _norm_cdf(x: float) -> float:
    return 0.5 * (1 + erf(x / sqrt(2)))


def _norm_pdf(x: float) -> float:
    return (1 / sqrt(2 * pi)) * exp(-(x**2) / 2)


@dataclass
class Greeks:
    delta: float
    gamma: float
    theta: float
    vega: float
    rho: float


@dataclass
class PortfolioGreeks:
    delta: float
    gamma: float
    theta: float
    vega: float
    rho: float


class GreeksCalculator:
    def black_scholes_price(self, params: dict) -> float:
        s = params['spot']
        k = params['strike']
        t = params['expiry']
        sigma = params['volatility']
        r = params.get('risk_free_rate', 0.06)
        option_type = params['option_type']
        d1 = (log(s / k) + (r + 0.5 * sigma**2) * t) / (sigma * sqrt(t) + 1e-9)
        d2 = d1 - sigma * sqrt(t)
        if option_type.upper() == 'CALL':
            return s * _norm_cdf(d1) - k * exp(-r * t) * _norm_cdf(d2)
        return k * exp(-r * t) * _norm_cdf(-d2) - s * _norm_cdf(-d1)

    def calculate_single_option(
        self,
        spot: float,
        strike: float,
        expiry: float,
        volatility: float,
        option_type: str,
        risk_free_rate: float,
    ) -> Greeks:
        d1 = (log(spot / strike) + (risk_free_rate + 0.5 * volatility**2) * expiry) / (volatility * sqrt(expiry) + 1e-9)
        d2 = d1 - volatility * sqrt(expiry)
        if option_type.upper() == 'CALL':
            delta = _norm_cdf(d1)
            theta = (-(spot * _norm_pdf(d1) * volatility) / (2 * sqrt(expiry)) - risk_free_rate * strike * exp(-risk_free_rate * expiry) * _norm_cdf(d2)) / 365
            rho = strike * expiry * exp(-risk_free_rate * expiry) * _norm_cdf(d2) / 100
        else:
            delta = _norm_cdf(d1) - 1
            theta = (-(spot * _norm_pdf(d1) * volatility) / (2 * sqrt(expiry)) + risk_free_rate * strike * exp(-risk_free_rate * expiry) * _norm_cdf(-d2)) / 365
            rho = -strike * expiry * exp(-risk_free_rate * expiry) * _norm_cdf(-d2) / 100

        gamma = _norm_pdf(d1) / (spot * volatility * sqrt(expiry) + 1e-9)
        vega = spot * _norm_pdf(d1) * sqrt(expiry) / 100
        return Greeks(delta=delta, gamma=gamma, theta=theta, vega=vega, rho=rho)

    def implied_volatility(self, market_price: float, params: dict) -> float:
        sigma = 0.2
        for _ in range(20):
            test_params = dict(params)
            test_params['volatility'] = sigma
            price = self.black_scholes_price(test_params)
            greeks = self.calculate_single_option(
                spot=params['spot'],
                strike=params['strike'],
                expiry=params['expiry'],
                volatility=sigma,
                option_type=params['option_type'],
                risk_free_rate=params.get('risk_free_rate', 0.06),
            )
            vega = max(greeks.vega * 100, 1e-6)
            sigma -= (price - market_price) / vega
            sigma = max(1e-4, min(3.0, sigma))
        return sigma

    def calculate_portfolio(self, positions: list[dict]) -> PortfolioGreeks:
        totals = {'delta': 0.0, 'gamma': 0.0, 'theta': 0.0, 'vega': 0.0, 'rho': 0.0}
        for pos in positions:
            qty = float(pos.get('quantity', 0.0))
            if pos.get('instrument_type') == 'OPTION':
                g = self.calculate_single_option(
                    spot=float(pos['spot']),
                    strike=float(pos['strike']),
                    expiry=float(pos['expiry']),
                    volatility=float(pos['volatility']),
                    option_type=pos.get('option_type', 'CALL'),
                    risk_free_rate=float(pos.get('risk_free_rate', 0.06)),
                )
                totals['delta'] += g.delta * qty
                totals['gamma'] += g.gamma * qty
                totals['theta'] += g.theta * qty
                totals['vega'] += g.vega * qty
                totals['rho'] += g.rho * qty
            else:
                totals['delta'] += qty

        return PortfolioGreeks(**totals)
