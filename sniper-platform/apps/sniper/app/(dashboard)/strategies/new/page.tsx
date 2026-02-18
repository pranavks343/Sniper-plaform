'use client';

import { useEffect, useRef, useState } from 'react';
import { useRouter } from 'next/navigation';
import gsap from 'gsap';
import Link from 'next/link';
import {
  ArrowLeft,
  ArrowRight,
  BarChart3,
  BrainCircuit,
  CheckCircle2,
  ChevronDown,
  Clock,
  GitBranch,
  Layers,
  Settings,
  Shield,
  TrendingUp,
  Zap,
} from 'lucide-react';
import { Badge } from '@sniper/framework';
import { useStrategies } from '@/hooks/use-strategies';

/* ─── Types ───────────────────────────────────────────────────────────────── */
type Step = 'meta' | 'builder' | 'risk' | 'review';

const INDICATOR_NODES = [
  { id: 'ema',     label: 'EMA',             category: 'indicator', description: 'Exponential Moving Average' },
  { id: 'sma',     label: 'SMA',             category: 'indicator', description: 'Simple Moving Average' },
  { id: 'rsi',     label: 'RSI',             category: 'indicator', description: 'Relative Strength Index' },
  { id: 'macd',    label: 'MACD',            category: 'indicator', description: 'MACD Oscillator' },
  { id: 'bb',      label: 'Bollinger Bands', category: 'indicator', description: 'Volatility bands' },
  { id: 'atr',     label: 'ATR',             category: 'indicator', description: 'Average True Range' },
  { id: 'adx',     label: 'ADX',             category: 'indicator', description: 'Trend strength' },
  { id: 'vwap',    label: 'VWAP',            category: 'indicator', description: 'Volume Weighted Avg Price' },
  { id: 'regime',  label: 'Market Regime',   category: 'filter',    description: 'Trend / Ranging / Volatile' },
  { id: 'volume',  label: 'Volume Filter',   category: 'filter',    description: 'Above average volume' },
  { id: 'time',    label: 'Time Filter',     category: 'filter',    description: 'Trading session window' },
  { id: 'cross',   label: 'Crossover',       category: 'condition', description: 'A crosses above/below B' },
  { id: 'thresh',  label: 'Threshold',       category: 'condition', description: 'Value > / < threshold' },
  { id: 'and',     label: 'AND Gate',        category: 'logic',     description: 'All conditions true' },
  { id: 'or',      label: 'OR Gate',         category: 'logic',     description: 'Any condition true' },
  { id: 'buy',     label: 'Enter Long',      category: 'action',    description: 'Open long position' },
  { id: 'sell',    label: 'Enter Short',     category: 'action',    description: 'Open short position' },
  { id: 'exit',    label: 'Exit Position',   category: 'action',    description: 'Close existing position' },
  { id: 'sl',      label: 'Stop Loss',       category: 'action',    description: 'Set stop loss level' },
  { id: 'tp',      label: 'Take Profit',     category: 'action',    description: 'Set take profit level' },
];

const CATEGORY_META: Record<string, { label: string; color: string; bg: string }> = {
  indicator: { label: 'Indicators',  color: '#2962ff', bg: 'rgba(41,98,255,0.1)'  },
  filter:    { label: 'Filters',     color: '#f7a600', bg: 'rgba(247,166,0,0.1)'  },
  condition: { label: 'Conditions',  color: '#9c27b0', bg: 'rgba(156,39,176,0.1)' },
  logic:     { label: 'Logic',       color: '#00bcd4', bg: 'rgba(0,188,212,0.1)'  },
  action:    { label: 'Actions',     color: '#26a69a', bg: 'rgba(38,166,154,0.1)' },
};

/* ─── Canvas node ─────────────────────────────────────────────────────────── */
function CanvasNode({ node, onRemove }: {
  node: typeof INDICATOR_NODES[0] & { canvasId: string };
  onRemove: (id: string) => void;
}) {
  const meta = CATEGORY_META[node.category];
  return (
    <div
      className="flex items-center gap-2 rounded-md px-3 py-2 text-[12px] font-medium select-none cursor-default"
      style={{ background: meta.bg, border: `1px solid ${meta.color}33`, color: meta.color }}
    >
      <span>{node.label}</span>
      <button
        onClick={() => onRemove(node.canvasId)}
        className="ml-1 opacity-50 hover:opacity-100 text-[10px] leading-none"
      >✕</button>
    </div>
  );
}

