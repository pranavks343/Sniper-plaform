'use client';

import { TradingViewChart } from '@/components/charts/trading-view-chart';
import { OrderEntryPanel } from '@/components/trading/order-entry-panel';
import { PositionTable } from '@/components/trading/position-table';
import { Card } from '@/components/ui/card';
import { usePositions } from '@/hooks/use-positions';

export default function LiveTradingPage() {
  const { positions } = usePositions();

  return (
    <div className="grid gap-6 lg:grid-cols-5">
      <div className="space-y-6 lg:col-span-3">
        <Card>
          <h2 className="mb-3 font-heading text-2xl">TradingView</h2>
          <TradingViewChart />
        </Card>
        <div className="grid gap-4 md:grid-cols-2">
          <Card>
            <h3 className="font-heading text-lg">Order Book</h3>
            <p className="mt-3 text-sm text-slate-600 dark:text-slate-300">Top 5 bids/asks streamed in real-time.</p>
          </Card>
          <Card>
            <h3 className="font-heading text-lg">Time & Sales</h3>
            <p className="mt-3 text-sm text-slate-600 dark:text-slate-300">Recent trades and aggressor direction.</p>
          </Card>
        </div>
      </div>
      <div className="space-y-6 lg:col-span-2">
        <OrderEntryPanel />
        <PositionTable positions={positions} />
      </div>
    </div>
  );
}
