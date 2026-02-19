'use client';

import { useEffect, useRef } from 'react';
import Link from 'next/link';
import gsap from 'gsap';
import {
  BarChart3,
  BrainCircuit,
  CheckCircle2,
  Clock,
  Edit2,
  Filter,
  Play,
  Plus,
  Search,
  Square,
  Trash2,
  TrendingUp,
  Zap,
} from 'lucide-react';
import { Badge } from '@/lib/ui';
import { useStrategies } from '@/hooks/use-strategies';
import { useCopilotStore } from '@/store/copilot-store';
import type { Strategy } from '@/types/strategy';
import { useState } from 'react';

type FilterTab = 'all' | 'active' | 'inactive';

/* ─── Strategy card ───────────────────────────────────────────────────────── */
function StrategyCard({
  s, onToggle, onDelete, onSelect,
}: {
  s: Strategy;
  onToggle: (id: string) => void;
  onDelete: (id: string) => void;
  onSelect: (id: string) => void;
}) {
  const active   = s.status === 'active';
  const symbol   = (s.parameters?.symbol as string)    ?? '--';
  const tf       = (s.parameters?.timeframe as string) ?? '--';
  const maxLoss  = (s.parameters?.max_loss_pct as number) ?? null;
  const createdAt = s.created_at ? s.created_at.split('T')[0] : '--';

  return (
    <div
      className="tv-panel overflow-hidden transition-all hover:border-[var(--tv-border-light)]"
      style={{ borderLeft: `3px solid ${active ? '#26a69a' : 'var(--tv-border)'}` }}
    >
      {/* Header */}
      <div className="px-4 py-3 border-b flex items-start justify-between gap-2" style={{ borderColor: 'var(--tv-border)' }}>
        <div className="min-w-0 flex-1">
          <div className="flex items-center gap-2 mb-0.5">
            <span
              className={`h-2 w-2 rounded-full flex-shrink-0 ${active ? 'live-dot' : ''}`}
              style={{ background: active ? '#26a69a' : 'var(--tv-text-muted)' }}
            />
            <Link href={`/dashboard/strategies/${s.id}`} onClick={() => onSelect(s.id)}>
              <h3 className="text-[13px] font-semibold truncate hover:underline" style={{ color: 'var(--tv-text-primary)' }}>
                {s.name}
              </h3>
            </Link>
          </div>
          <div className="flex items-center gap-1.5 flex-wrap">
            <Badge tone="muted" className="text-[10px]">{s.type}</Badge>
            {symbol !== '--' && <Badge tone="muted" className="text-[10px]">{symbol}</Badge>}
            {tf !== '--' && <Badge tone="muted" className="text-[10px]">{tf}</Badge>}
          </div>
        </div>
        <Badge
          tone={active ? 'success' : 'muted'}
          dot={active}
          className="flex-shrink-0"
        >
          {s.status}
        </Badge>
      </div>

      {/* Details */}
      <div className="px-4 py-3 grid grid-cols-2 gap-2 border-b" style={{ borderColor: 'var(--tv-border)' }}>
        <div className="text-center">
          <p className="panel-caption mb-1">Symbol</p>
          <p className="text-[13px] font-mono font-semibold" style={{ color: 'var(--tv-text-primary)' }}>{symbol}</p>
        </div>
        <div className="text-center">
          <p className="panel-caption mb-1">Timeframe</p>
          <p className="text-[13px] font-mono font-semibold" style={{ color: 'var(--tv-text-primary)' }}>{tf}</p>
        </div>
        {maxLoss !== null && (
          <div className="text-center">
            <p className="panel-caption mb-1">Max Loss %</p>
            <p className="text-[13px] font-mono font-semibold" style={{ color: '#ef5350' }}>{maxLoss}%</p>
          </div>
        )}
        <div className="text-center">
          <p className="panel-caption mb-1">Created</p>
          <p className="text-[13px] font-mono font-semibold" style={{ color: 'var(--tv-text-muted)' }}>{createdAt}</p>
        </div>
      </div>

      {/* Footer */}
      <div className="px-3 py-2.5 flex items-center gap-1.5">
        <div className="flex items-center gap-1 text-[10px]" style={{ color: 'var(--tv-text-muted)' }}>
          <Clock size={10} /> {createdAt}
        </div>
        <div className="flex-1" />
        <Link href={`/dashboard/strategies/${s.id}/builder`}>
          <button className="tv-btn tv-btn-ghost text-[11px] py-1 px-2 flex items-center gap-1">
            <Edit2 size={10} /> Edit
          </button>
        </Link>
        <Link href="/dashboard/backtesting">
          <button className="tv-btn tv-btn-ghost text-[11px] py-1 px-2 flex items-center gap-1">
            <BarChart3 size={10} /> Backtest
          </button>
        </Link>
        <button
          onClick={() => onDelete(s.id)}
          className="tv-btn tv-btn-ghost text-[11px] py-1 px-2"
          style={{ color: '#ef5350' }}
          title="Delete strategy"
        >
          <Trash2 size={10} />
        </button>
        <button
          onClick={() => onToggle(s.id)}
          className="flex items-center gap-1 rounded px-2.5 py-1.5 text-[11px] font-semibold transition-all"
          style={active
            ? { background: 'rgba(239,83,80,0.1)', border: '1px solid rgba(239,83,80,0.3)', color: '#ef5350' }
            : { background: 'rgba(38,166,154,0.1)', border: '1px solid rgba(38,166,154,0.3)', color: '#26a69a' }
          }
        >
          {active ? <><Square size={10} /> Stop</> : <><Play size={10} /> Start</>}
        </button>
      </div>
    </div>
  );
}

