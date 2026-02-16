'use client';

import { useCallback, useEffect, useState } from 'react';

import { apiClient } from '@/lib/api-client';
import type { QuantumStatus, QuantumUsage } from '@/types/quantum';

export function useQuantumStatus() {
  const [status, setStatus] = useState<QuantumStatus | null>(null);
  const [usage, setUsage] = useState<QuantumUsage | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const refresh = useCallback(async () => {
    try {
      setLoading(true);
      const [s, u] = await Promise.all([apiClient.quantum.getStatus(), apiClient.quantum.getUsage()]);
      setStatus(s);
      setUsage(u);
      setError(null);
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void refresh();
  }, [refresh]);

  return { status, usage, credits: status?.credits ?? 0, loading, error, refresh };
}
