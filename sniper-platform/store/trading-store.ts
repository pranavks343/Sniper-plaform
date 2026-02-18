import { create } from 'zustand';

import { websocketClient } from '@/lib/websocket-client';
import type { Order, Position, Trade } from '@/types/trading';

type TradingState = {
  orders: Order[];
  positions: Position[];
  trades: Trade[];
  marketData: Record<string, unknown>[];
  addOrder: (order: Order) => void;
  updateOrder: (order: Order) => void;
  setPositions: (positions: Position[]) => void;
  updatePosition: (position: Position) => void;
  setMarketData: (event: Record<string, unknown>) => void;
  connectRealtime: () => void;
};

let marketUnsubscribe: (() => void) | null = null;

export const useTradingStore = create<TradingState>((set, get) => ({
  orders: [],
  positions: [],
  trades: [],
  marketData: [],
  addOrder: (order) => set((state) => ({ orders: [order, ...state.orders] })),
  updateOrder: (order) =>
    set((state) => ({
      orders: state.orders.map((item) => (item.id === order.id ? order : item))
    })),
  setPositions: (positions) => set({ positions }),
  updatePosition: (position) =>
    set((state) => ({
      positions: state.positions.map((item) => (item.symbol === position.symbol ? position : item))
    })),
  setMarketData: (event) => set((state) => ({ marketData: [event, ...state.marketData].slice(0, 500) })),
  connectRealtime: () => {
    // Only connect once
    if (marketUnsubscribe) {
      return;
    }
    websocketClient.market.connect();
    websocketClient.orders.connect();
    websocketClient.positions.connect();

    marketUnsubscribe = websocketClient.market.subscribe((payload) => {
      get().setMarketData(payload as Record<string, unknown>);
    });
  }
}));
