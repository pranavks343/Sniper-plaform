export type QuantumStatus = {
  available: boolean;
  provider: string;
  backend: string;
  credits: number;
  last_solve?: string;
};

export type QuantumUsage = {
  total_solves: number;
  avg_solve_time_ms: number;
  cost_this_month: number;
};

export type QuantumConnectionInfo = {
  connected: boolean;
  backend?: string;
  available_backends?: string[];
};

export type QuantumConfigUpdate = {
  enable_quantum_routing?: boolean;
  enable_quantum_portfolio?: boolean;
  enable_quantum_hedging?: boolean;
  quantum_timeout_ms?: number;
};
