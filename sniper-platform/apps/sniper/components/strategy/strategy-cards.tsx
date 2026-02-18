import Link from 'next/link';
import { BarChart2, Edit2, Play, Square } from 'lucide-react';
import type { Strategy } from '@/types/strategy';
import { Badge } from '@sniper/framework';

function StrategyCard({ strategy }: { strategy: Strategy }) {
  const active  = strategy.status === 'active';
  const symbol  = (strategy.parameters?.symbol as string) ?? '--';
  const tf      = (strategy.parameters?.timeframe as string) ?? '--';

  return (
    <div
      className="rounded-md overflow-hidden transition"
      style={{ background: 'var(--tv-bg-surface)', border: '1px solid var(--tv-border)' }}
    >
      {/* Header */}
      <div
        className="px-4 py-3 border-b flex items-start justify-between gap-2"
        style={{ borderColor: 'var(--tv-border)' }}
      >
        <div className="min-w-0">
          <h3
            className="text-[13px] font-semibold truncate"
            style={{ color: 'var(--tv-text-primary)' }}
          >
            {strategy.name}
          </h3>
          <p className="panel-caption mt-0.5">{strategy.type}</p>
        </div>
        <Badge tone={active ? 'success' : 'muted'} dot={active} className="flex-shrink-0">
          {strategy.status}
        </Badge>
      </div>

      {/* Details */}
      <div className="px-4 py-3 grid grid-cols-2 gap-2">
        <div className="text-center">
          <p className="panel-caption mb-1">Symbol</p>
          <p className="text-[13px] font-mono font-semibold" style={{ color: 'var(--tv-text-primary)' }}>
            {symbol}
          </p>
        </div>
        <div className="text-center">
          <p className="panel-caption mb-1">Timeframe</p>
          <p className="text-[13px] font-mono font-semibold" style={{ color: 'var(--tv-text-primary)' }}>
            {tf}
          </p>
        </div>
      </div>

      {/* Actions */}
      <div
        className="px-3 py-2 border-t flex items-center gap-1.5"
        style={{ borderColor: 'var(--tv-border)' }}
      >
        <Link href={`/dashboard/strategies/${strategy.id}`}>
          <button className="tv-btn tv-btn-ghost text-[11px] py-1 px-2.5 flex items-center gap-1">
            <Edit2 size={11} />
            Edit
          </button>
        </Link>
        <Link href={`/dashboard/strategies/${strategy.id}/builder`}>
          <button className="tv-btn tv-btn-ghost text-[11px] py-1 px-2.5 flex items-center gap-1">
            <BarChart2 size={11} />
            Builder
          </button>
        </Link>
        <div className="flex-1" />
        {active ? (
          <button
            className="tv-btn text-[11px] py-1 px-2.5 flex items-center gap-1"
            style={{ background: 'rgba(239,83,80,0.1)', border: '1px solid rgba(239,83,80,0.3)', color: '#ef5350' }}
          >
            <Square size={10} />
            Stop
          </button>
        ) : (
          <button
            className="tv-btn text-[11px] py-1 px-2.5 flex items-center gap-1"
            style={{ background: 'rgba(38,166,154,0.1)', border: '1px solid rgba(38,166,154,0.3)', color: '#26a69a' }}
          >
            <Play size={10} />
            Start
          </button>
        )}
      </div>
    </div>
  );
}

export function StrategyCards({ strategies }: { strategies: Strategy[] }) {
  if (strategies.length === 0) {
    return (
      <div className="tv-panel py-12 flex flex-col items-center gap-3 text-center">
        <p className="text-[14px] font-semibold" style={{ color: 'var(--tv-text-primary)' }}>
          No strategies yet
        </p>
        <p className="text-[12px]" style={{ color: 'var(--tv-text-muted)' }}>
          Create your first strategy to see it here
        </p>
      </div>
    );
  }

  return (
    <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-3">
      {strategies.map((strategy) => (
        <StrategyCard key={strategy.id} strategy={strategy} />
      ))}
    </div>
  );
}
