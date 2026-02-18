'use client';

import { useEffect, useRef } from 'react';
import gsap from 'gsap';
import Link from 'next/link';
import {
  Activity,
  AlertTriangle,
  ArrowDownRight,
  ArrowUpRight,
  BarChart3,
  BrainCircuit,
  CheckCircle2,
  ChevronRight,
  Play,
  Plus,
  ShieldCheck,
  Square,
  TrendingUp,
  Zap,
} from 'lucide-react';

import { Badge } from '@/components/ui/badge';
import { PositionTable } from '@/components/trading/position-table';
import { usePositions } from '@/hooks/use-positions';
import { useRiskMetrics } from '@/hooks/use-risk-metrics';
import { useTradingStore } from '@/store/trading-store';
import { useStrategies } from '@/hooks/use-strategies';
import type { Strategy } from '@/types/strategy';

/* ─── Stat card ───────────────────────────────────────────────────────────── */
function StatCard({
  label, value, sub, icon: Icon, trend, accent,
}: {
  label: string; value: string; sub?: string;
  icon: React.ElementType; trend?: 'up' | 'down' | 'neutral'; accent?: 'bull' | 'bear' | 'blue' | 'warning';
}) {
  const accentColor: Record<string, string> = {
    bull: '#26a69a', bear: '#ef5350', blue: '#2962ff', warning: '#f7a600', neutral: 'var(--tv-text-muted)',
  };
  const color = accentColor[accent ?? 'neutral'] ?? accentColor.neutral;

  return (
    <div className="dash-stat metric-card" style={{ opacity: 0 }}>
      <div className="flex items-start justify-between">
        <span className="panel-caption">{label}</span>
        <span className="flex h-7 w-7 items-center justify-center rounded" style={{ background: `${color}18`, color }}>
          <Icon size={14} strokeWidth={1.8} />
        </span>
      </div>
      <div className="flex items-end justify-between gap-2">
        <span className="metric-value" style={{ color }}>{value}</span>
        {trend && (
          <span className="mb-0.5 flex items-center gap-0.5 text-[11px] font-medium"
            style={{ color: trend === 'up' ? '#26a69a' : trend === 'down' ? '#ef5350' : 'var(--tv-text-muted)' }}>
            {trend === 'up' ? <ArrowUpRight size={12} /> : trend === 'down' ? <ArrowDownRight size={12} /> : null}
          </span>
        )}
      </div>
      {sub && <span className="text-[11px]" style={{ color: 'var(--tv-text-muted)' }}>{sub}</span>}
    </div>
  );
}

/* ─── Strategy row ────────────────────────────────────────────────────────── */
function StrategyRow({ s, onToggle }: {
  s: Strategy;
  onToggle: (id: string) => void;
}) {
  const active  = s.status === 'active';
  const signal  = (s.regime_filters?.[0] ?? 'IDLE') as string;
  const symbol  = (s.parameters?.symbol as string) ?? '--';
  const tf      = (s.parameters?.timeframe as string) ?? '--';

  return (
    <div
      className="flex flex-wrap items-center gap-3 px-4 py-3 border-b transition-colors hover:bg-[var(--tv-bg-elevated)]"
      style={{ borderColor: 'var(--tv-border)' }}
    >
      <div className="flex items-center gap-2.5 min-w-[180px] flex-1">
        <span
          className={`h-2 w-2 rounded-full flex-shrink-0 ${active ? 'live-dot' : ''}`}
          style={{ background: active ? '#26a69a' : 'var(--tv-text-muted)' }}
        />
        <div>
          <Link href={`/dashboard/strategies/${s.id}`}>
            <span className="text-[13px] font-semibold hover:underline" style={{ color: 'var(--tv-text-primary)' }}>
              {s.name}
            </span>
          </Link>
          <p className="panel-caption">{s.type}</p>
        </div>
      </div>
      <Badge tone={signal === 'TRENDING' ? 'success' : signal === 'MEAN_REVERTING' ? 'blue' : 'muted'}>
        {signal}
      </Badge>
      <div className="flex items-center gap-4 ml-auto">
        <div className="text-right">
          <p className="panel-caption mb-0.5">Symbol</p>
          <p className="text-[12px] font-mono font-semibold" style={{ color: 'var(--tv-text-primary)' }}>
            {symbol}
          </p>
        </div>
        <div className="text-right hidden sm:block">
          <p className="panel-caption mb-0.5">Timeframe</p>
          <p className="text-[12px] font-mono font-semibold" style={{ color: 'var(--tv-text-primary)' }}>{tf}</p>
        </div>
        <div className="text-right hidden md:block">
          <p className="panel-caption mb-0.5">Status</p>
          <p className="text-[12px] font-mono font-semibold" style={{ color: active ? '#26a69a' : 'var(--tv-text-muted)' }}>
            {active ? 'Running' : 'Inactive'}
          </p>
        </div>
      </div>
      <button
        onClick={() => onToggle(s.id)}
        className="flex items-center gap-1.5 rounded px-2.5 py-1.5 text-[11px] font-semibold transition-all"
        style={active
          ? { background: 'rgba(239,83,80,0.1)', border: '1px solid rgba(239,83,80,0.3)', color: '#ef5350' }
          : { background: 'rgba(38,166,154,0.1)', border: '1px solid rgba(38,166,154,0.3)', color: '#26a69a' }
        }
      >
        {active ? <><Square size={10} /> Stop</> : <><Play size={10} /> Start</>}
      </button>
      <Link href={`/dashboard/strategies/${s.id}`}>
        <ChevronRight size={14} style={{ color: 'var(--tv-text-muted)' }} />
      </Link>
    </div>
  );
}

