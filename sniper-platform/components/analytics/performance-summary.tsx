import { formatINR } from '@/lib/utils';

export function PerformanceSummary({
  totalPnl,
  sharpe,
  winRate,
  maxDrawdown
}: {
  totalPnl: number;
  sharpe: number;
  winRate: number;
  maxDrawdown: number;
}) {
  return (
    <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
      <div className="card-shell">
        <p className="text-sm text-slate-500">Total P&L</p>
        <p className="mt-2 font-heading text-2xl">{formatINR(totalPnl)}</p>
      </div>
      <div className="card-shell">
        <p className="text-sm text-slate-500">Sharpe</p>
        <p className="mt-2 font-heading text-2xl">{sharpe.toFixed(2)}</p>
      </div>
      <div className="card-shell">
        <p className="text-sm text-slate-500">Win Rate</p>
        <p className="mt-2 font-heading text-2xl">{(winRate * 100).toFixed(1)}%</p>
      </div>
      <div className="card-shell">
        <p className="text-sm text-slate-500">Max Drawdown</p>
        <p className="mt-2 font-heading text-2xl text-danger">{(maxDrawdown * 100).toFixed(1)}%</p>
      </div>
    </div>
  );
}
