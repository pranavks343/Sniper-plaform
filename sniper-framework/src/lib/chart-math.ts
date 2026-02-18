// Local type declarations (structurally compatible with apps/sniper/types/chart.ts)
type CandlePoint = { time: number; open: number; high: number; low: number; close: number; volume: number };
type LinePoint = { time: number; value: number };

export function calculateEma(values: number[], period: number): number[] {
  if (values.length === 0) {
    return [];
  }
  const alpha = 2 / (period + 1);
  const ema: number[] = [values[0]];
  for (let i = 1; i < values.length; i += 1) {
    ema.push(values[i] * alpha + ema[i - 1] * (1 - alpha));
  }
  return ema;
}

export function calculateVwap(candles: CandlePoint[]): number[] {
  let cumulativePriceVolume = 0;
  let cumulativeVolume = 0;
  return candles.map((candle) => {
    const typicalPrice = (candle.high + candle.low + candle.close) / 3;
    cumulativePriceVolume += typicalPrice * candle.volume;
    cumulativeVolume += candle.volume;
    return cumulativePriceVolume / Math.max(cumulativeVolume, 1e-9);
  });
}

export function toLineSeries(times: number[], values: number[]): LinePoint[] {
  const size = Math.min(times.length, values.length);
  const output: LinePoint[] = [];
  for (let i = 0; i < size; i += 1) {
    output.push({ time: times[i], value: values[i] });
  }
  return output;
}

export function clamp(value: number, min: number, max: number): number {
  return Math.min(max, Math.max(min, value));
}
