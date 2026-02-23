'use client';

import { useCallback, useEffect, useRef, useState } from 'react';

export interface RegimeData {
  regime: string;
  confidence: number;
  hurst: number;
  adx: number;
  volatility: number;
  description: string;
  currentPrice: number;
  sma20?: number;
  sma50?: number;
  shortTermMomentum?: number;
  mediumTermMomentum?: number;
  dataPoints?: number;
}

export interface MarketRegimeResponse {
  nifty: RegimeData | null;
  bankNifty: (RegimeData & { currentPrice: number }) | null;
  updatedAt: string;
  error?: string;
}

const POLL_INTERVAL_MS = 60_000;

export function useMarketRegime() {
  const [data, setData] = useState<MarketRegimeResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const fetchData = useCallback(async () => {
    try {
      const res = await fetch('/api/market-regime', { cache: 'no-store' });
      const json = await res.json();
      if (json.error) {
        setError(json.error);
      } else {
        setData(json);
        setError(null);
      }
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to fetch regime data');
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

  return { data, loading, error };
}
