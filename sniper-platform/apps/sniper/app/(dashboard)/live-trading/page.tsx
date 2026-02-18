'use client';

import { useEffect, useRef } from 'react';
import gsap from 'gsap';
import Link from 'next/link';
import {
  Activity,
  AlertTriangle,
  BrainCircuit,
  CheckCircle2,
  ChevronRight,
  Play,
  Plus,
  Shield,
  Square,
  TrendingDown,
  TrendingUp,
  Zap,
} from 'lucide-react';

import { TradingWorkspace } from '@/components/charts/trading-workspace';
import { PositionTable } from '@/components/trading/position-table';
import { Badge } from '@sniper/framework';
import { usePositions } from '@/hooks/use-positions';
import { useRiskMetrics } from '@/hooks/use-risk-metrics';
import { useStrategies } from '@/hooks/use-strategies';
import { useCopilotStore } from '@/store/copilot-store';
import type { Strategy } from '@/types/strategy';

/* ─── Algo status row ─────────────────────────────────────────────────────── */
function AlgoStatusRow({ strategy, onToggle }: {
  strategy: Strategy;
  onToggle: (id: string) => void;
}) {
  const active  = strategy.status === 'active';
  const symbol  = (strategy.parameters?.symbol as string) ?? '--';
  const regime  = (strategy.regime_filters?.[0] ?? 'IDLE') as string;

  return (
    <div
      className="flex items-center gap-3 px-4 py-2.5 border-b last:border-0 hover:bg-[var(--tv-bg-elevated)] transition-colors"
      style={{ borderColor: 'var(--tv-border)' }}
    >
      <span
        className={`h-2 w-2 rounded-full flex-shrink-0 ${active ? 'live-dot' : ''}`}
        style={{ background: active ? '#26a69a' : 'var(--tv-text-muted)' }}
      />
      <div className="flex-1 min-w-0">
        <p className="text-[12px] font-semibold truncate" style={{ color: 'var(--tv-text-primary)' }}>
          {strategy.name}
        </p>
        <div className="flex items-center gap-1.5 mt-0.5">
          <Badge
            tone={regime === 'TRENDING' ? 'success' : regime === 'MEAN_REVERTING' ? 'blue' : 'muted'}
            className="text-[9px] py-0"
          >
            {regime}
          </Badge>
          {symbol !== '--' && (
            <span className="text-[10px]" style={{ color: 'var(--tv-text-muted)' }}>{symbol}</span>
          )}
        </div>
      </div>
      <button
        onClick={() => onToggle(strategy.id)}
        className="flex items-center gap-1 rounded px-2 py-1 text-[10px] font-semibold transition-all"
        style={active
          ? { background: 'rgba(239,83,80,0.1)', border: '1px solid rgba(239,83,80,0.3)', color: '#ef5350' }
          : { background: 'rgba(38,166,154,0.1)', border: '1px solid rgba(38,166,154,0.3)', color: '#26a69a' }
        }
      >
        {active ? <><Square size={9} /> Stop</> : <><Play size={9} /> Start</>}
      </button>
    </div>
  );
}

