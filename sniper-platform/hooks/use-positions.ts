'use client';

import { useEffect, useMemo, useState } from 'react';

import { apiClient } from '@/lib/api-client';
import type { Position } from '@/types/trading';

export function usePositions() {
  const [positions, setPositions] = useState<Position[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    apiClient.execution
      .getPositions()
      .then(setPositions)
      .catch((err: Error) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  const totalPnl = positions.reduce((sum, position) => sum + position.pnl, 0);
  const greeks = positions.reduce(
    (acc, position) => {
      acc.delta += position.delta;
      acc.gamma += position.gamma;
      acc.theta += position.theta;
      acc.vega += position.vega;
      return acc;
    },
    { delta: 0, gamma: 0, theta: 0, vega: 0 }
  );

  return useMemo(() => ({ positions, loading, error, totalPnl, greeks }), [positions, loading, error, totalPnl, greeks]);
}
