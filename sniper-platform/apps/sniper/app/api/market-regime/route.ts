import { NextResponse } from 'next/server';

export const revalidate = 0;
export const dynamic = 'force-dynamic';

interface ChartMeta {
  regularMarketPrice?: number;
  chartPreviousClose?: number;
  previousClose?: number;
}

interface ChartIndicators {
  quote?: Array<{
    close?: (number | null)[];
    high?: (number | null)[];
    low?: (number | null)[];
    volume?: (number | null)[];
  }>;
}

function calculateReturns(prices: number[]): number[] {
  const returns: number[] = [];
  for (let i = 1; i < prices.length; i++) {
    returns.push(Math.log(prices[i] / prices[i - 1]));
  }
  return returns;
}

function calculateHurst(prices: number[]): number {
  if (prices.length < 20) return 0.5;
  const maxLag = Math.min(20, Math.floor(prices.length / 2));
  const lags: number[] = [];
  const tau: number[] = [];
  for (let lag = 2; lag < maxLag; lag++) {
    const diffs: number[] = [];
    for (let i = lag; i < prices.length; i++) {
      diffs.push(prices[i] - prices[i - lag]);
    }
    const mean = diffs.reduce((a, b) => a + b, 0) / diffs.length;
    const std = Math.sqrt(diffs.reduce((a, b) => a + (b - mean) ** 2, 0) / diffs.length);
    if (std > 0) {
      lags.push(Math.log(lag));
      tau.push(Math.log(std));
    }
  }
  if (lags.length < 2) return 0.5;
  const n = lags.length;
  const sumX = lags.reduce((a, b) => a + b, 0);
  const sumY = tau.reduce((a, b) => a + b, 0);
  const sumXY = lags.reduce((a, x, i) => a + x * tau[i], 0);
  const sumX2 = lags.reduce((a, x) => a + x * x, 0);
  const slope = (n * sumXY - sumX * sumY) / (n * sumX2 - sumX * sumX);
  return Math.max(0, Math.min(1, slope));
}

function calculateADX(prices: number[]): number {
  if (prices.length < 15) return 25.0;
  const delta = prices.slice(-15).map((p, i, arr) => (i > 0 ? p - arr[i - 1] : 0)).slice(1);
  const up = delta.map((d) => (d > 0 ? d : 0));
  const down = delta.map((d) => (d < 0 ? -d : 0));
  const absDelta = delta.map((d) => Math.abs(d));
  const avgUp = up.reduce((a, b) => a + b, 0) / up.length;
  const avgDown = down.reduce((a, b) => a + b, 0) / down.length;
  const avgAbs = absDelta.reduce((a, b) => a + b, 0) / absDelta.length + 1e-9;
  const plusDI = (100 * avgUp) / avgAbs;
  const minusDI = (100 * avgDown) / avgAbs;
  return (100 * Math.abs(plusDI - minusDI)) / (plusDI + minusDI + 1e-9);
}

function detectRegime(prices: number[]): {
  regime: string;
  confidence: number;
  hurst: number;
  adx: number;
  volatility: number;
  description: string;
} {
  const returns = calculateReturns(prices);
  const hurst = calculateHurst(prices);
  const adx = calculateADX(prices);
  const vol = returns.length > 0
    ? Math.sqrt(returns.reduce((a, r) => a + r * r, 0) / returns.length) * Math.sqrt(252)
    : 0;
  const vol80 = returns.length > 0
    ? returns.map(Math.abs).sort((a, b) => a - b)[Math.floor(returns.length * 0.8)] ?? 0
    : 0;

  let regime: string;
  let confidence: number;
  let description: string;

  if (adx > 25 && vol80 < 0.02 && hurst > 0.55) {
    regime = 'TRENDING';
    confidence = Math.min(0.95, 0.6 + (adx - 25) / 100 + (hurst - 0.5) * 0.5);
    description = 'Market shows strong directional momentum. Trend-following strategies are favoured.';
  } else if (vol80 > 0.018 || vol > 0.25) {
    regime = 'VOLATILE';
    confidence = Math.min(0.95, 0.55 + vol80 * 10 + (vol > 0.3 ? 0.15 : 0));
    description = 'Elevated volatility detected. Options sellers beware — consider hedging or reducing position sizes.';
  } else {
    regime = 'MEAN_REVERTING';
    confidence = Math.min(0.95, 0.55 + (0.5 - Math.abs(hurst - 0.5)) * 0.8);
    description = 'Prices are range-bound. Mean-reversion and delta-neutral strategies perform well in this regime.';
  }

  return {
    regime,
    confidence: Math.round(confidence * 100) / 100,
    hurst: Math.round(hurst * 1000) / 1000,
    adx: Math.round(adx * 10) / 10,
    volatility: Math.round(vol * 10000) / 10000,
    description,
  };
}

