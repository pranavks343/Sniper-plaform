'use client';

import Link from 'next/link';
import { useEffect, useRef, useState } from 'react';
import gsap from 'gsap';
import {
  ArrowLeft,
  ArrowRight,
  BarChart3,
  CheckCircle2,
  ChevronRight,
  GitBranch,
  Play,
  Save,
  Settings,
  Shield,
  Zap,
} from 'lucide-react';
import { Badge } from '@/lib/ui';
import { useCopilotStore } from '@/store/copilot-store';

/* ─── Node palette data ───────────────────────────────────────────────────── */
const PALETTE = [
  { id: 'ema',    label: 'EMA',            cat: 'indicator', color: '#2962ff', desc: 'Exponential Moving Average' },
  { id: 'sma',    label: 'SMA',            cat: 'indicator', color: '#2962ff', desc: 'Simple Moving Average' },
  { id: 'rsi',    label: 'RSI',            cat: 'indicator', color: '#2962ff', desc: 'Relative Strength Index (14)' },
  { id: 'macd',   label: 'MACD',           cat: 'indicator', color: '#2962ff', desc: 'MACD Histogram' },
  { id: 'bb',     label: 'Bollinger',      cat: 'indicator', color: '#2962ff', desc: 'Bollinger Bands (20,2)' },
  { id: 'atr',    label: 'ATR',            cat: 'indicator', color: '#2962ff', desc: 'Average True Range' },
  { id: 'vwap',   label: 'VWAP',           cat: 'indicator', color: '#2962ff', desc: 'Volume Weighted Avg Price' },
  { id: 'regime', label: 'Market Regime',  cat: 'filter',    color: '#f7a600', desc: 'Trend / Ranging / Volatile' },
  { id: 'vol',    label: 'Volume Filter',  cat: 'filter',    color: '#f7a600', desc: 'Volume > N-period average' },
  { id: 'time',   label: 'Time Filter',    cat: 'filter',    color: '#f7a600', desc: 'Session window filter' },
  { id: 'cross',  label: 'Crossover',      cat: 'condition', color: '#9c27b0', desc: 'A crosses above B' },
  { id: 'thresh', label: 'Threshold',      cat: 'condition', color: '#9c27b0', desc: 'Value > threshold' },
  { id: 'and',    label: 'AND',            cat: 'logic',     color: '#00bcd4', desc: 'All conditions must be true' },
  { id: 'or',     label: 'OR',             cat: 'logic',     color: '#00bcd4', desc: 'Any condition must be true' },
  { id: 'buy',    label: 'Enter Long',     cat: 'action',    color: '#26a69a', desc: 'Open long position' },
  { id: 'sell',   label: 'Enter Short',    cat: 'action',    color: '#ef5350', desc: 'Open short position' },
  { id: 'exit',   label: 'Exit All',       cat: 'action',    color: '#26a69a', desc: 'Close all positions' },
  { id: 'sl',     label: 'Stop Loss',      cat: 'action',    color: '#f7a600', desc: 'Set stop-loss level' },
  { id: 'tp',     label: 'Take Profit',    cat: 'action',    color: '#26a69a', desc: 'Set take-profit level' },
];

const CAT_ORDER = ['indicator', 'filter', 'condition', 'logic', 'action'] as const;
const CAT_LABELS: Record<string, string> = {
  indicator: 'Indicators', filter: 'Filters', condition: 'Conditions', logic: 'Logic', action: 'Actions',
};

type CanvasNode = typeof PALETTE[0] & { uid: string };

type Params = { params: { id: string } };

