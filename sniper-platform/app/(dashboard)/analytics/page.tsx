'use client';

import { EquityCurveChart } from '@/components/charts/equity-curve-chart';
import { Card } from '@/components/ui/card';
import { usePositions } from '@/hooks/use-positions';
import { useRiskMetrics } from '@/hooks/use-risk-metrics';
import { BarChart3, ShieldCheck, TrendingUp } from 'lucide-react';

function MetricCard({
  label, value, sub, icon: Icon, color,
}: {
  label: string; value: string; sub?: string;
  icon: React.ElementType; color: string;
}) {
  return (
    <div className="metric-card">
      <div className="flex items-center justify-between mb-1">
        <span className="panel-caption">{label}</span>
        <Icon size={13} style={{ color }} />
      </div>
      <p className="text-[22px] font-bold font-mono" style={{ color }}>{value}</p>
      {sub && <p className="text-[11px] mt-0.5" style={{ color: 'var(--tv-text-muted)' }}>{sub}</p>}
    </div>
  );
}

export default function AnalyticsPage() {
  const { positions, loading: posLoading } = usePositions();
  const { metrics, greeks, greeksLoading } = useRiskMetrics();

  const totalPnl   = positions.reduce((a, p) => a + p.pnl, 0);
  const hasData    = positions.length > 0;

  // Build a minimal equity array from current positions if available
  const equityPoints = hasData
    ? positions.map((_, i) => {
        const runningPnl = positions.slice(0, i + 1).reduce((a, p) => a + p.pnl, 0);
        return 1_000_000 + runningPnl;
      })
    : [];

  return (
    <div className="space-y-5 animate-fadein">

      {/* Page header */}
      <div>
        <p className="panel-caption mb-1">Performance Analysis</p>
        <h1 className="text-[17px] font-semibold tracking-tight" style={{ color: 'var(--tv-text-primary)' }}>
          Analytics
        </h1>
      </div>

      {/* Summary cards */}
      <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
        <MetricCard
          label="Open P&L"
          value={hasData ? `${totalPnl >= 0 ? '+' : ''}₹${Math.abs(totalPnl).toLocaleString()}` : '—'}
          sub={hasData ? `${positions.length} open position${positions.length !== 1 ? 's' : ''}` : 'No open positions'}
          icon={TrendingUp}
          color={totalPnl >= 0 ? '#26a69a' : '#ef5350'}
        />
        <MetricCard
          label="Portfolio Delta"
          value={(metrics?.delta ?? 0).toFixed(1)}
          sub="Net delta exposure"
          icon={BarChart3}
          color={Math.abs(metrics?.delta ?? 0) < 500 ? '#2962ff' : '#f7a600'}
        />
        <MetricCard
          label="Gamma"
          value={(metrics?.gamma ?? 0).toFixed(3)}
          sub="Rate of delta change"
          icon={BarChart3}
          color="#9c27b0"
        />
        <MetricCard
          label="Vega"
          value={(metrics?.vega ?? 0).toFixed(1)}
          sub="Volatility sensitivity"
          icon={ShieldCheck}
          color="#f7a600"
        />
      </div>

      {/* Equity curve */}
      <Card>
        <h2 className="mb-3 font-heading text-xl">Equity Curve</h2>
        {equityPoints.length > 1 ? (
          <EquityCurveChart values={equityPoints} />
        ) : (
          <div className="h-32 flex items-center justify-center rounded-md"
            style={{ background: 'var(--tv-bg-elevated)', border: '1px solid var(--tv-border)' }}>
            <p className="text-[13px]" style={{ color: 'var(--tv-text-muted)' }}>
              {posLoading ? 'Loading positions…' : 'No position data available yet'}
            </p>
          </div>
        )}
      </Card>

      {/* Greeks breakdown — sourced from /risk/greeks (pure in-memory, always fast) */}
      <Card>
        <div className="flex items-center justify-between mb-3">
          <h2 className="font-heading text-xl">Greeks Exposure</h2>
          {greeksLoading && (
            <span className="text-[11px]" style={{ color: 'var(--tv-text-muted)' }}>Loading…</span>
          )}
          {!greeksLoading && metrics?.trading_allowed === false && (
            <span className="text-[11px] font-semibold" style={{ color: '#ef5350' }}>
              Circuit Breaker Active
            </span>
          )}
        </div>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
          {[
            {
              label: 'Delta',
              value: greeks.delta.toFixed(2),
              color: '#2962ff',
              hint: 'Price sensitivity',
              limit: metrics ? `Limit: ${metrics.delta !== undefined ? '±500' : '—'}` : null,
            },
            {
              label: 'Gamma',
              value: greeks.gamma.toFixed(4),
              color: '#9c27b0',
              hint: 'Delta acceleration',
              limit: null,
            },
            {
              label: 'Theta',
              value: greeks.theta.toFixed(2),
              color: '#ef5350',
              hint: 'Daily time decay (₹)',
              limit: null,
            },
            {
              label: 'Vega',
              value: greeks.vega.toFixed(2),
              color: '#f7a600',
              hint: 'Volatility sensitivity',
              limit: metrics ? `Limit: 10,000` : null,
            },
          ].map((g) => (
            <div
              key={g.label}
              className="flex flex-col items-center justify-center py-4 rounded-md"
              style={{
                background: `color-mix(in srgb, ${g.color}12, var(--tv-bg-elevated) 88%)`,
                border: `1px solid ${g.color}22`,
              }}
            >
              <p className="panel-caption mb-1">{g.label}</p>
              <p className="text-[22px] font-bold font-mono" style={{ color: g.color }}>
                {g.value}
              </p>
              <p className="text-[10px] mt-1" style={{ color: 'var(--tv-text-muted)' }}>
                {g.hint}
              </p>
              {g.limit && (
                <p className="text-[10px] mt-0.5" style={{ color: 'var(--tv-text-muted)' }}>
                  {g.limit}
                </p>
              )}
            </div>
          ))}
        </div>
      </Card>

      {/* Positions table */}
      {hasData && (
        <Card>
          <h2 className="mb-3 font-heading text-xl">Open Positions</h2>
          <div className="overflow-x-auto">
            <table className="tv-table w-full">
              <thead>
                <tr>
                  <th>Symbol</th>
                  <th className="text-right">Qty</th>
                  <th className="text-right">Avg Price</th>
                  <th className="text-right">Current</th>
                  <th className="text-right">P&L</th>
                  <th className="text-right">Delta</th>
                </tr>
              </thead>
              <tbody>
                {positions.map((p) => (
                  <tr key={p.symbol}>
                    <td className="font-semibold" style={{ color: 'var(--tv-text-primary)' }}>{p.symbol}</td>
                    <td className="text-right font-mono">{p.quantity}</td>
                    <td className="text-right font-mono">₹{p.avg_price.toFixed(2)}</td>
                    <td className="text-right font-mono">₹{p.current_price.toFixed(2)}</td>
                    <td className="text-right font-mono font-semibold"
                      style={{ color: p.pnl >= 0 ? '#26a69a' : '#ef5350' }}>
                      {p.pnl >= 0 ? '+' : ''}₹{p.pnl.toFixed(2)}
                    </td>
                    <td className="text-right font-mono">{p.delta.toFixed(2)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>
      )}

      {!hasData && !posLoading && (
        <Card>
          <div className="py-8 flex flex-col items-center gap-3 text-center">
            <BarChart3 size={28} style={{ color: 'var(--tv-text-muted)' }} />
            <p className="text-[14px] font-semibold" style={{ color: 'var(--tv-text-primary)' }}>
              No trading data yet
            </p>
            <p className="text-[12px]" style={{ color: 'var(--tv-text-muted)' }}>
              Analytics will populate as your strategies execute trades
            </p>
          </div>
        </Card>
      )}
    </div>
  );
}
