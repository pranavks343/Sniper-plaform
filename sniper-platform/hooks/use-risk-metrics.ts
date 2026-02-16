'use client';

import { useEffect } from 'react';

import { useRiskStore } from '@/store/risk-store';

export function useRiskMetrics() {
  const store = useRiskStore();

  useEffect(() => {
    void store.fetchRiskMetrics();
    void store.fetchViolations();
    store.connectRealtime();
  }, [store]);

  return {
    metrics: store.metrics,
    greeks: store.greeks,
    violations: store.violations,
    circuitBreakerActive: store.circuitBreakerActive
  };
}