export default function StrategyBuilderPage({ params }: Params) {
  const { id } = params;
  const pageRef = useRef<HTMLDivElement>(null);
  const [nodes, setNodes] = useState<CanvasNode[]>([]);
  const [selected, setSelected] = useState<CanvasNode | null>(null);
  const [saved, setSaved] = useState(false);
  const { setSelectedStrategy } = useCopilotStore();

  // Set this strategy as the copilot context while editing
  useEffect(() => {
    setSelectedStrategy(id);
    return () => setSelectedStrategy(null);
  }, [id, setSelectedStrategy]);

  useEffect(() => {
    if (!pageRef.current) return;
    const ctx = gsap.context(() => {
      gsap.fromTo('.builder-header', { opacity: 0, y: -14 }, { opacity: 1, y: 0, duration: 0.4, ease: 'power3.out' });
      gsap.fromTo('.builder-body',   { opacity: 0, y: 16  }, { opacity: 1, y: 0, duration: 0.4, ease: 'power3.out', delay: 0.1 });
    }, pageRef);
    return () => ctx.revert();
  }, []);

  const addNode = (p: typeof PALETTE[0]) => {
    const n: CanvasNode = { ...p, uid: `${p.id}-${Date.now()}` };
    setNodes((prev) => [...prev, n]);
    setSelected(n);
  };

  const removeNode = (uid: string) => {
    setNodes((prev) => prev.filter((n) => n.uid !== uid));
    if (selected?.uid === uid) setSelected(null);
  };

  const handleSave = () => {
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
  };

  // Categorised view of canvas
  const grouped = CAT_ORDER.reduce<Record<string, CanvasNode[]>>((acc, cat) => {
    acc[cat] = nodes.filter((n) => n.cat === cat);
    return acc;
  }, {} as Record<string, CanvasNode[]>);

  return (
    <div ref={pageRef} className="flex flex-col h-full gap-4">

      {/* Header */}
      <div className="builder-header flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-3">
          <Link href={`/dashboard/strategies/${id}`}>
            <button className="tv-btn tv-btn-ghost p-2"><ArrowLeft size={14} /></button>
          </Link>
          <div>
            <p className="panel-caption mb-0.5">Strategy Builder</p>
            <h1 className="text-[16px] font-semibold tracking-tight" style={{ color: 'var(--tv-text-primary)' }}>
              Visual Logic Editor
            </h1>
          </div>
          <Badge tone="blue"><GitBranch size={10} className="mr-1" /> Strategy #{id}</Badge>
        </div>
        <div className="flex items-center gap-2">
          <Link href="/dashboard/backtesting">
            <button className="tv-btn tv-btn-ghost flex items-center gap-1.5 text-[12px]">
              <BarChart3 size={12} /> Run Backtest
            </button>
          </Link>
          <button
            onClick={handleSave}
            className="tv-btn tv-btn-primary flex items-center gap-1.5 text-[12px]"
          >
            {saved ? <><CheckCircle2 size={12} /> Saved!</> : <><Save size={12} /> Save Logic</>}
          </button>
        </div>
      </div>

      {/* 3-column builder */}
      <div className="builder-body grid gap-4 lg:grid-cols-4 min-h-[70vh]">

        {/* Palette */}
        <div className="tv-panel overflow-hidden lg:col-span-1 flex flex-col">
          <div className="px-4 py-3 border-b" style={{ borderColor: 'var(--tv-border)' }}>
            <p className="panel-title">Components</p>
            <p className="panel-caption mt-0.5">Click to add to canvas</p>
          </div>
          <div className="flex-1 overflow-y-auto p-3 space-y-3">
            {CAT_ORDER.map((cat) => (
              <div key={cat}>
                <p className="panel-caption mb-1.5 px-1 uppercase tracking-wider text-[9px]">{CAT_LABELS[cat]}</p>
                <div className="space-y-1">
                  {PALETTE.filter((p) => p.cat === cat).map((p) => (
                    <button
                      key={p.id}
                      onClick={() => addNode(p)}
                      title={p.desc}
                      className="w-full flex items-center gap-2 rounded-md px-2.5 py-2 text-[12px] text-left transition-all hover:scale-[1.01] hover:opacity-90"
                      style={{ background: `${p.color}12`, border: `1px solid ${p.color}30`, color: p.color }}
                    >
                      <span className="font-semibold flex-1">{p.label}</span>
                      <span className="text-[10px] opacity-50">+</span>
                    </button>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Canvas */}
        <div className="tv-panel overflow-hidden lg:col-span-2 flex flex-col">
          <div className="px-4 py-3 border-b flex items-center justify-between" style={{ borderColor: 'var(--tv-border)' }}>
            <div className="flex items-center gap-2">
              <p className="panel-title">Logic Canvas</p>
              <Badge tone="muted">{nodes.length} nodes</Badge>
            </div>
            {nodes.length > 0 && (
              <button onClick={() => { setNodes([]); setSelected(null); }}
                className="text-[11px] tv-btn tv-btn-ghost py-1 px-2" style={{ color: '#ef5350' }}>
                Clear
              </button>
            )}
          </div>

          <div className="flex-1 p-4 overflow-y-auto">
            {nodes.length === 0 ? (
              <div className="h-full flex flex-col items-center justify-center gap-3 text-center">
                <div className="h-16 w-16 rounded-full flex items-center justify-center"
                  style={{ background: 'var(--tv-bg-elevated)' }}>
                  <GitBranch size={26} style={{ color: 'var(--tv-text-muted)' }} />
                </div>
                <p className="text-[13px] font-medium" style={{ color: 'var(--tv-text-muted)' }}>
                  Click components to build logic
                </p>
                <p className="text-[11px]" style={{ color: 'var(--tv-text-muted)' }}>
                  Indicators → Conditions → Actions
                </p>
                <div className="flex items-center gap-2 mt-2 text-[11px]" style={{ color: 'var(--tv-text-muted)' }}>
                  <span className="px-2 py-0.5 rounded" style={{ background: 'rgba(41,98,255,0.1)', color: '#2962ff' }}>EMA</span>
                  <ArrowRight size={11} />
                  <span className="px-2 py-0.5 rounded" style={{ background: 'rgba(156,39,176,0.1)', color: '#9c27b0' }}>Crossover</span>
                  <ArrowRight size={11} />
                  <span className="px-2 py-0.5 rounded" style={{ background: 'rgba(38,166,154,0.1)', color: '#26a69a' }}>Enter Long</span>
                </div>
              </div>
            ) : (
              <div className="space-y-4">
                {/* Flow pipeline */}
                {CAT_ORDER.map((cat) => {
                  const catNodes = grouped[cat];
                  if (!catNodes.length) return null;
                  const colors: Record<string, string> = {
                    indicator: '#2962ff', filter: '#f7a600', condition: '#9c27b0', logic: '#00bcd4', action: '#26a69a',
                  };
                  const color = colors[cat];
                  return (
                    <div key={cat}>
                      <p className="text-[10px] uppercase tracking-widest font-semibold mb-2" style={{ color }}>{CAT_LABELS[cat]}</p>
                      <div className="flex flex-wrap gap-2">
                        {catNodes.map((n) => (
                          <button
                            key={n.uid}
                            onClick={() => setSelected(n)}
                            className="flex items-center gap-1.5 rounded-md px-2.5 py-1.5 text-[11px] font-semibold transition-all hover:brightness-110"
                            style={{
                              background: `${n.color}15`,
                              border: `1px solid ${selected?.uid === n.uid ? n.color : `${n.color}40`}`,
                              color: n.color,
                              boxShadow: selected?.uid === n.uid ? `0 0 0 2px ${n.color}30` : 'none',
                            }}
                          >
                            {n.label}
                            <span
                              onClick={(e) => { e.stopPropagation(); removeNode(n.uid); }}
                              className="opacity-40 hover:opacity-100 cursor-pointer"
                            >✕</span>
                          </button>
                        ))}
                      </div>
                      {cat !== 'action' && <div className="mt-3 flex items-center gap-2">
                        <div className="flex-1 border-t border-dashed" style={{ borderColor: 'var(--tv-border)' }} />
                        <ArrowRight size={11} style={{ color: 'var(--tv-text-muted)' }} />
                        <div className="flex-1 border-t border-dashed" style={{ borderColor: 'var(--tv-border)' }} />
                      </div>}
                    </div>
                  );
                })}

                {/* Pseudocode */}
                {nodes.some((n) => n.cat === 'action') && (
                  <div className="rounded-md p-3 mt-2" style={{ background: 'var(--tv-bg-base)', border: '1px solid var(--tv-border)' }}>
                    <p className="panel-caption mb-2">Generated Pseudocode</p>
                    <pre className="text-[11px] font-mono whitespace-pre-wrap leading-relaxed" style={{ color: '#26a69a' }}>
{`if (${grouped.condition.map((n) => `${n.label}()`).join(' AND ') || '# conditions'}):
    ${grouped.action.map((n) => n.label).join(', ')}
    risk: SL=${grouped.action.some((n) => n.id === 'sl') ? 'ATR×1.5' : 'none'}, TP=${grouped.action.some((n) => n.id === 'tp') ? 'ATR×3' : 'none'}`}
                    </pre>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>

        {/* Properties + actions */}
        <div className="space-y-4 lg:col-span-1">
          {/* Properties */}
          <div className="tv-panel overflow-hidden flex-1">
            <div className="px-4 py-3 border-b" style={{ borderColor: 'var(--tv-border)' }}>
              <p className="panel-title flex items-center gap-2">
                <Settings size={13} /> Node Properties
              </p>
            </div>
            <div className="p-4">
              {selected ? (
                <div className="space-y-3">
                  <div className="flex items-center gap-2">
                    <span className="rounded px-2 py-1 text-[12px] font-semibold"
                      style={{ background: `${selected.color}15`, color: selected.color, border: `1px solid ${selected.color}30` }}>
                      {selected.label}
                    </span>
                    <Badge tone="muted">{CAT_LABELS[selected.cat]}</Badge>
                  </div>
                  <p className="text-[11px]" style={{ color: 'var(--tv-text-muted)' }}>{selected.desc}</p>

                  {/* Dynamic parameter inputs */}
                  {selected.id === 'ema' && <>
                    <div>
                      <label className="panel-caption mb-1 block">Period</label>
                      <input type="number" className="tv-input w-full" defaultValue={20} />
                    </div>
                    <div>
                      <label className="panel-caption mb-1 block">Apply To</label>
                      <select className="tv-select w-full"><option>Close</option><option>Open</option><option>High</option><option>Low</option></select>
                    </div>
                  </>}
                  {selected.id === 'rsi' && <>
                    <div>
                      <label className="panel-caption mb-1 block">Period</label>
                      <input type="number" className="tv-input w-full" defaultValue={14} />
                    </div>
                    <div>
                      <label className="panel-caption mb-1 block">Overbought</label>
                      <input type="number" className="tv-input w-full" defaultValue={70} />
                    </div>
                    <div>
                      <label className="panel-caption mb-1 block">Oversold</label>
                      <input type="number" className="tv-input w-full" defaultValue={30} />
                    </div>
                  </>}
                  {selected.id === 'sl' && <>
                    <div>
                      <label className="panel-caption mb-1 block">Stop Type</label>
                      <select className="tv-select w-full"><option>ATR Multiple</option><option>Fixed %</option><option>Swing High/Low</option></select>
                    </div>
                    <div>
                      <label className="panel-caption mb-1 block">ATR Multiple</label>
                      <input type="number" className="tv-input w-full" defaultValue={1.5} step={0.1} />
                    </div>
                  </>}
                  {selected.id === 'tp' && <>
                    <div>
                      <label className="panel-caption mb-1 block">Target Type</label>
                      <select className="tv-select w-full"><option>ATR Multiple</option><option>Risk:Reward</option><option>Fixed %</option></select>
                    </div>
                    <div>
                      <label className="panel-caption mb-1 block">ATR Multiple</label>
                      <input type="number" className="tv-input w-full" defaultValue={3} step={0.5} />
                    </div>
                  </>}
                  {['buy','sell','exit'].includes(selected.id) && (
                    <div>
                      <label className="panel-caption mb-1 block">Position Size</label>
                      <select className="tv-select w-full">
                        <option>1 Lot</option><option>2 Lots</option><option>Fixed ₹1L</option><option>2% Capital</option>
                      </select>
                    </div>
                  )}
                  {!['ema','rsi','sl','tp','buy','sell','exit'].includes(selected.id) && (
                    <p className="text-[11px]" style={{ color: 'var(--tv-text-muted)' }}>
                      Default parameters applied. Click to customise.
                    </p>
                  )}
                </div>
              ) : (
                <p className="text-[12px]" style={{ color: 'var(--tv-text-muted)' }}>
                  Click a node on the canvas to view and edit its parameters.
                </p>
              )}
            </div>
          </div>

          {/* Quick actions */}
          <div className="tv-panel p-4 space-y-2">
            <p className="panel-title mb-2">Quick Actions</p>
            <Link href="/dashboard/backtesting" className="block">
              <button className="w-full tv-btn tv-btn-ghost text-[12px] flex items-center gap-2 justify-start py-2">
                <BarChart3 size={12} style={{ color: '#2962ff' }} /> Run Backtest
              </button>
            </Link>
            <button onClick={handleSave} className="w-full tv-btn tv-btn-ghost text-[12px] flex items-center gap-2 justify-start py-2">
              <Save size={12} style={{ color: '#26a69a' }} /> Save Strategy
            </button>
            <Link href="/dashboard/strategies" className="block">
              <button className="w-full tv-btn tv-btn-ghost text-[12px] flex items-center gap-2 justify-start py-2">
                <ChevronRight size={12} /> Strategy Library
              </button>
            </Link>
            <div className="mt-3 rounded-md p-3" style={{ background: 'rgba(38,166,154,0.06)', border: '1px solid rgba(38,166,154,0.15)' }}>
              <div className="flex items-center gap-1.5 mb-1">
                <Shield size={11} style={{ color: '#26a69a' }} />
                <span className="text-[11px] font-semibold" style={{ color: '#26a69a' }}>Algo Only</span>
              </div>
              <p className="text-[10px]" style={{ color: 'var(--tv-text-muted)' }}>
                This strategy executes fully automatically. No manual order placement.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
