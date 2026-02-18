import type { QuantumConfigUpdate, QuantumConnectionInfo, QuantumStatus, QuantumUsage } from './quantum';
import type { RiskLimits, RiskMetrics } from './risk';
import type { Strategy } from './strategy';
import type { Order, Position, Trade } from './trading';

export type Api = {
  strategy: {
    getAll: () => Promise<Strategy[]>;
    getById: (id: string) => Promise<Strategy>;
    create: (payload: Partial<Strategy>) => Promise<Strategy>;
    update: (id: string, payload: Partial<Strategy>) => Promise<Strategy>;
    remove: (id: string) => Promise<void>;
    activate: (id: string) => Promise<Strategy>;
    deactivate: (id: string) => Promise<Strategy>;
  };
  execution: {
    placeOrder: (payload: Record<string, unknown>) => Promise<Order>;
    listOrders: () => Promise<Order[]>;
    getPositions: () => Promise<Position[]>;
    getTrades: () => Promise<Trade[]>;
  };
  risk: {
    getMetrics: () => Promise<RiskMetrics>;
    getLimits: () => Promise<RiskLimits>;
    getViolations: () => Promise<RiskMetrics['violations']>;
  };
  quantum: {
    getStatus: () => Promise<QuantumStatus>;
    getUsage: () => Promise<QuantumUsage>;
    test: () => Promise<QuantumConnectionInfo>;
    connect: (payload?: { api_token?: string }) => Promise<QuantumConnectionInfo>;
    disconnect: () => Promise<{ connected: boolean }>;
    updateConfig: (payload: QuantumConfigUpdate) => Promise<QuantumConfigUpdate>;
  };
};
