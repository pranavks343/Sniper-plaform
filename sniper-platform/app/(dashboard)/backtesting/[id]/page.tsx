'use client';

import { useBacktest } from '@/hooks/use-backtest';

import { EquityCurveChart } from '@/components/charts/equity-curve-chart';
import { Card } from '@/components/ui/card';

export default function BacktestResultsPage({ params }: { params: { id: string } }) {
  const { status, progress, results } = useBacktest(params.id);

  const metrics = (results?.metrics ?? {}) as Record<string, number>;
  const equityCurve = ((results?.equity_curve ?? []) as Array<{ value: number }>).map((p) => p.value);
  const trades = (results?.trades ?? []) as Array<Record<string, unknown>>;

  return (
    <div className="space-y-6">
      <Card>
        <h1 className="font-heading text-3xl">Backtest Results</h1>
        <p className="mt-2 text-sm">Status: {status} ({Math.round(progress * 100)}%)</p>
      </Card>

      <div className="grid gap-4 md:grid-cols-3">
        <Card>Total Return: {(((metrics.total_return ?? 0) as number) * 100).toFixed(2)}%</Card>
        <Card>Sharpe: {(metrics.sharpe ?? 0).toFixed(2)}</Card>
        <Card>Max DD: {(((metrics.max_drawdown ?? 0) as number) * 100).toFixed(2)}%</Card>
      </div>

      <Card>
        <h2 className="mb-3 font-heading text-xl">Equity Curve</h2>
        <EquityCurveChart values={equityCurve} />
      </Card>

      <Card>
        <h2 className="mb-3 font-heading text-xl">Trades</h2>
        <table className="w-full text-sm">
          <thead>
            <tr className="text-left text-slate-500">
              <th>Symbol</th>
              <th>Side</th>
              <th>Qty</th>
              <th>Entry</th>
              <th>Exit</th>
              <th>P&L</th>
            </tr>
          </thead>
          <tbody>
            {trades.map((trade, idx) => (
              <tr key={idx} className="border-t border-slate-200/70 dark:border-slate-800">
                <td>{String(trade.symbol)}</td>
                <td>{String(trade.side)}</td>
                <td>{String(trade.qty)}</td>
                <td>{String(trade.entry)}</td>
                <td>{String(trade.exit)}</td>
                <td>{String(trade.pnl)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </Card>
    </div>
  );
}
