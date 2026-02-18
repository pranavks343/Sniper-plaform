import { create } from 'zustand';

import { apiClient } from '@/lib/api-client';
import type { Strategy } from '@/types/strategy';

type StrategyState = {
  strategies: Strategy[];
  activeStrategyId: string | null;
  selectedStrategyId: string | null;
  fetchStrategies: () => Promise<void>;
  createStrategy: (payload: Partial<Strategy>) => Promise<void>;
  updateStrategy: (id: string, payload: Partial<Strategy>) => Promise<void>;
  deleteStrategy: (id: string) => Promise<void>;
  activateStrategy: (id: string) => Promise<void>;
  deactivateStrategy: (id: string) => Promise<void>;
};

export const useStrategyStore = create<StrategyState>((set, get) => ({
  strategies: [],
  activeStrategyId: null,
  selectedStrategyId: null,
  fetchStrategies: async () => {
    const strategies = await apiClient.strategy.getAll();
    set({ strategies, activeStrategyId: strategies.find((s) => s.status === 'active')?.id ?? null });
  },
  createStrategy: async (payload) => {
    await apiClient.strategy.create(payload);
    await get().fetchStrategies();
  },
  updateStrategy: async (id, payload) => {
    await apiClient.strategy.update(id, payload);
    await get().fetchStrategies();
  },
  deleteStrategy: async (id) => {
    await apiClient.strategy.remove(id);
    await get().fetchStrategies();
  },
  activateStrategy: async (id) => {
    await apiClient.strategy.activate(id);
    await get().fetchStrategies();
  },
  deactivateStrategy: async (id) => {
    await apiClient.strategy.deactivate(id);
    await get().fetchStrategies();
  },
}));
