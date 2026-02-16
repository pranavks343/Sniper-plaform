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
