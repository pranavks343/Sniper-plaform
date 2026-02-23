'use client';

import { useEffect } from 'react';
import { useRiskStore } from '@/store/risk-store';

export function useRiskMetrics() {
  const fetchRiskMetrics    = useRiskStore((state) => state.fetchRiskMetrics);
  const fetchGreeks         = useRiskStore((state) => state.fetchGreeks);
  const setPortfolioState   = useRiskStore((state) => state.setPortfolioState);
  const fetchViolations     = useRiskStore((state) => state.fetchViolations);
  const connectRealtime     = useRiskStore((state) => state.connectRealtime);
  const metrics             = useRiskStore((state) => state.metrics);
  const greeks              = useRiskStore((state) => state.greeks);
  const greeksLoading       = useRiskStore((state) => state.greeksLoading);
  const violations          = useRiskStore((state) => state.violations);
  const circuitBreakerActive = useRiskStore((state) => state.circuitBreakerActive);

  useEffect(() => {
    fetchGreeks().catch(() => {});
    fetchRiskMetrics().catch(() => {});
    fetchViolations().catch(() => {});
    connectRealtime();
  }, [fetchGreeks, fetchRiskMetrics, fetchViolations, connectRealtime]);

  return { metrics, greeks, greeksLoading, violations, circuitBreakerActive, setPortfolioState };
}
