'use client';

import { useEffect, useState } from 'react';

import { apiClient } from '@/lib/api-client';

export function useBacktest(jobId?: string) {
  const [status, setStatus] = useState<string>('idle');
  const [progress, setProgress] = useState(0);
  const [results, setResults] = useState<Record<string, unknown> | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!jobId) {
      return;
    }

    let mounted = true;
    const run = async () => {
      try {
        setLoading(true);
        const state = await apiClient.backtest.status(jobId);
        if (!mounted) {
          return;
        }
        setStatus(state.status);
        setProgress(state.progress);
        if (state.status === 'completed') {
          const payload = await apiClient.backtest.results(jobId);
          if (mounted) {
            setResults(payload);
          }
        }
      } catch (err) {
        if (mounted) {
          setError((err as Error).message);
        }
      } finally {
        if (mounted) {
          setLoading(false);
        }
      }
    };

    void run();
    return () => {
      mounted = false;
    };
  }, [jobId]);

  return { status, progress, results, loading, error };
}
