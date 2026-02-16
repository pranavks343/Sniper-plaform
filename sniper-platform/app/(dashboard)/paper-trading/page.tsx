'use client';

import Link from 'next/link';

import { TradingViewChart } from '@/components/charts/trading-view-chart';
import { OrderEntryPanel } from '@/components/trading/order-entry-panel';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';

export default function PaperTradingPage() {
  return (
    <div className="space-y-6">
      <div className="card-shell flex items-center justify-between">
        <Badge tone="warning">PAPER TRADING MODE - Simulated Orders</Badge>
        <Link href="/dashboard/live-trading">
          <Button>Switch to Live Trading</Button>
        </Link>
      </div>

      <div className="grid gap-6 lg:grid-cols-5">
        <div className="lg:col-span-3">
          <Card>
            <h2 className="mb-3 font-heading text-2xl">Paper Trading Chart</h2>
            <TradingViewChart />
          </Card>
        </div>
        <div className="lg:col-span-2">
          <OrderEntryPanel />
        </div>
      </div>
    </div>
  );
}
