'use client';

import type { Position } from '@/types/trading';

import { formatINR } from '@/lib/utils';

import { Button } from '../ui/button';

export function PositionTable({ positions }: { positions: Position[] }) {
  return (
    <div className="card-shell overflow-x-auto">
      <h3 className="mb-3 font-heading text-xl">Active Positions</h3>
      <table className="w-full text-sm">
        <thead>
          <tr className="text-left text-slate-500">
            <th>Symbol</th>
            <th>Qty</th>
            <th>Avg</th>
            <th>Current</th>
            <th>P&L</th>
            <th>Delta</th>
            <th>Gamma</th>
            <th>Theta</th>
            <th>Vega</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          {positions.map((position) => (
            <tr key={position.symbol} className="border-t border-slate-200/70 dark:border-slate-800">
              <td>{position.symbol}</td>
              <td>{position.quantity}</td>
              <td>{position.avg_price.toFixed(2)}</td>
              <td>{position.current_price.toFixed(2)}</td>
              <td className={position.pnl >= 0 ? 'text-success' : 'text-danger'}>{formatINR(position.pnl)}</td>
              <td>{position.delta.toFixed(2)}</td>
              <td>{position.gamma.toFixed(2)}</td>
              <td>{position.theta.toFixed(2)}</td>
              <td>{position.vega.toFixed(2)}</td>
              <td>
                <Button className="bg-danger px-2 py-1 text-xs">Close</Button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
