'use client';

import { useCallback, useEffect, useRef, useState } from 'react';

export interface IndexTicker {
  symbol: string;
  price: number;
  change: number;
  pct: number;
  prevClose: number;
}

interface MarketDataResponse {
  tickers: IndexTicker[];
  updatedAt: string;
  error?: string;
}

const FALLBACK_TICKERS: IndexTicker[] = [
  { symbol: 'NIFTY', price: 0, change: 0, pct: 0, prevClose: 0 },
  { symbol: 'BANKNIFTY', price: 0, change: 0, pct: 0, prevClose: 0 },
  { symbol: 'SENSEX', price: 0, change: 0, pct: 0, prevClose: 0 },
  { symbol: 'USDINR', price: 0, change: 0, pct: 0, prevClose: 0 },
];

const POLL_INTERVAL_MS = 15_000;

export function useLiveIndices() {
  const [tickers, setTickers] = useState<IndexTicker[]>(FALLBACK_TICKERS);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const fetchData = useCallback(async () => {
    try {
      const res = await fetch('/api/market-data', { cache: 'no-store' });
      const data: MarketDataResponse = await res.json();
      if (data.tickers && data.tickers.length > 0) {
        setTickers(data.tickers);
        setError(null);
      } else if (data.error) {
        setError(data.error);
      }
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to fetch market data');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchData();
    timerRef.current = setInterval(fetchData, POLL_INTERVAL_MS);
    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
    };
  }, [fetchData]);

  return { tickers, loading, error };
}
