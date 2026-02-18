'use client';

import type { Position } from '@/types/trading';
import { useMemo } from 'react';
import { BrainCircuit } from 'lucide-react';

import { formatINR } from '@/lib/utils';
import { Badge } from '../ui/badge';

export function PositionTable({ positions }: { positions: Position[] }) {
  const activePositions = useMemo(() => positions.filter((p) => p.quantity !== 0), [positions]);

  return (
    <div className="tv-panel overflow-hidden">
      {/* Header */}
      <div
        className="flex items-center justify-between px-4 py-3 border-b"
        style={{ borderColor: 'var(--tv-border)' }}
      >
        <div className="flex items-center gap-2">
          <BrainCircuit size={14} style={{ color: 'var(--tv-blue)' }} />
          <span className="panel-title">Algo Positions</span>
          <Badge>{activePositions.length} Open</Badge>
          <Badge tone="blue">System-Generated</Badge>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-[11px]" style={{ color: 'var(--tv-text-muted)' }}>
            Positions are managed exclusively by algorithms
          </span>
          <button
            className="tv-btn tv-btn-ghost text-[11px] py-1 px-2"
            style={{ borderColor: 'var(--tv-border-light)' }}
          >
            Export
          </button>
        </div>
      </div>

      {/* Table */}
      <div className="overflow-x-auto">
        <table className="tv-table">
          <thead>
            <tr>
              <th>Symbol</th>
              <th>Strategy</th>
              <th className="text-right">Qty</th>
              <th className="text-right">Avg Price</th>
              <th className="text-right">LTP</th>
              <th className="text-right">P&L</th>
              <th className="text-right">P&L%</th>
              <th className="text-right">Delta</th>
              <th className="text-right">Theta</th>
              <th className="text-right">Vega</th>
            </tr>
          </thead>
          <tbody>
            {activePositions.map((position) => {
              const pnlPct = position.avg_price !== 0
                ? ((position.current_price - position.avg_price) / position.avg_price) * 100
                : 0;
              const bull = position.pnl >= 0;

              return (
                <tr key={position.symbol}>
                  <td>
                    <div className="flex items-center gap-2">
                      <span
                        className="h-1.5 w-1.5 rounded-full flex-shrink-0"
                        style={{ background: position.quantity > 0 ? '#26a69a' : '#ef5350' }}
                      />
                      <span className="font-semibold text-[12px]" style={{ color: 'var(--tv-text-primary)' }}>
                        {position.symbol}
                      </span>
                      <Badge tone={position.quantity > 0 ? 'success' : 'danger'} className="text-[10px] py-0">
                        {position.quantity > 0 ? 'LONG' : 'SHORT'}
                      </Badge>
                    </div>
                  </td>
                  <td>
                    <span className="text-[11px]" style={{ color: 'var(--tv-text-muted)' }}>
                      Iron Condor NIFTY
                    </span>
                  </td>
                  <td className="text-right font-mono" style={{ color: 'var(--tv-text-primary)' }}>
                    {position.quantity}
                  </td>
                  <td className="text-right font-mono" style={{ color: 'var(--tv-text-secondary)' }}>
                    {position.avg_price.toFixed(2)}
                  </td>
                  <td className="text-right font-mono font-semibold" style={{ color: 'var(--tv-text-primary)' }}>
                    {position.current_price.toFixed(2)}
                  </td>
                  <td className="text-right font-mono font-semibold" style={{ color: bull ? '#26a69a' : '#ef5350' }}>
                    {bull ? '+' : ''}{formatINR(position.pnl)}
                  </td>
                  <td className="text-right font-mono text-[11px]" style={{ color: bull ? '#26a69a' : '#ef5350' }}>
                    {bull ? '+' : ''}{pnlPct.toFixed(2)}%
                  </td>
                  <td className="text-right font-mono text-[11px]" style={{ color: 'var(--tv-text-secondary)' }}>
                    {position.delta.toFixed(2)}
                  </td>
                  <td className="text-right font-mono text-[11px]" style={{ color: 'var(--tv-text-secondary)' }}>
                    {position.theta.toFixed(2)}
                  </td>
                  <td className="text-right font-mono text-[11px]" style={{ color: 'var(--tv-text-secondary)' }}>
                    {position.vega.toFixed(2)}
                  </td>
                </tr>
              );
            })}

            {activePositions.length === 0 && (
              <tr>
                <td colSpan={10} className="py-10 text-center" style={{ color: 'var(--tv-text-muted)' }}>
                  <div className="flex flex-col items-center gap-2">
                    <BrainCircuit size={24} style={{ color: 'var(--tv-text-muted)', opacity: 0.5 }} />
                    <span className="text-[13px]">No active algo positions</span>
                    <span className="text-[11px]">Activate a strategy and the system will open positions automatically</span>
                  </div>
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
