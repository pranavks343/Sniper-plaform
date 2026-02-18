'use client';

import { useEffect, useMemo, useRef, useState } from 'react';

import { calculateEma, calculateVwap, toLineSeries } from '@/lib/chart-math';
import { websocketClient } from '@/lib/websocket-client';
import type { CandlePoint, LinePoint, OrderBook, TickPoint, TimeSalesEntry } from '@/types/chart';

const MAX_BARS = 360;
const BAR_INTERVAL_SECONDS = 60;

function generateSeedCandles(startPrice: number, count: number): CandlePoint[] {
  const now = Math.floor(Date.now() / 1000);
  const data: CandlePoint[] = [];
  let price = startPrice;

  for (let i = count; i > 0; i -= 1) {
    const time = now - i * BAR_INTERVAL_SECONDS;
    const drift = (Math.random() - 0.5) * 15;
    const open = price;
    const close = Math.max(1, open + drift);
    const high = Math.max(open, close) + Math.random() * 8;
    const low = Math.min(open, close) - Math.random() * 8;
    const volume = 800 + Math.random() * 1200;
    data.push({ time, open, high, low, close, volume });
    price = close;
  }

  return data;
}

function aggregateTick(candles: CandlePoint[], tick: TickPoint): CandlePoint[] {
  const bucket = Math.floor(tick.time / BAR_INTERVAL_SECONDS) * BAR_INTERVAL_SECONDS;
  const last = candles[candles.length - 1];

  if (!last || last.time < bucket) {
    const previousClose = last ? last.close : tick.price;
    const nextCandle: CandlePoint = {
      time: bucket,
      open: previousClose,
      high: Math.max(previousClose, tick.price),
      low: Math.min(previousClose, tick.price),
      close: tick.price,
      volume: tick.volume
    };
    return [...candles.slice(-MAX_BARS + 1), nextCandle];
  }

  const updated = {
    ...last,
    high: Math.max(last.high, tick.price),
    low: Math.min(last.low, tick.price),
    close: tick.price,
    volume: last.volume + tick.volume
  };

  return [...candles.slice(0, -1), updated];
}

function normalizeTick(payload: unknown, symbol: string, fallbackPrice: number): TickPoint {
  const envelope = payload as { data?: Record<string, unknown> };
  const data = envelope?.data ?? {};
  const eventTime = Number(data.ts ?? Date.now() / 1000);

  const parsedPrice = Number(data.ltp ?? data.price ?? Number.NaN);
  const price = Number.isFinite(parsedPrice) ? parsedPrice : Math.max(1, fallbackPrice + (Math.random() - 0.5) * 4);

  const parsedVolume = Number(data.volume ?? data.qty ?? Number.NaN);
  const volume = Number.isFinite(parsedVolume) ? parsedVolume : 10 + Math.random() * 90;

  return {
    time: Math.floor(Number.isFinite(eventTime) ? eventTime : Date.now() / 1000),
    price,
    volume,
    symbol: String(data.symbol ?? symbol)
  };
}

function buildOrderBook(lastPrice: number): OrderBook {
  const bids = Array.from({ length: 5 }, (_, level) => ({
    price: Number((lastPrice - 0.05 * (level + 1)).toFixed(2)),
    size: Math.round(60 + Math.random() * 700)
  }));

  const asks = Array.from({ length: 5 }, (_, level) => ({
    price: Number((lastPrice + 0.05 * (level + 1)).toFixed(2)),
    size: Math.round(60 + Math.random() * 700)
  }));

  return { bids, asks };
}

