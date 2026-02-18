export type RiskMetrics = {
  daily_pnl: number;
  drawdown: number;
  delta: number;
  gamma: number;
  theta: number;
  vega: number;
  trading_allowed: boolean;
  violations: RiskViolation[];
};

export type Greeks = {
  delta: number;
  gamma: number;
  theta: number;
  vega: number;
};

export type RiskLimits = {
  max_daily_loss_pct: number;
  max_drawdown_pct: number;
  max_delta: number;
  max_gamma: number;
  max_vega: number;
};

export type RiskViolation = {
  type: string;
  severity: string;
  value: number;
  limit: number;
  action_taken?: string;
};
