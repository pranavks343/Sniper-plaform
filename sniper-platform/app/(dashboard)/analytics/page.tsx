'use client';

import { EquityCurveChart } from '@/components/charts/equity-curve-chart';
import { PerformanceSummary } from '@/components/analytics/performance-summary';
import { Card } from '@/components/ui/card';

export default function AnalyticsPage() {
  const equity = Array.from({ length: 100 }, (_, i) => 1_000_000 * (1 + i / 300) + Math.sin(i / 5) * 5000);

  return (
    <div className="space-y-6">
      <h1 className="font-heading text-3xl">Analytics</h1>

      <PerformanceSummary totalPnl={180000} sharpe={1.9} winRate={0.62} maxDrawdown={0.08} />

      <Card>
        <h2 className="mb-3 font-heading text-xl">Equity Curve</h2>
        <EquityCurveChart values={equity} />
      </Card>

      <Card>
        <h2 className="font-heading text-xl">Monthly Returns</h2>
        <p className="mt-2 text-sm text-slate-600 dark:text-slate-300">Heatmap and distribution views scaffolded for API-backed data.</p>
      </Card>
    </div>
  );
}