export function useTradingFeed(symbol: string) {
  const [candles, setCandles] = useState<CandlePoint[]>(() => generateSeedCandles(22450, 220));
  const [timeSales, setTimeSales] = useState<TimeSalesEntry[]>([]);
  const [orderBook, setOrderBook] = useState<OrderBook>(() => buildOrderBook(22450));
  const [ticksPerSecond, setTicksPerSecond] = useState(0);
  const [source, setSource] = useState<'live' | 'simulated'>('simulated');

  const queueRef = useRef<TickPoint[]>([]);
  const runningRef = useRef(true);
  const receivedInWindowRef = useRef(0);
  const lastIncomingAtRef = useRef(0);
  const lastPriceRef = useRef(candles[candles.length - 1]?.close ?? 22450);

  useEffect(() => {
    runningRef.current = true;
    websocketClient.market.connect();

    const unsubscribe = websocketClient.market.subscribe((payload) => {
      const tick = normalizeTick(payload, symbol, lastPriceRef.current);
      queueRef.current.push(tick);
      lastIncomingAtRef.current = Date.now();
      receivedInWindowRef.current += 1;
      setSource('live');
    });

    const frame = () => {
      if (!runningRef.current) {
        return;
      }

      if (queueRef.current.length > 0) {
        const ticks = queueRef.current.splice(0, queueRef.current.length);

        setCandles((prev) => {
          let next = prev;
          for (const tick of ticks) {
            next = aggregateTick(next, tick);
            lastPriceRef.current = tick.price;
          }
          return next;
        });

        setOrderBook(buildOrderBook(lastPriceRef.current));

        setTimeSales((prev) => {
          const additions = ticks.slice(-10).map((tick, idx) => ({
            id: `${tick.time}-${tick.price}-${idx}`,
            time: tick.time,
            price: tick.price,
            size: Math.round(tick.volume),
            side: (Math.random() > 0.5 ? 'BUY' : 'SELL') as 'BUY' | 'SELL'
          }));
          return [...additions.reverse(), ...prev].slice(0, 60);
        });
      }

      requestAnimationFrame(frame);
    };

    requestAnimationFrame(frame);

    const statsInterval = window.setInterval(() => {
      setTicksPerSecond(receivedInWindowRef.current);
      receivedInWindowRef.current = 0;
      if (Date.now() - lastIncomingAtRef.current > 3500) {
        setSource('simulated');
      }
    }, 1000);

    const simulatorInterval = window.setInterval(() => {
      if (Date.now() - lastIncomingAtRef.current < 2500) {
        return;
      }
      const simulated: TickPoint = {
        time: Math.floor(Date.now() / 1000),
        price: Math.max(1, lastPriceRef.current + (Math.random() - 0.5) * 6),
        volume: 20 + Math.random() * 100,
        symbol
      };
      queueRef.current.push(simulated);
      receivedInWindowRef.current += 1;
    }, 180);

    return () => {
      runningRef.current = false;
      unsubscribe();
      window.clearInterval(statsInterval);
      window.clearInterval(simulatorInterval);
    };
  }, [symbol]);

  const closeSeries = useMemo(() => candles.map((candle) => candle.close), [candles]);
  const times = useMemo(() => candles.map((candle) => candle.time), [candles]);

  const ema20 = useMemo<LinePoint[]>(() => toLineSeries(times, calculateEma(closeSeries, 20)), [times, closeSeries]);
  const ema50 = useMemo<LinePoint[]>(() => toLineSeries(times, calculateEma(closeSeries, 50)), [times, closeSeries]);
  const vwap = useMemo<LinePoint[]>(() => toLineSeries(times, calculateVwap(candles)), [times, candles]);

  const momentum = useMemo<LinePoint[]>(() => {
    if (closeSeries.length === 0) {
      return [];
    }
    const baseline = closeSeries[0];
    return toLineSeries(
      times,
      closeSeries.map((price) => ((price - baseline) / Math.max(baseline, 1e-9)) * 100)
    );
  }, [closeSeries, times]);

  const benchmark = useMemo<LinePoint[]>(() => {
    const wave = closeSeries.map((_, idx) => 0.18 * idx + Math.sin(idx / 7) * 0.9);
    return toLineSeries(times, wave);
  }, [closeSeries, times]);

  const lastPrice = candles[candles.length - 1]?.close ?? 0;
  const firstPrice = candles[0]?.open ?? lastPrice;
  const changePct = firstPrice === 0 ? 0 : ((lastPrice - firstPrice) / firstPrice) * 100;

  return {
    candles,
    ema20,
    ema50,
    vwap,
    momentum,
    benchmark,
    orderBook,
    timeSales,
    ticksPerSecond,
    source,
    lastPrice,
    changePct
  };
}