async function fetchNiftyPrices(): Promise<number[]> {
  const url =
    'https://query1.finance.yahoo.com/v8/finance/chart/%5ENSEI?range=6mo&interval=1d';
  const res = await fetch(url, {
    headers: { 'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)' },
    next: { revalidate: 0 },
  });
  if (!res.ok) throw new Error(`Yahoo chart responded ${res.status}`);
  const json = await res.json();
  const result = json?.chart?.result?.[0];
  if (!result) throw new Error('No chart data');
  const indicators: ChartIndicators = result.indicators;
  const closes = indicators?.quote?.[0]?.close ?? [];
  return closes.filter((c): c is number => c !== null && c > 0);
}

async function fetchBankNiftyPrices(): Promise<number[]> {
  const url =
    'https://query1.finance.yahoo.com/v8/finance/chart/%5ENSEBANK?range=6mo&interval=1d';
  const res = await fetch(url, {
    headers: { 'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)' },
    next: { revalidate: 0 },
  });
  if (!res.ok) return [];
  const json = await res.json();
  const result = json?.chart?.result?.[0];
  if (!result) return [];
  const closes = result.indicators?.quote?.[0]?.close ?? [];
  return closes.filter((c: number | null) => c !== null && (c as number) > 0) as number[];
}

export async function GET() {
  try {
    const [niftyPrices, bankNiftyPrices] = await Promise.all([
      fetchNiftyPrices(),
      fetchBankNiftyPrices(),
    ]);

    const niftyRegime = detectRegime(niftyPrices);
    const bankNiftyRegime = bankNiftyPrices.length > 30 ? detectRegime(bankNiftyPrices) : null;

    const niftyReturns = calculateReturns(niftyPrices);
    const last5 = niftyReturns.slice(-5);
    const last20 = niftyReturns.slice(-20);
    const shortTermMomentum =
      last5.length > 0 ? last5.reduce((a, b) => a + b, 0) / last5.length : 0;
    const mediumTermMomentum =
      last20.length > 0 ? last20.reduce((a, b) => a + b, 0) / last20.length : 0;

    const currentPrice = niftyPrices[niftyPrices.length - 1] ?? 0;
    const sma20 =
      niftyPrices.length >= 20
        ? niftyPrices.slice(-20).reduce((a, b) => a + b, 0) / 20
        : currentPrice;
    const sma50 =
      niftyPrices.length >= 50
        ? niftyPrices.slice(-50).reduce((a, b) => a + b, 0) / 50
        : currentPrice;

    return NextResponse.json(
      {
        nifty: {
          ...niftyRegime,
          currentPrice: Math.round(currentPrice * 100) / 100,
          sma20: Math.round(sma20 * 100) / 100,
          sma50: Math.round(sma50 * 100) / 100,
          shortTermMomentum: Math.round(shortTermMomentum * 10000) / 10000,
          mediumTermMomentum: Math.round(mediumTermMomentum * 10000) / 10000,
          dataPoints: niftyPrices.length,
        },
        bankNifty: bankNiftyRegime
          ? {
              ...bankNiftyRegime,
              currentPrice:
                Math.round(
                  (bankNiftyPrices[bankNiftyPrices.length - 1] ?? 0) * 100,
                ) / 100,
            }
          : null,
        updatedAt: new Date().toISOString(),
      },
      {
        headers: {
          'Cache-Control': 'public, s-maxage=60, stale-while-revalidate=300',
        },
      },
    );
  } catch (err) {
    const message = err instanceof Error ? err.message : 'Unknown error';
    return NextResponse.json({ error: message }, { status: 502 });
  }
}
