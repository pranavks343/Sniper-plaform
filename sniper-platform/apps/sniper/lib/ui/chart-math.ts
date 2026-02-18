/** EMA over a price series; returns array same length as prices (warm-up for first period-1) */
export function calculateEma(prices: number[], period: number): number[] {
  if (prices.length === 0) return [];
  const alpha = 2 / (period + 1);
  const out: number[] = [];
  let ema = prices[0];
  for (let i = 0; i < prices.length; i++) {
    if (i < period - 1) {
      ema = prices[i];
    } else if (i === period - 1) {
      const slice = prices.slice(0, period);
      ema = slice.reduce((a, b) => a + b, 0) / period;
    } else {
      ema = alpha * prices[i] + (1 - alpha) * ema;
    }
    out.push(ema);
  }
  return out;
}

/** Cumulative VWAP from OHLCV candles; one value per candle */
export function calculateVwap(
  candles: { open: number; high: number; low: number; close: number; volume: number }[]
): number[] {
  if (candles.length === 0) return [];
  let cumVol = 0;
  let cumVp = 0;
  return candles.map((c) => {
    const typical = (c.high + c.low + c.close) / 3;
    const v = c.volume || 0;
    cumVol += v;
    cumVp += typical * v;
    return cumVol > 0 ? cumVp / cumVol : typical;
  });
}

/** Zip times and values into line series for charts */
export function toLineSeries(
  times: number[],
  values: number[]
): { time: number; value: number }[] {
  const len = Math.min(times.length, values.length);
  return Array.from({ length: len }, (_, i) => ({ time: times[i], value: values[i] }));
}

export function clamp(value: number, min: number, max: number): number {
  return Math.min(max, Math.max(min, value));
}