/* ─── Steps ───────────────────────────────────────────────────────────────── */
const STEPS: { id: Step; label: string; icon: React.ElementType }[] = [
  { id: 'meta',    label: 'Setup',    icon: Settings     },
  { id: 'builder', label: 'Builder',  icon: GitBranch    },
  { id: 'risk',    label: 'Risk',     icon: Shield       },
  { id: 'review',  label: 'Review',   icon: CheckCircle2 },
];

/* ─── Page ────────────────────────────────────────────────────────────────── */
export default function NewStrategyPage() {
  const router   = useRouter();
  const pageRef  = useRef<HTMLDivElement>(null);
  const { createStrategy } = useStrategies();

  const [step, setStep]   = useState<Step>('meta');
  const [name, setName]   = useState('');
  const [type, setType]   = useState('momentum');
  const [symbol, setSymbol] = useState('NIFTY');
  const [timeframe, setTimeframe] = useState('5m');
  const [canvasNodes, setCanvasNodes] = useState<(typeof INDICATOR_NODES[0] & { canvasId: string })[]>([]);
  const [maxLoss, setMaxLoss]   = useState('2');
  const [maxPos, setMaxPos]     = useState('1');
  const [trailSl, setTrailSl]   = useState(true);

  useEffect(() => {
    if (!pageRef.current) return;
    const ctx = gsap.context(() => {
      gsap.fromTo('.strategy-new-header', { opacity: 0, y: -14 }, { opacity: 1, y: 0, duration: 0.5, ease: 'power3.out' });
      gsap.fromTo('.strategy-new-body',   { opacity: 0, y: 20  }, { opacity: 1, y: 0, duration: 0.5, ease: 'power3.out', delay: 0.1 });
    }, pageRef);
    return () => ctx.revert();
  }, []);

  const addToCanvas = (node: typeof INDICATOR_NODES[0]) =>
    setCanvasNodes((prev) => [...prev, { ...node, canvasId: `${node.id}-${Date.now()}` }]);

  const removeFromCanvas = (canvasId: string) =>
    setCanvasNodes((prev) => prev.filter((n) => n.canvasId !== canvasId));

  const currentStepIdx = STEPS.findIndex((s) => s.id === step);

  const handleSave = async () => {
    await createStrategy({ name: name || 'Untitled Strategy', type, parameters: { symbol, timeframe, max_loss_pct: +maxLoss, max_positions: +maxPos, trailing_sl: trailSl } });
    router.push('/dashboard/strategies');
  };

  return (
    <div ref={pageRef} className="space-y-4">

      {/* Header */}
      <div className="strategy-new-header flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-3">
          <Link href="/dashboard/strategies">
            <button className="tv-btn tv-btn-ghost p-2"><ArrowLeft size={14} /></button>
          </Link>
          <div>
            <p className="panel-caption mb-0.5">Strategy Builder</p>
            <h1 className="text-[17px] font-semibold tracking-tight" style={{ color: 'var(--tv-text-primary)' }}>
              Create New Strategy
            </h1>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <Badge tone="blue">
            <BrainCircuit size={10} className="mr-1" />
            Visual Builder
          </Badge>
        </div>
      </div>

      {/* Step progress */}
      <div className="strategy-new-body tv-panel px-4 py-3">
        <div className="flex items-center gap-0">
          {STEPS.map((s, i) => {
            const done    = i < currentStepIdx;
            const current = i === currentStepIdx;
            const Icon    = s.icon;
            return (
              <div key={s.id} className="flex items-center">
                <button
                  onClick={() => i <= currentStepIdx && setStep(s.id)}
                  className="flex items-center gap-1.5 rounded px-3 py-1.5 text-[12px] font-medium transition-colors"
                  style={{
                    color:      current ? '#2962ff' : done ? '#26a69a' : 'var(--tv-text-muted)',
                    background: current ? 'rgba(41,98,255,0.1)' : 'transparent',
                    cursor:     i <= currentStepIdx ? 'pointer' : 'default',
                  }}
                >
                  {done ? <CheckCircle2 size={13} /> : <Icon size={13} />}
                  {s.label}
                </button>
                {i < STEPS.length - 1 && (
                  <ChevronDown size={12} style={{ color: 'var(--tv-text-muted)', transform: 'rotate(-90deg)' }} />
                )}
              </div>
            );
          })}
        </div>
      </div>

      {/* ── Step: Setup ── */}
      {step === 'meta' && (
        <div className="strategy-new-body grid gap-4 lg:grid-cols-2">
          <div className="tv-panel p-5 space-y-4">
            <h2 className="panel-title">Strategy Details</h2>
            <div className="space-y-3">
              <div>
                <label className="panel-caption mb-1.5 block">Strategy Name</label>
                <input
                  className="tv-input w-full"
                  placeholder="e.g. Iron Condor NIFTY Weekly"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                />
              </div>
              <div>
                <label className="panel-caption mb-1.5 block">Strategy Type</label>
                <select className="tv-select w-full" value={type} onChange={(e) => setType(e.target.value)}>
                  <option value="momentum">Momentum</option>
                  <option value="mean_reversion">Mean Reversion</option>
                  <option value="options_sell">Options Selling</option>
                  <option value="pairs">Pairs Trading</option>
                  <option value="scalping">Scalping</option>
                  <option value="swing">Swing Trading</option>
                </select>
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="panel-caption mb-1.5 block">Symbol</label>
                  <select className="tv-select w-full" value={symbol} onChange={(e) => setSymbol(e.target.value)}>
                    <option>NIFTY</option>
                    <option>BANKNIFTY</option>
                    <option>FINNIFTY</option>
                    <option>SENSEX</option>
                    <option>RELIANCE</option>
                  </select>
                </div>
                <div>
                  <label className="panel-caption mb-1.5 block">Timeframe</label>
                  <select className="tv-select w-full" value={timeframe} onChange={(e) => setTimeframe(e.target.value)}>
                    {['1m','3m','5m','15m','30m','1h','4h','1d'].map((tf) => (
                      <option key={tf}>{tf}</option>
                    ))}
                  </select>
                </div>
              </div>
            </div>
          </div>

          <div className="tv-panel p-5 space-y-4">
            <h2 className="panel-title">Quick Templates</h2>
            {[
              { name: 'EMA Crossover',     desc: 'Classic trend-following with dual EMA',        icon: TrendingUp, color: '#26a69a' },
              { name: 'RSI Mean Revert',   desc: 'Fade extremes with RSI + Bollinger Bands',     icon: BarChart3,  color: '#2962ff' },
              { name: 'VWAP Momentum',     desc: 'Trade price bounces off VWAP with volume',     icon: Zap,        color: '#f7a600' },
              { name: 'Options Iron Condor', desc: 'Sell strangle + hedge with wings',           icon: Layers,     color: '#9c27b0' },
            ].map((t) => (
              <button
                key={t.name}
                onClick={() => setName(t.name)}
                className="w-full flex items-center gap-3 rounded-md px-3 py-2.5 text-left transition-colors hover:bg-[var(--tv-bg-elevated)]"
                style={{ border: '1px solid var(--tv-border)' }}
              >
                <span className="flex h-8 w-8 items-center justify-center rounded flex-shrink-0"
                  style={{ background: `${t.color}18`, color: t.color }}>
                  <t.icon size={14} />
                </span>
                <div>
                  <p className="text-[12px] font-semibold" style={{ color: 'var(--tv-text-primary)' }}>{t.name}</p>
                  <p className="text-[11px]" style={{ color: 'var(--tv-text-muted)' }}>{t.desc}</p>
                </div>
              </button>
            ))}
          </div>
        </div>
      )}

      {/* ── Step: Builder ── */}
      {step === 'builder' && (
        <div className="strategy-new-body grid gap-4 lg:grid-cols-4">
          {/* Palette */}
          <div className="tv-panel overflow-hidden lg:col-span-1">
            <div className="px-4 py-3 border-b" style={{ borderColor: 'var(--tv-border)' }}>
              <span className="panel-title">Component Palette</span>
            </div>
            <div className="p-3 space-y-3 overflow-y-auto max-h-[60vh]">
              {Object.entries(CATEGORY_META).map(([cat, meta]) => (
                <div key={cat}>
                  <p className="panel-caption mb-1.5 px-1">{meta.label}</p>
                  <div className="space-y-1">
                    {INDICATOR_NODES.filter((n) => n.category === cat).map((n) => (
                      <button
                        key={n.id}
                        onClick={() => addToCanvas(n)}
                        className="w-full flex items-center gap-2 rounded px-2.5 py-2 text-[12px] text-left transition-all hover:scale-[1.01]"
                        style={{ background: meta.bg, border: `1px solid ${meta.color}33`, color: meta.color }}
                        title={n.description}
                      >
                        <span className="font-semibold">{n.label}</span>
                        <span className="text-[10px] opacity-60 ml-auto">+</span>
                      </button>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Canvas */}
          <div className="tv-panel overflow-hidden lg:col-span-2">
            <div className="px-4 py-3 border-b flex items-center justify-between" style={{ borderColor: 'var(--tv-border)' }}>
              <span className="panel-title">Logic Canvas</span>
              <Badge tone="muted">{canvasNodes.length} nodes</Badge>
            </div>
            <div className="p-4 min-h-[52vh] relative">
              {canvasNodes.length === 0 ? (
                <div className="absolute inset-0 flex flex-col items-center justify-center gap-3 text-center">
                  <div className="h-16 w-16 rounded-full flex items-center justify-center"
                    style={{ background: 'var(--tv-bg-elevated)' }}>
                    <GitBranch size={24} style={{ color: 'var(--tv-text-muted)' }} />
                  </div>
                  <p className="text-[13px] font-medium" style={{ color: 'var(--tv-text-muted)' }}>
                    Click components from the palette
                  </p>
                  <p className="text-[11px]" style={{ color: 'var(--tv-text-muted)' }}>
                    Build your algo logic visually
                  </p>
                </div>
              ) : (
                <div>
                  {/* Flow visualization */}
                  <div className="flex flex-col gap-3">
                    {/* Group by category for a pipeline view */}
                    {(['indicator','filter','condition','logic','action'] as const).map((cat) => {
                      const nodes = canvasNodes.filter((n) => n.category === cat);
                      if (!nodes.length) return null;
                      const meta = CATEGORY_META[cat];
                      return (
                        <div key={cat}>
                          <p className="text-[10px] uppercase tracking-widest mb-1.5" style={{ color: meta.color }}>{meta.label}</p>
                          <div className="flex flex-wrap gap-2">
                            {nodes.map((n) => <CanvasNode key={n.canvasId} node={n} onRemove={removeFromCanvas} />)}
                          </div>
                          {cat !== 'action' && nodes.length > 0 && (
                            <div className="my-2 flex items-center gap-2">
                              <div className="flex-1 border-t border-dashed" style={{ borderColor: 'var(--tv-border)' }} />
                              <ArrowRight size={12} style={{ color: 'var(--tv-text-muted)' }} />
                              <div className="flex-1 border-t border-dashed" style={{ borderColor: 'var(--tv-border)' }} />
                            </div>
                          )}
                        </div>
                      );
                    })}
                  </div>

                  {/* Generated pseudocode */}
                  <div className="mt-4 rounded-md p-3" style={{ background: 'var(--tv-bg-base)', border: '1px solid var(--tv-border)' }}>
                    <p className="panel-caption mb-2">Generated Logic</p>
                    <pre className="text-[11px] font-mono whitespace-pre-wrap" style={{ color: '#26a69a' }}>
{canvasNodes
  .filter((n) => n.category === 'condition' || n.category === 'logic')
  .map((n) => `${n.label}(...)`)
  .join(' AND ') || '# Add conditions'}
{'\n→ '}
{canvasNodes.filter((n) => n.category === 'action').map((n) => n.label).join(', ') || '# Add actions'}
                    </pre>
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Properties */}
          <div className="tv-panel overflow-hidden lg:col-span-1">
            <div className="px-4 py-3 border-b" style={{ borderColor: 'var(--tv-border)' }}>
              <span className="panel-title">Properties</span>
            </div>
            <div className="p-4 space-y-4">
              {canvasNodes.length === 0 ? (
                <p className="text-[12px]" style={{ color: 'var(--tv-text-muted)' }}>Select a node to edit its parameters</p>
              ) : (
                <div className="space-y-3">
                  <p className="text-[12px]" style={{ color: 'var(--tv-text-muted)' }}>
                    {canvasNodes.length} components added. Configure parameters:
                  </p>
                  {canvasNodes.filter((n) => ['ema','sma','rsi'].includes(n.id)).slice(0,2).map((n) => (
                    <div key={n.canvasId}>
                      <label className="panel-caption mb-1 block">{n.label} Period</label>
                      <input type="number" className="tv-input w-full" defaultValue={n.id === 'rsi' ? 14 : 20} />
                    </div>
                  ))}
                  <div>
                    <label className="panel-caption mb-1 block">Position Size</label>
                    <select className="tv-select w-full">
                      <option>1 Lot</option>
                      <option>2 Lots</option>
                      <option>Fixed ₹1L</option>
                      <option>2% Capital</option>
                    </select>
                  </div>
                </div>
              )}

              <div className="pt-2 border-t" style={{ borderColor: 'var(--tv-border)' }}>
                <p className="panel-caption mb-2">Quick Info</p>
                {[
                  { label: 'Symbol',    value: symbol },
                  { label: 'Timeframe', value: timeframe },
                  { label: 'Type',      value: type },
                  { label: 'Nodes',     value: String(canvasNodes.length) },
                ].map((r) => (
                  <div key={r.label} className="flex justify-between py-1 text-[12px]">
                    <span style={{ color: 'var(--tv-text-muted)' }}>{r.label}</span>
                    <span className="font-mono" style={{ color: 'var(--tv-text-primary)' }}>{r.value}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* ── Step: Risk ── */}
      {step === 'risk' && (
        <div className="strategy-new-body grid gap-4 lg:grid-cols-2">
          <div className="tv-panel p-5 space-y-4">
            <h2 className="panel-title flex items-center gap-2">
              <Shield size={14} style={{ color: '#f7a600' }} /> Risk Parameters
            </h2>
            <div className="space-y-3">
              {[
                { label: 'Max Loss per Day (%)', value: maxLoss, setter: setMaxLoss, type: 'number', hint: 'Strategy auto-stops if daily loss exceeds this' },
                { label: 'Max Open Positions',   value: maxPos,  setter: setMaxPos,  type: 'number', hint: 'Maximum concurrent positions this algo can hold' },
              ].map((f) => (
                <div key={f.label}>
                  <label className="panel-caption mb-1.5 block">{f.label}</label>
                  <input
                    type={f.type}
                    className="tv-input w-full"
                    value={f.value}
                    onChange={(e) => f.setter(e.target.value)}
                  />
                  <p className="text-[11px] mt-1" style={{ color: 'var(--tv-text-muted)' }}>{f.hint}</p>
                </div>
              ))}
              <div>
                <label className="panel-caption mb-1.5 block">Stop Loss Type</label>
                <select className="tv-select w-full">
                  <option>Fixed %</option>
                  <option>ATR Multiple</option>
                  <option>Swing Low/High</option>
                </select>
              </div>
              <div className="flex items-center justify-between py-2 px-3 rounded" style={{ background: 'var(--tv-bg-elevated)' }}>
                <div>
                  <p className="text-[12px] font-medium" style={{ color: 'var(--tv-text-primary)' }}>Trailing Stop Loss</p>
                  <p className="text-[11px]" style={{ color: 'var(--tv-text-muted)' }}>Auto-trail SL to lock profits</p>
                </div>
                <button
                  onClick={() => setTrailSl((v) => !v)}
                  className="rounded-full transition-colors px-1"
                  style={{
                    background: trailSl ? '#26a69a' : 'var(--tv-border)',
                    width: 40, height: 22, position: 'relative',
                  }}
                >
                  <span
                    className="absolute top-[3px] rounded-full bg-white transition-all"
                    style={{ width: 16, height: 16, left: trailSl ? 21 : 3 }}
                  />
                </button>
              </div>
            </div>
          </div>

          <div className="tv-panel p-5 space-y-4">
            <h2 className="panel-title flex items-center gap-2">
              <Clock size={14} style={{ color: '#2962ff' }} /> Session & Limits
            </h2>
            <div className="space-y-3">
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="panel-caption mb-1.5 block">Session Start</label>
                  <input type="time" className="tv-input w-full" defaultValue="09:15" />
                </div>
                <div>
                  <label className="panel-caption mb-1.5 block">Session End</label>
                  <input type="time" className="tv-input w-full" defaultValue="15:20" />
                </div>
              </div>
              <div>
                <label className="panel-caption mb-1.5 block">Square-off Time</label>
                <input type="time" className="tv-input w-full" defaultValue="15:25" />
                <p className="text-[11px] mt-1" style={{ color: 'var(--tv-text-muted)' }}>Force-exit all positions before market close</p>
              </div>
              <div>
                <label className="panel-caption mb-1.5 block">Max Trades per Day</label>
                <input type="number" className="tv-input w-full" defaultValue={10} />
              </div>
              <div className="rounded-md p-3" style={{ background: 'rgba(38,166,154,0.08)', border: '1px solid rgba(38,166,154,0.2)' }}>
                <div className="flex items-center gap-2 mb-1">
                  <Shield size={12} style={{ color: '#26a69a' }} />
                  <span className="text-[12px] font-semibold" style={{ color: '#26a69a' }}>Risk Engine Integration</span>
                </div>
                <p className="text-[11px]" style={{ color: 'var(--tv-text-muted)' }}>
                  Circuit breaker will override these settings if portfolio-level limits are breached.
                </p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* ── Step: Review ── */}
      {step === 'review' && (
        <div className="strategy-new-body grid gap-4 lg:grid-cols-3">
          <div className="tv-panel p-5 lg:col-span-2 space-y-4">
            <h2 className="panel-title">Strategy Summary</h2>
            {[
              { label: 'Name',        value: name || 'Untitled Strategy' },
              { label: 'Type',        value: type },
              { label: 'Symbol',      value: symbol },
              { label: 'Timeframe',   value: timeframe },
              { label: 'Components',  value: `${canvasNodes.length} nodes` },
              { label: 'Max Loss',    value: `${maxLoss}% per day` },
              { label: 'Max Pos.',    value: `${maxPos} positions` },
              { label: 'Trailing SL', value: trailSl ? 'Enabled' : 'Disabled' },
            ].map((r) => (
              <div key={r.label} className="flex items-center justify-between py-2 border-b" style={{ borderColor: 'var(--tv-border)' }}>
                <span className="text-[12px]" style={{ color: 'var(--tv-text-muted)' }}>{r.label}</span>
                <span className="text-[13px] font-semibold" style={{ color: 'var(--tv-text-primary)' }}>{r.value}</span>
              </div>
            ))}
          </div>
          <div className="tv-panel p-5 space-y-4">
            <h2 className="panel-title">Next Steps</h2>
            {[
              { icon: BarChart3,  label: 'Run Backtest',      desc: 'Validate on historical data before going live', color: '#2962ff' },
              { icon: Zap,        label: 'Activate Strategy', desc: 'Enable the algo to trade autonomously',         color: '#26a69a' },
              { icon: TrendingUp, label: 'Monitor Dashboard', desc: 'Watch P&L and positions in real-time',          color: '#f7a600' },
            ].map((item) => (
              <div key={item.label} className="flex gap-3 py-2">
                <span className="flex h-8 w-8 items-center justify-center rounded flex-shrink-0"
                  style={{ background: `${item.color}18`, color: item.color }}>
                  <item.icon size={14} />
                </span>
                <div>
                  <p className="text-[12px] font-semibold" style={{ color: 'var(--tv-text-primary)' }}>{item.label}</p>
                  <p className="text-[11px]" style={{ color: 'var(--tv-text-muted)' }}>{item.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Navigation */}
      <div className="flex items-center justify-between gap-3">
        <button
          onClick={() => setStep(STEPS[Math.max(0, currentStepIdx - 1)].id)}
          disabled={currentStepIdx === 0}
          className="tv-btn tv-btn-ghost flex items-center gap-1.5 disabled:opacity-40"
        >
          <ArrowLeft size={13} /> Back
        </button>
        <div className="flex items-center gap-2">
          {step === 'review' ? (
            <>
              <Link href={`/dashboard/backtesting`}>
                <button className="tv-btn tv-btn-ghost flex items-center gap-1.5">
                  <BarChart3 size={13} /> Save &amp; Backtest
                </button>
              </Link>
              <button onClick={handleSave} className="tv-btn tv-btn-primary flex items-center gap-1.5">
                <CheckCircle2 size={13} /> Save Strategy
              </button>
            </>
          ) : (
            <button
              onClick={() => setStep(STEPS[Math.min(STEPS.length - 1, currentStepIdx + 1)].id)}
              className="tv-btn tv-btn-primary flex items-center gap-1.5"
            >
              Continue <ArrowRight size={13} />
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
