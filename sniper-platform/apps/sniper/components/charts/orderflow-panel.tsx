'use client';

import type { OrderBook, TimeSalesEntry } from '@/types/chart';

type OrderflowPanelProps = {
  orderBook: OrderBook;
  timeSales: TimeSalesEntry[];
};

function formatTime(epochSeconds: number): string {
  const date = new Date(epochSeconds * 1000);
  return date.toLocaleTimeString([], { hour12: false });
}

export function OrderflowPanel({ orderBook, timeSales }: OrderflowPanelProps) {
  return (
    <div className="grid h-full gap-3 xl:grid-cols-2">
      <div className="orderflow-card p-3">
        <p className="orderflow-title">Order Book</p>
        <div className="mt-3 grid grid-cols-2 gap-3">
          <div>
            <p className="orderflow-side-title bid">Bids</p>
            <div className="space-y-1 text-xs">
              {orderBook.bids.map((level, idx) => (
                <div key={`b-${idx}`} className="orderflow-row bid flex items-center justify-between px-2 py-1 transition-colors hover:bg-green-500/20">
                  <span suppressHydrationWarning>{level.price.toFixed(2)}</span>
                  <span className="text-muted" suppressHydrationWarning>{level.size}</span>
                </div>
              ))}
            </div>
          </div>
          <div>
            <p className="orderflow-side-title ask">Asks</p>
            <div className="space-y-1 text-xs">
              {orderBook.asks.map((level, idx) => (
                <div key={`a-${idx}`} className="orderflow-row ask flex items-center justify-between px-2 py-1 transition-colors hover:bg-red-500/20">
                  <span suppressHydrationWarning>{level.price.toFixed(2)}</span>
                  <span className="text-muted" suppressHydrationWarning>{level.size}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      <div className="orderflow-card p-3">
        <p className="orderflow-title">Time &amp; Sales</p>
        <div className="mt-3 h-[220px] overflow-auto pr-1">
          <div className="space-y-1 text-xs">
            {timeSales.slice(0, 30).map((trade) => (
              <div key={trade.id} className="orderflow-row trade grid grid-cols-[1fr_auto_auto] items-center gap-2 px-2 py-1 transition-colors hover:bg-blue-900/40">
                <span className="text-muted" suppressHydrationWarning>{formatTime(trade.time)}</span>
                <span className={trade.side === 'BUY' ? 'text-green-400' : 'text-red-400'} suppressHydrationWarning>{trade.price.toFixed(2)}</span>
                <span className="text-muted" suppressHydrationWarning>{trade.size}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