/* ─── Page ────────────────────────────────────────────────────────────────── */
export default function StrategiesPage() {
  const { strategies, activateStrategy, deactivateStrategy, deleteStrategy } = useStrategies();
  const { setSelectedStrategy } = useCopilotStore();
  const pageRef = useRef<HTMLDivElement>(null);

  const [search, setSearch]       = useState('');
  const [filterTab, setFilterTab] = useState<FilterTab>('all');

  useEffect(() => {
    if (!pageRef.current) return;
    const ctx = gsap.context(() => {
      gsap.fromTo('.strat-header', { opacity: 0, y: -14 }, { opacity: 1, y: 0, duration: 0.4, ease: 'power3.out' });
      gsap.fromTo('.strat-card',   { opacity: 0, y: 20  }, { opacity: 1, y: 0, duration: 0.4, ease: 'power3.out', stagger: 0.06, delay: 0.1 });
    }, pageRef);
    return () => ctx.revert();
  }, [filterTab]);

  const handleToggle = async (id: string) => {
    const s = strategies.find((st) => st.id === id);
    if (!s) return;
    if (s.status === 'active') {
      await deactivateStrategy(id);
    } else {
      await activateStrategy(id);
    }
  };

  const handleDelete = async (id: string) => {
    await deleteStrategy(id);
  };

  const handleSelect = (id: string) => {
    setSelectedStrategy(id);
  };

  const filtered = strategies
    .filter((s) => filterTab === 'all' ? true : s.status === filterTab)
    .filter((s) => !search || s.name.toLowerCase().includes(search.toLowerCase())
      || ((s.parameters?.symbol as string) ?? '').toLowerCase().includes(search.toLowerCase()));

  const activeCount   = strategies.filter((s) => s.status === 'active').length;
  const inactiveCount = strategies.filter((s) => s.status === 'inactive').length;

  const TABS: { id: FilterTab; label: string; count: number }[] = [
    { id: 'all',      label: 'All',      count: strategies.length },
    { id: 'active',   label: 'Active',   count: activeCount       },
    { id: 'inactive', label: 'Inactive', count: inactiveCount     },
  ];

  return (
    <div ref={pageRef} className="space-y-4">

      {/* Header */}
      <div className="strat-header flex flex-wrap items-center justify-between gap-3">
        <div>
          <p className="panel-caption mb-1">Algorithmic Strategy Management</p>
          <h1 className="text-[17px] font-semibold tracking-tight" style={{ color: 'var(--tv-text-primary)' }}>
            Strategy Library
          </h1>
        </div>
        <div className="flex items-center gap-2">
          {activeCount > 0 && <Badge tone="success" dot>{activeCount} Running</Badge>}
          <Link href="/dashboard/strategies/new">
            <button className="tv-btn tv-btn-primary flex items-center gap-1.5">
              <Plus size={14} /> New Strategy
            </button>
          </Link>
        </div>
      </div>

      {/* Summary row */}
      <div className="strat-header grid grid-cols-2 lg:grid-cols-3 gap-3">
        {[
          { label: 'Total Strategies', value: String(strategies.length), icon: BrainCircuit, color: '#2962ff' },
          { label: 'Active',           value: String(activeCount),       icon: CheckCircle2, color: '#26a69a' },
          { label: 'Inactive',         value: String(inactiveCount),     icon: TrendingUp,   color: '#f7a600' },
        ].map((c) => (
          <div key={c.label} className="metric-card">
            <div className="flex items-center justify-between mb-1">
              <span className="panel-caption">{c.label}</span>
              <c.icon size={13} style={{ color: c.color }} />
            </div>
            <p className="text-[20px] font-bold font-mono" style={{ color: c.color }}>{c.value}</p>
          </div>
        ))}
      </div>

      {/* Toolbar */}
      <div
        className="strat-header rounded-md flex flex-wrap items-center gap-3 px-3 py-2"
        style={{ background: 'var(--tv-bg-surface)', border: '1px solid var(--tv-border)' }}
      >
        {/* Tabs */}
        <div className="tv-tab-bar flex-shrink-0">
          {TABS.map((t) => (
            <button
              key={t.id}
              onClick={() => setFilterTab(t.id)}
              className={`tv-tab${filterTab === t.id ? ' active' : ''}`}
            >
              {t.label}
              <span className="ml-1 rounded-full px-1.5 py-0.5 text-[10px] font-mono"
                style={{ background: 'var(--tv-bg-elevated)', color: 'var(--tv-text-muted)' }}>
                {t.count}
              </span>
            </button>
          ))}
        </div>

        <div className="tv-v-divider h-5" />

        {/* Search */}
        <div className="flex items-center gap-2 flex-1 min-w-[160px]">
          <Search size={13} style={{ color: 'var(--tv-text-muted)', flexShrink: 0 }} />
          <input
            className="bg-transparent outline-none text-[13px] w-full"
            style={{ color: 'var(--tv-text-primary)' }}
            placeholder="Search by name or symbol…"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>

        <button className="tv-btn tv-btn-ghost text-[12px] py-1 px-2.5 flex items-center gap-1.5">
          <Filter size={12} /> Filter
        </button>
      </div>

      {/* Cards */}
      {filtered.length === 0 ? (
        <div className="tv-panel py-16 flex flex-col items-center gap-4 text-center">
          <div className="h-14 w-14 rounded-full flex items-center justify-center"
            style={{ background: 'var(--tv-bg-elevated)' }}>
            <BrainCircuit size={24} style={{ color: 'var(--tv-text-muted)' }} />
          </div>
          <div>
            <p className="text-[14px] font-semibold" style={{ color: 'var(--tv-text-primary)' }}>
              {search ? 'No strategies found' : 'No strategies yet'}
            </p>
            <p className="text-[12px] mt-1" style={{ color: 'var(--tv-text-muted)' }}>
              {search
                ? `No results for "${search}"`
                : 'Create your first algorithmic strategy to get started'}
            </p>
          </div>
          {!search && (
            <Link href="/dashboard/strategies/new">
              <button className="tv-btn tv-btn-primary flex items-center gap-1.5">
                <Plus size={13} /> Create Strategy
              </button>
            </Link>
          )}
        </div>
      ) : (
        <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-3">
          {filtered.map((s) => (
            <div key={s.id} className="strat-card">
              <StrategyCard s={s} onToggle={handleToggle} onDelete={handleDelete} onSelect={handleSelect} />
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
