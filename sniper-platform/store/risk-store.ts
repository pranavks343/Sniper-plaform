import { create } from 'zustand';

import { apiClient } from '@/lib/api-client';
import { websocketClient } from '@/lib/websocket-client';
import type { RiskMetrics, RiskViolation } from '@/types/risk';

type RiskState = {
  metrics: RiskMetrics | null;
  greeks: Record<string, number>;
  violations: RiskViolation[];
  circuitBreakerActive: boolean;
  fetchRiskMetrics: () => Promise<void>;
  fetchViolations: () => Promise<void>;
  connectRealtime: () => void;
};

export const useRiskStore = create<RiskState>((set) => ({
  metrics: null,
  greeks: {},
  violations: [],
  circuitBreakerActive: false,
  fetchRiskMetrics: async () => {
    const metrics = await apiClient.risk.getMetrics();
    set({ metrics, greeks: { delta: metrics.delta, gamma: metrics.gamma, vega: metrics.vega } });
  },
  fetchViolations: async () => {
    const violations = await apiClient.risk.getViolations();
    set({ violations });
  },
  connectRealtime: () => {
    websocketClient.risk.connect();
    websocketClient.risk.subscribe(() => {
      set((state) => ({ ...state }));
    });
  }
}));
