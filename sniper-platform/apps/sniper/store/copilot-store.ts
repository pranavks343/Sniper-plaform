import { create } from 'zustand';

/**
 * Minimal store that tracks which strategy is currently "selected" across
 * the whole dashboard (Strategy Library, Live Monitor, Builder, etc.).
 * The AI Copilot reads this to include strategy_id in every chat request.
 */
type CopilotState = {
  /** The strategy currently in focus (null = nothing selected) */
  selectedStrategyId: string | null;
  /** Whether the copilot panel is open */
  copilotOpen: boolean;

  setSelectedStrategy: (id: string | null) => void;
  openCopilot: () => void;
  closeCopilot: () => void;
  toggleCopilot: () => void;
};

export const useCopilotStore = create<CopilotState>((set) => ({
  selectedStrategyId: null,
  copilotOpen: false,

  setSelectedStrategy: (id) => set({ selectedStrategyId: id }),
  openCopilot:  () => set({ copilotOpen: true }),
  closeCopilot: () => set({ copilotOpen: false }),
  toggleCopilot: () => set((s) => ({ copilotOpen: !s.copilotOpen })),
}));