/* ─── Empty state ─────────────────────────────────────────────────────────── */
function EmptyStrategies() {
  return (
    <div className="py-14 flex flex-col items-center gap-4 text-center">
      <div className="h-14 w-14 rounded-full flex items-center justify-center"
        style={{ background: 'var(--tv-bg-elevated)' }}>
        <BrainCircuit size={24} style={{ color: 'var(--tv-text-muted)' }} />
      </div>
      <div>
        <p className="text-[14px] font-semibold" style={{ color: 'var(--tv-text-primary)' }}>No strategies yet</p>
        <p className="text-[12px] mt-1" style={{ color: 'var(--tv-text-muted)' }}>
          Create your first algorithmic strategy to get started
        </p>
      </div>
      <Link href="/dashboard/strategies/new">
        <button className="tv-btn tv-btn-primary flex items-center gap-1.5">
          <Plus size={13} /> Create Strategy
        </button>
      </Link>
    </div>
  );
}

/* ─── Page ────────────────────────────────────────────────────────────────── */
export default function StrategyDashboardPage() {
  const { positions } = usePositions();
  const { metrics }   = useRiskMetrics();
  const connectRealtime = useTradingStore((state) => state.connectRealtime);
  const { strategies, activateStrategy, deactivateStrategy } = useStrategies();
  const pageRef = useRef<HTMLDivElement>(null);

  useEffect(() => { connectRealtime(); }, [connectRealtime]);

  useEffect(() => {
    if (!pageRef.current) return;
    const ctx = gsap.context(() => {
      const tl = gsap.timeline({ defaults: { ease: 'power3.out' } });
      tl.fromTo('.dash-header',    { opacity: 0, y: -16 },            { opacity: 1, y: 0, duration: 0.5 })
        .fromTo('.dash-stat',      { opacity: 0, y: 24, scale: 0.97 }, { opacity: 1, y: 0, scale: 1, duration: 0.5, stagger: 0.07 }, '-=0.2')
        .fromTo('.dash-secondary', { opacity: 0, y: 20 },              { opacity: 1, y: 0, duration: 0.45, stagger: 0.06 }, '-=0.2')
        .fromTo('.dash-main',      { opacity: 0, y: 28 },              { opacity: 1, y: 0, duration: 0.5 }, '-=0.2')
        .fromTo('.dash-riskbar',   { opacity: 0 },                     { opacity: 1, duration: 0.4 }, '-=0.1');
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

  const drawdown    = (metrics?.drawdown ?? 0) * 100;
  const activeCount = strategies.filter((s) => s.status === 'active').length;

  return (
    <div ref={pageRef} className="space-y-4">

      {/* ── Page header ── */}
      <div className="dash-header flex flex-wrap items-center justify-between gap-3">
        <div>
          <p className="panel-caption mb-1">Algorithmic Trading Platform</p>
          <h1 className="text-[17px] font-semibold tracking-tight" style={{ color: 'var(--tv-text-primary)' }}>
            Strategy Dashboard
          </h1>
        </div>
        <div className="flex items-center gap-2">
          <Badge tone="success" dot>Algo Engine: Armed</Badge>
          <Badge tone="blue">{activeCount} Strategies Running</Badge>
          <Badge>{positions.length} Algo Positions</Badge>
          <Link href="/dashboard/strategies/new">
            <button className="tv-btn tv-btn-primary flex items-center gap-1.5 text-[12px]">
              <Zap size={12} />
              New Strategy
            </button>
          </Link>
        </div>
      </div>

      {/* ── Portfolio stat cards ── */}
      <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
        <StatCard
          label="Open Positions P&L"
          value={positions.length > 0
            ? `${positions.reduce((a, p) => a + p.pnl, 0) >= 0 ? '+' : ''}₹${Math.abs(positions.reduce((a, p) => a + p.pnl, 0)).toLocaleString()}`
            : '—'}
          sub={positions.length > 0 ? `${positions.length} open position${positions.length !== 1 ? 's' : ''}` : 'No open positions'}
          icon={TrendingUp}
          accent={positions.reduce((a, p) => a + p.pnl, 0) >= 0 ? 'bull' : 'bear'}
          trend={positions.reduce((a, p) => a + p.pnl, 0) >= 0 ? 'up' : 'down'}
        />
        <StatCard
          label="Active Strategies"
          value={strategies.length > 0 ? `${activeCount} / ${strategies.length}` : '0 / 0'}
          sub={strategies.length > 0
            ? `${strategies.filter((s) => s.status === 'inactive').length} inactive`
            : 'Create a strategy to begin'}
          icon={BrainCircuit} accent="blue" trend="neutral"
        />
        <StatCard
          label="Portfolio Delta"
          value={`${(metrics?.delta ?? 0) >= 0 ? '+' : ''}${(metrics?.delta ?? 0).toFixed(1)}`}
          sub="Net options exposure" icon={ShieldCheck}
          accent={Math.abs(metrics?.delta ?? 0) < 500 ? 'bull' : 'warning'} trend="neutral"
        />
        <StatCard
          label="Max Drawdown"
          value={`${drawdown.toFixed(2)}%`}
          sub={drawdown < 2 ? 'Within limits' : 'Approaching limit'}
          icon={Activity} accent={drawdown < 2 ? 'bull' : 'warning'} trend={drawdown < 1 ? 'up' : 'down'}
        />
      </div>

      {/* ── Secondary metrics ── */}
      <div className="dash-secondary grid gap-3 xl:grid-cols-3" style={{ opacity: 0 }}>
        <StatCard
          label="Portfolio Delta"
          value={`${(metrics?.delta ?? 0) >= 0 ? '+' : ''}${(metrics?.delta ?? 0).toFixed(1)}`}
          sub="Net options exposure" icon={ShieldCheck}
          accent={Math.abs(metrics?.delta ?? 0) < 500 ? 'bull' : 'warning'} trend="neutral"
        />
        <StatCard
          label="Gamma"
          value={`${(metrics?.gamma ?? 0).toFixed(3)}`}
          sub="Portfolio gamma exposure" icon={BarChart3} accent="blue" trend="neutral"
        />
        <StatCard
          label="Vega"
          value={`${(metrics?.vega ?? 0).toFixed(1)}`}
          sub="Volatility sensitivity" icon={Zap} accent="bull" trend="neutral"
        />
      </div>

      {/* ── Active strategies panel ── */}
      <div className="dash-main tv-panel overflow-hidden" style={{ opacity: 0 }}>
        <div className="flex items-center justify-between px-4 py-3 border-b" style={{ borderColor: 'var(--tv-border)' }}>
          <div className="flex items-center gap-2">
            <BrainCircuit size={15} style={{ color: 'var(--tv-blue)' }} />
            <span className="panel-title">Active Strategies</span>
            {activeCount > 0 && <Badge tone="success" dot>{activeCount} Running</Badge>}
          </div>
          <div className="flex items-center gap-2">
            <Link href="/dashboard/strategies">
              <button className="tv-btn tv-btn-ghost text-[11px] py-1 px-2.5 flex items-center gap-1">
                <BarChart3 size={11} /> Strategy Library
              </button>
            </Link>
            <Link href="/dashboard/strategies/new">
              <button className="tv-btn tv-btn-ghost text-[11px] py-1 px-2.5">+ New</button>
            </Link>
          </div>
        </div>
        {strategies.length === 0
          ? <EmptyStrategies />
          : strategies.map((s) => <StrategyRow key={s.id} s={s} onToggle={handleToggle} />)
        }
      </div>

      {/* ── Algo positions ── */}
      <div className="dash-main" style={{ opacity: 0 }}>
        <PositionTable positions={positions} />
      </div>

      {/* ── Risk bar ── */}
      <div
        className="dash-riskbar rounded-md px-4 py-3 flex flex-wrap items-center justify-between gap-3"
        style={{ opacity: 0, background: 'var(--tv-bg-surface)', border: '1px solid var(--tv-border)' }}
      >
        <div className="flex items-center gap-2">
          <ShieldCheck size={14} style={{ color: metrics?.trading_allowed !== false ? '#26a69a' : '#ef5350' }} />
          <span className="text-[12px] font-medium" style={{ color: 'var(--tv-text-primary)' }}>Risk Status</span>
          <Badge tone={metrics?.trading_allowed !== false ? 'success' : 'danger'} dot>
            {metrics?.trading_allowed !== false ? 'Algo Trading Allowed' : 'Restricted'}
          </Badge>
        </div>
        <div className="flex items-center gap-4">
          {[
            { label: 'Delta', value: (metrics?.delta ?? 0).toFixed(1) },
            { label: 'Gamma', value: (metrics?.gamma ?? 0).toFixed(3) },
            { label: 'Vega',  value: (metrics?.vega  ?? 0).toFixed(1) },
            { label: 'Positions', value: String(positions.length) },
          ].map((g) => (
            <div key={g.label} className="text-center">
              <div className="panel-caption">{g.label}</div>
              <div className="text-[12px] font-mono font-semibold mt-0.5" style={{ color: 'var(--tv-text-primary)' }}>{g.value}</div>
            </div>
          ))}
        </div>
        {metrics?.trading_allowed === false ? (
          <div className="flex items-center gap-1.5 text-[12px]" style={{ color: '#f7a600' }}>
            <AlertTriangle size={13} /> Circuit breaker triggered — all algos halted
          </div>
        ) : (
          <div className="flex items-center gap-1.5 text-[12px]" style={{ color: '#26a69a' }}>
            <CheckCircle2 size={13} /> All systems nominal
          </div>
        )}
      </div>
    </div>
  );
}
