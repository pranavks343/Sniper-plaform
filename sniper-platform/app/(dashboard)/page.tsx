'use client';

import { useEffect } from 'react';

import { Badge } from '@/components/ui/badge';
import { Card } from '@/components/ui/card';
import { PositionTable } from '@/components/trading/position-table';
import { usePositions } from '@/hooks/use-positions';
import { useRiskMetrics } from '@/hooks/use-risk-metrics';
import { useStrategies } from '@/hooks/use-strategies';
import { useTradingStore } from '@/store/trading-store';

export default function DashboardPage() {
  const { positions, totalPnl } = usePositions();
  const { metrics } = useRiskMetrics();
  const { strategies } = useStrategies();
  const connectRealtime = useTradingStore((state) => state.connectRealtime);

  useEffect(() => {
    connectRealtime();
  }, [connectRealtime]);

  return (
    <div className="space-y-6">
      <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <Card>
          <p className="text-sm text-slate-500">Daily P&L</p>
          <p className={`mt-2 text-2xl font-semibold ${totalPnl >= 0 ? 'text-success' : 'text-danger'}`}>{totalPnl.toFixed(2)}</p>
        </Card>
        <Card>
          <p className="text-sm text-slate-500">Drawdown</p>
          <p className="mt-2 text-2xl font-semibold">{((metrics?.drawdown ?? 0) * 100).toFixed(2)}%</p>
        </Card>
        <Card>
          <p className="text-sm text-slate-500">Total Trades</p>
          <p className="mt-2 text-2xl font-semibold">{positions.length * 4}</p>
        </Card>
        <Card>
          <p className="text-sm text-slate-500">Market Regime</p>
          <div className="mt-3 flex items-center gap-2">
            <Badge tone="success">TRENDING</Badge>
            <span className="text-sm">82%</span>
          </div>
        </Card>
      </section>

      <PositionTable positions={positions} />

      <section className="card-shell">
        <h3 className="font-heading text-xl">Active Strategies</h3>
        <div className="mt-3 flex flex-wrap gap-2">
          {strategies.length ? strategies.map((strategy) => <Badge key={strategy.id}>{strategy.name}</Badge>) : <p className="text-sm">No strategies created yet.</p>}
        </div>
      </section>
    </div>
  );
}
