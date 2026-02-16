'use client';

import { useEffect, useState } from 'react';

import { websocketClient } from '@/lib/websocket-client';

export function useMarketData(symbol: string) {
  const [tick, setTick] = useState<Record<string, unknown> | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    websocketClient.market.connect();
    const unsubscribe = websocketClient.market.subscribe((payload) => {
      const event = payload as { data?: Record<string, unknown> };
      setTick({ symbol, ...(event.data ?? {}) });
      setLoading(false);
    });

    return () => {
      unsubscribe();
    };
  }, [symbol]);

  return { tick, loading, error };
}
