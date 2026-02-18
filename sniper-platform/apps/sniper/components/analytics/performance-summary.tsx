import { formatINR } from '@sniper/framework';

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
        <p className="panel-caption">Total P&L</p>
        <p className="mt-2 font-heading text-2xl text-ink">{formatINR(totalPnl)}</p>
      </div>
      <div className="card-shell">
        <p className="panel-caption">Sharpe</p>
        <p className="mt-2 font-heading text-2xl text-ink">{sharpe.toFixed(2)}</p>
      </div>
      <div className="card-shell">
        <p className="panel-caption">Win Rate</p>
        <p className="mt-2 font-heading text-2xl text-ink">{(winRate * 100).toFixed(1)}%</p>
      </div>
      <div className="card-shell">
        <p className="panel-caption">Max Drawdown</p>
        <p className="mt-2 font-heading text-2xl text-danger">{(maxDrawdown * 100).toFixed(1)}%</p>
      </div>
    </div>
  );
}
