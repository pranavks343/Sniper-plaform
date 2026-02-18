export type Side = 'BUY' | 'SELL';

export type Order = {
  id: string;
  symbol: string;
  side: Side;
  quantity: number;
  order_type: string;
  status: 'PENDING' | 'PARTIAL' | 'COMPLETE' | 'CANCELLED';
  price?: number;
  filled_qty: number;
  avg_price?: number;
  strategy_id?: string;
  timestamp: string;
  costs?: Record<string, number>;
};

export type Position = {
  symbol: string;
  quantity: number;
  avg_price: number;
  current_price: number;
  pnl: number;
  delta: number;
  gamma: number;
  theta: number;
  vega: number;
};

export type Trade = {
  id: string;
  order_id: string;
  symbol: string;
  side: Side;
  quantity: number;
  entry_price: number;
  exit_price?: number;
  pnl: number;
  entry_time: string;
};
