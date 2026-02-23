import { create } from 'zustand';

import { apiClient } from '@/lib/api-client';
import { websocketClient } from '@/lib/websocket-client';
import type { Greeks, RiskMetrics, RiskViolation } from '@/types/risk';

type RiskState = {
  metrics: RiskMetrics | null;
  greeks: Greeks;
  violations: RiskViolation[];
  circuitBreakerActive: boolean;
  greeksLoading: boolean;
  error: string | null;
  fetchRiskMetrics: () => Promise<void>;
  fetchGreeks: () => Promise<void>;
  setPortfolioState: (greeks: Greeks) => Promise<void>;
  fetchViolations: () => Promise<void>;
  connectRealtime: () => void;
};

let riskUnsubscribe: (() => void) | null = null;

const DEFAULT_GREEKS: Greeks = { delta: 0, gamma: 0, theta: 0, vega: 0 };

export const useRiskStore = create<RiskState>((set) => ({
  metrics: null,
  greeks: DEFAULT_GREEKS,
  violations: [],
  circuitBreakerActive: false,
  greeksLoading: false,
  error: null,

  /* ── /risk/metrics — may be slow due to Convex publishing, handle gracefully */
  fetchRiskMetrics: async () => {
    try {
      const metrics = await apiClient.risk.getMetrics();
      set({
        metrics,
        // Merge metrics greeks into the greeks state (keeps theta if already fetched)
        greeks: {
          delta: metrics.delta,
          gamma: metrics.gamma,
          theta: (metrics as any).theta ?? 0,
          vega:  metrics.vega,
        },
        error: null,
      });
    } catch (err) {
      // Don't throw — silently keep null metrics so UI degrades gracefully
      set({ error: err instanceof Error ? err.message : 'Failed to load risk metrics' });
    }
  },

  /* ── /risk/greeks — pure in-memory, always fast, includes theta */
  fetchGreeks: async () => {
    set({ greeksLoading: true });
    try {
      const data = await apiClient.risk.getGreeks();
      set({
        greeks: {
          delta: data.delta ?? 0,
          gamma: data.gamma ?? 0,
          theta: data.theta ?? 0,
          vega:  data.vega  ?? 0,
        },
        greeksLoading: false,
        error: null,
      });
    } catch (err) {
      set({ greeksLoading: false, error: err instanceof Error ? err.message : 'Failed to load greeks' });
    }
  },

  setPortfolioState: async (payload: Greeks) => {
    set({ greeksLoading: true });
    try {
      const data = await apiClient.risk.setPortfolioState(payload);
      set({
        greeks: {
          delta: data.delta ?? 0,
          gamma: data.gamma ?? 0,
          theta: data.theta ?? 0,
          vega:  data.vega  ?? 0,
        },
        greeksLoading: false,
        error: null,
      });
    } catch (err) {
      set({ greeksLoading: false, error: err instanceof Error ? err.message : 'Failed to update portfolio state' });
    }
  },

  fetchViolations: async () => {
    try {
      const violations = await apiClient.risk.getViolations();
      set({ violations });
    } catch {
      // Silently ignore — violations table stays empty
    }
  },

  connectRealtime: () => {
    if (riskUnsubscribe) return;
    try {
      websocketClient.risk.connect();
      riskUnsubscribe = websocketClient.risk.subscribe(() => {
        set((state) => ({ ...state }));
      });
    } catch {
      // WebSocket unavailable — ignore
    }
  },
}));