/* ─── Page ────────────────────────────────────────────────────────────────── */
export default function LiveTradingPage() {
  const { positions }                                        = usePositions();
  const { metrics }                                          = useRiskMetrics();
  const { strategies, activateStrategy, deactivateStrategy } = useStrategies();
  const { setSelectedStrategy } = useCopilotStore();
  const pageRef = useRef<HTMLDivElement>(null);

  // Set the first active strategy as copilot context when viewing the monitor
  useEffect(() => {
    const first = strategies.find((s) => s.status === 'active');
    setSelectedStrategy(first?.id ?? null);
  }, [strategies, setSelectedStrategy]);

  useEffect(() => {
    if (!pageRef.current) return;
    const ctx = gsap.context(() => {
      const tl = gsap.timeline({ defaults: { ease: 'power3.out' } });
      tl.fromTo('.lt-header', { opacity: 0, y: -14 }, { opacity: 1, y: 0, duration: 0.4 })
        .fromTo('.lt-bar',    { opacity: 0 },          { opacity: 1, duration: 0.35 }, '-=0.1')
        .fromTo('.lt-chart',  { opacity: 0, y: 20 },   { opacity: 1, y: 0, duration: 0.45 }, '-=0.15')
        .fromTo('.lt-side',   { opacity: 0, x: 20 },   { opacity: 1, x: 0, duration: 0.45 }, '-=0.3')
        .fromTo('.lt-bottom', { opacity: 0, y: 20 },   { opacity: 1, y: 0, duration: 0.4 }, '-=0.1');
    }, pageRef);
    return () => ctx.revert();
  }, []);

  const handleToggle = async (id: string) => {
    const s = strategies.find((st) => st.id === id);
    if (!s) return;
    if (s.status === 'active') {
      await deactivateStrategy(id);
    } else {
      await activateStrategy(id);
    }
  };

  const activeCount  = strategies.filter((s) => s.status === 'active').length;
  const totalPosPnl  = positions.reduce((acc, p) => acc + p.pnl, 0);
  const tradingOk    = metrics?.trading_allowed !== false;

  return (
    <div ref={pageRef} className="space-y-4">

      {/* Header */}
      <div className="lt-header flex flex-wrap items-center justify-between gap-3">
        <div>
          <p className="panel-caption mb-1">Algorithmic Execution Monitor</p>
          <h1 className="text-[17px] font-semibold tracking-tight" style={{ color: 'var(--tv-text-primary)' }}>
            Live Trading
          </h1>
        </div>
        <div className="flex items-center gap-2">
          <Badge tone={tradingOk ? 'success' : 'danger'} dot>
            {tradingOk ? 'Algo Engine: Armed' : 'Trading Restricted'}
          </Badge>
          {activeCount > 0 && <Badge tone="blue">{activeCount} Strategies Active</Badge>}
          {positions.length > 0 && (
            <Badge tone={totalPosPnl >= 0 ? 'success' : 'danger'}>
              {totalPosPnl >= 0 ? '+' : ''}₹{totalPosPnl.toLocaleString()} P&L
            </Badge>
          )}
        </div>
      </div>

      {/* Status bar */}
      <div
        className="lt-bar rounded-md flex flex-wrap items-center gap-0 overflow-hidden"
        style={{ background: 'var(--tv-bg-surface)', border: '1px solid var(--tv-border)' }}
      >
        {[
          { label: 'Open Positions P&L', value: positions.length > 0 ? `${totalPosPnl >= 0 ? '+' : ''}₹${totalPosPnl.toLocaleString()}` : '—', color: positions.length > 0 ? (totalPosPnl >= 0 ? '#26a69a' : '#ef5350') : 'var(--tv-text-muted)' },
          { label: 'Open Positions',     value: `${positions.length}`,                           color: 'var(--tv-text-primary)' },
          { label: 'Active Algos',       value: `${activeCount} / ${strategies.length}`,         color: '#2962ff' },
          { label: 'Portfolio Delta',    value: (metrics?.delta ?? 0).toFixed(1),                color: Math.abs(metrics?.delta ?? 0) < 500 ? '#26a69a' : '#f7a600' },
          { label: 'Risk Status',        value: tradingOk ? 'ALLOWED' : 'RESTRICTED',            color: tradingOk ? '#26a69a' : '#ef5350' },
        ].map((chip) => (
          <div
            key={chip.label}
            className="flex flex-col px-4 py-2.5 border-r"
            style={{ borderColor: 'var(--tv-border)' }}
          >
            <span className="panel-caption">{chip.label}</span>
            <span className="text-[13px] font-semibold font-mono mt-0.5" style={{ color: chip.color }}>
              {chip.value}
            </span>
          </div>
        ))}
        <div className="ml-auto px-4 py-2.5 flex items-center gap-2">
          {tradingOk ? (
            <div className="flex items-center gap-1.5 text-[12px]" style={{ color: '#26a69a' }}>
              <CheckCircle2 size={13} /> All systems nominal
            </div>
          ) : (
            <div className="flex items-center gap-1.5 text-[12px]" style={{ color: '#ef5350' }}>
              <AlertTriangle size={13} /> Circuit breaker active
            </div>
          )}
        </div>
      </div>

      {/* Chart + Algo panel */}
      <div className="grid gap-4 xl:grid-cols-4">
        {/* Chart */}
        <div className="lt-chart xl:col-span-3">
          <TradingWorkspace symbol="AAPL" />
        </div>

        {/* Algo control panel */}
        <div className="lt-side space-y-4 xl:col-span-1">
          <div className="tv-panel overflow-hidden">
            <div className="px-4 py-3 border-b flex items-center justify-between" style={{ borderColor: 'var(--tv-border)' }}>
              <div className="flex items-center gap-2">
                <BrainCircuit size={13} style={{ color: '#2962ff' }} />
                <span className="panel-title">Algo Control</span>
              </div>
              <Link href="/dashboard/strategies">
                <ChevronRight size={14} style={{ color: 'var(--tv-text-muted)' }} />
              </Link>
            </div>
            {strategies.length === 0 ? (
              <div className="px-4 py-6 text-center">
                <p className="text-[12px]" style={{ color: 'var(--tv-text-muted)' }}>
                  No strategies yet
                </p>
                <Link href="/dashboard/strategies/new">
                  <button className="mt-3 tv-btn tv-btn-primary text-[11px] py-1 px-3 flex items-center gap-1 mx-auto">
                    <Plus size={10} /> Create Strategy
                  </button>
                </Link>
              </div>
            ) : (
              strategies.map((s) => (
                <AlgoStatusRow key={s.id} strategy={s} onToggle={handleToggle} />
              ))
            )}
          </div>

          {/* Risk summary */}
          <div className="tv-panel p-4 space-y-3">
            <div className="flex items-center gap-2">
              <Shield size={13} style={{ color: '#26a69a' }} />
              <span className="panel-title">Risk Status</span>
            </div>
            {[
              {
                label: 'Portfolio Delta',
                used:  Math.min(Math.abs(metrics?.delta ?? 0) / 10, 100),
                value: (metrics?.delta ?? 0).toFixed(1),
              },
              {
                label: 'Max Drawdown',
                used:  Math.min((metrics?.drawdown ?? 0) * 100 / 20 * 100, 100),
                value: `${((metrics?.drawdown ?? 0) * 100).toFixed(2)}%`,
              },
              {
                label: 'Open Positions',
                used:  Math.min(positions.length / 10 * 100, 100),
                value: `${positions.length} open`,
              },
            ].map((r) => (
              <div key={r.label}>
                <div className="flex justify-between text-[11px] mb-1">
                  <span style={{ color: 'var(--tv-text-muted)' }}>{r.label}</span>
                  <span className="font-mono" style={{ color: 'var(--tv-text-primary)' }}>{r.value}</span>
                </div>
                <div className="h-1 rounded-full overflow-hidden" style={{ background: 'var(--tv-bg-elevated)' }}>
                  <div
                    className="h-full rounded-full"
                    style={{
                      width:      `${r.used}%`,
                      background: r.used > 80 ? '#ef5350' : r.used > 60 ? '#f7a600' : '#26a69a',
                    }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Positions + Activity feed */}
      <div className="lt-bottom grid gap-4 xl:grid-cols-5">
        <div className="xl:col-span-3">
          <PositionTable positions={positions} />
        </div>

        {/* Activity feed */}
        <div className="tv-panel overflow-hidden xl:col-span-2">
          <div className="px-4 py-3 border-b flex items-center gap-2" style={{ borderColor: 'var(--tv-border)' }}>
            <Activity size={13} style={{ color: '#2962ff' }} />
            <span className="panel-title">Algo Activity Feed</span>
            <Badge tone={tradingOk ? 'success' : 'danger'} dot className="ml-auto">
              {tradingOk ? 'Live' : 'Halted'}
            </Badge>
          </div>
          {positions.length === 0 && strategies.filter((s) => s.status === 'active').length === 0 ? (
            <div className="px-4 py-10 flex flex-col items-center gap-3 text-center">
              <Activity size={22} style={{ color: 'var(--tv-text-muted)' }} />
              <p className="text-[12px]" style={{ color: 'var(--tv-text-muted)' }}>
                No active algo trades yet
              </p>
              <p className="text-[11px]" style={{ color: 'var(--tv-text-muted)' }}>
                Activity will appear here once strategies start executing
              </p>
            </div>
          ) : (
            <div className="px-4 py-4 flex flex-col gap-2">
              {positions.map((p) => (
                <div key={p.symbol} className="border-b pb-2" style={{ borderColor: 'var(--tv-border)' }}>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <Badge tone={p.pnl >= 0 ? 'success' : 'danger'} className="text-[9px] py-0">
                        {p.quantity > 0 ? 'LONG' : 'SHORT'}
                      </Badge>
                      <span className="text-[11px] font-semibold" style={{ color: 'var(--tv-text-primary)' }}>
                        {p.symbol}
                      </span>
                    </div>
                    <span className="text-[11px] font-mono font-semibold"
                      style={{ color: p.pnl >= 0 ? '#26a69a' : '#ef5350' }}>
                      {p.pnl >= 0 ? '+' : ''}₹{p.pnl.toLocaleString()}
                    </span>
                  </div>
                  <p className="text-[10px] mt-0.5" style={{ color: 'var(--tv-text-muted)' }}>
                    {Math.abs(p.quantity)} qty @ ₹{p.avg_price.toFixed(2)} avg
                  </p>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Info cards */}
      <div className="lt-bottom grid gap-4 lg:grid-cols-3">
        {[
          { icon: Zap,          title: 'Zero Manual Intervention',  body: 'All positions are opened and closed exclusively by algorithms. The system monitors signals continuously and executes automatically.',       color: '#2962ff' },
          { icon: BrainCircuit, title: 'Signal Intelligence',       body: 'Quantum-enhanced market regime detection drives strategy selection. Algos auto-pause when market conditions turn unfavorable.',             color: '#26a69a' },
          { icon: Shield,       title: 'Automated Risk Engine',     body: 'Circuit breaker halts all strategies when portfolio loss limit is reached. Trailing stops protect open profits automatically.',              color: '#f7a600' },
        ].map((c) => (
          <div key={c.title} className="tv-panel p-4">
            <div className="flex items-center gap-2 mb-2">
              <div className="flex h-7 w-7 items-center justify-center rounded" style={{ background: `${c.color}18` }}>
                <c.icon size={14} style={{ color: c.color }} />
              </div>
              <span className="text-[13px] font-semibold" style={{ color: 'var(--tv-text-primary)' }}>{c.title}</span>
            </div>
            <p className="text-[12px] leading-relaxed" style={{ color: 'var(--tv-text-secondary)' }}>{c.body}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
