export type CandlePoint = {
  time: number;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
};

export type LinePoint = {
  time: number;
  value: number;
};

export type OverlayVisibility = {
  ema20: boolean;
  ema50: boolean;
  vwap: boolean;
};

export type TickPoint = {
  time: number;
  price: number;
  volume: number;
  symbol: string;
};

export type TimeSalesEntry = {
  id: string;
  time: number;
  price: number;
  size: number;
  side: 'BUY' | 'SELL';
};

export type OrderBookLevel = {
  price: number;
  size: number;
};

export type OrderBook = {
  bids: OrderBookLevel[];
  asks: OrderBookLevel[];
};

export type PanelKind = 'main' | 'comparison' | 'momentum' | 'orderflow';

export type WorkspacePanel = {
  id: string;
  title: string;
  kind: PanelKind;
  w: number;
  h: number;
  minW: number;
  maxW: number;
  minH: number;
  maxH: number;
};
