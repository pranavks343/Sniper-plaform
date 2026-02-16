export type RiskMetrics = {
  daily_pnl: number;
  drawdown: number;
  delta: number;
  gamma: number;
  vega: number;
  trading_allowed: boolean;
  violations: RiskViolation[];
};

export type RiskViolation = {
  type: string;
  severity: string;
  value: number;
  limit: number;
  action_taken?: string;
};
