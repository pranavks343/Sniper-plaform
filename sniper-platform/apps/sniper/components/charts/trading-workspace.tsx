'use client';

import dynamic from 'next/dynamic';
import { useRef, useState, useMemo, useCallback } from 'react';
import { GripVertical, Loader2, RotateCcw, Search, X } from 'lucide-react';

import { useTradingFeed } from '@/hooks/use-trading-feed';
import { clamp } from '@/lib/ui';
import type { OverlayVisibility, WorkspacePanel } from '@/types/chart';

import { MultiSeriesLineChart } from './multi-series-line-chart';

const AdvancedTradingChart = dynamic(
  () => import('./advanced-trading-chart').then((m) => ({ default: m.AdvancedTradingChart })),
  {
    ssr: false,
    loading: () => (
      <div className="flex h-full items-center justify-center text-slate-400">
        <Loader2 size={20} className="animate-spin mr-2" /> Loading chart…
      </div>
    ),
  }
);
import { OrderflowPanel } from './orderflow-panel';

/* ─── Popular symbols ─────────────────────────────────────────────────────── */
const QUICK_SYMBOLS = [
  { label: 'NIFTY 50',   value: 'NSE:NIFTY' },
  { label: 'BANKNIFTY',  value: 'NSE:BANKNIFTY' },
  { label: 'SENSEX',     value: 'BSE:SENSEX' },
  { label: 'RELIANCE',   value: 'NSE:RELIANCE' },
  { label: 'TCS',        value: 'NSE:TCS' },
  { label: 'HDFCBANK',   value: 'NSE:HDFCBANK' },
  { label: 'INFY',       value: 'NSE:INFY' },
  { label: 'ICICIBANK',  value: 'NSE:ICICIBANK' },
  { label: 'SBIN',       value: 'NSE:SBIN' },
  { label: 'BAJFINANCE', value: 'NSE:BAJFINANCE' },
  { label: 'WIPRO',      value: 'NSE:WIPRO' },
  { label: 'ITC',        value: 'NSE:ITC' },
  { label: 'LT',         value: 'NSE:LT' },
  { label: 'AXISBANK',   value: 'NSE:AXISBANK' },
  { label: 'KOTAKBANK',  value: 'NSE:KOTAKBANK' },
  { label: 'HINDUNILVR', value: 'NSE:HINDUNILVR' },
  { label: 'BHARTIARTL', value: 'NSE:BHARTIARTL' },
  { label: 'MARUTI',     value: 'NSE:MARUTI' },
  { label: 'TATAMOTORS', value: 'NSE:TATAMOTORS' },
  { label: 'TATASTEEL',  value: 'NSE:TATASTEEL' },
  { label: 'SUNPHARMA',  value: 'NSE:SUNPHARMA' },
  { label: 'ADANIENT',   value: 'NSE:ADANIENT' },
  { label: 'POWERGRID',  value: 'NSE:POWERGRID' },
  { label: 'NTPC',       value: 'NSE:NTPC' },
  { label: 'AAPL',       value: 'NASDAQ:AAPL' },
  { label: 'TSLA',       value: 'NASDAQ:TSLA' },
  { label: 'GOOGL',      value: 'NASDAQ:GOOGL' },
  { label: 'MSFT',       value: 'NASDAQ:MSFT' },
];

const COL_SPAN_CLASS: Record<number, string> = {
  3: 'lg:col-span-3',  4: 'lg:col-span-4',  5: 'lg:col-span-5',
  6: 'lg:col-span-6',  7: 'lg:col-span-7',  8: 'lg:col-span-8',
  9: 'lg:col-span-9', 10: 'lg:col-span-10', 11: 'lg:col-span-11',
  12: 'lg:col-span-12',
};

const INITIAL_LAYOUT: WorkspacePanel[] = [
  { id: 'main',       title: 'Price Panel',            kind: 'main',       w: 12, h: 4, minW: 6,  maxW: 12, minH: 3, maxH: 6 },
  { id: 'comparison', title: 'Multi-Series Comparison', kind: 'comparison', w: 6,  h: 2, minW: 4,  maxW: 8,  minH: 2, maxH: 4 },
  { id: 'momentum',   title: 'Momentum Overlay',        kind: 'momentum',   w: 6,  h: 2, minW: 4,  maxW: 8,  minH: 2, maxH: 4 },
  { id: 'orderflow',  title: 'Orderflow Matrix',        kind: 'orderflow',  w: 12, h: 2, minW: 6,  maxW: 12, minH: 2, maxH: 4 },
];

type ResizeState = { panelId: string; startX: number; startY: number; startW: number; startH: number };

export function TradingWorkspace({ symbol: defaultSymbol }: { symbol: string }) {
  /* ── Symbol state ─────────────────────────────────────────────────────── */
  const initialTv = QUICK_SYMBOLS.find(
    (q) => q.label.toUpperCase() === defaultSymbol.toUpperCase(),
  )?.value ?? `NSE:${defaultSymbol.toUpperCase()}`;

  const [tvSymbol, setTvSymbol]       = useState(initialTv);   // fed to TradingViewChart
  const [searchInput, setSearchInput] = useState(defaultSymbol.toUpperCase());
  const [showChips, setShowChips]     = useState(false);

  /* ── Internal feed (comparison / momentum / orderflow panels) ─────────── */
  const feedSymbol = tvSymbol.split(':').pop() ?? defaultSymbol;
  const { candles, ema20, ema50, vwap, momentum, benchmark, orderBook, timeSales, source, lastPrice, changePct, loading } =
    useTradingFeed(feedSymbol);

  /* ── Layout state ─────────────────────────────────────────────────────── */
  const [layout, setLayout]           = useState<WorkspacePanel[]>(INITIAL_LAYOUT);
  const [draggingPanelId, setDragging] = useState<string | null>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const resizeRef    = useRef<ResizeState | null>(null);
  const overlays     = useMemo<OverlayVisibility>(() => ({ ema20: true, ema50: true, vwap: true }), []);

  /* ── Symbol change ────────────────────────────────────────────────────── */
  const applySymbol = useCallback((raw: string) => {
    const upper = raw.trim().toUpperCase();
    if (!upper) return;
    // If user typed something like "NSE:TCS" keep it; otherwise prepend NSE:
    const resolved = upper.includes(':') ? upper : `NSE:${upper}`;
    setTvSymbol(resolved);
    setSearchInput(upper.includes(':') ? upper.split(':')[1] : upper);
    setShowChips(false);
  }, []);

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') applySymbol(searchInput);
    if (e.key === 'Escape') setShowChips(false);
  };

  /* ── Drag / resize ────────────────────────────────────────────────────── */
  const onDrop = (targetId: string) => {
    if (!draggingPanelId || draggingPanelId === targetId) return;
    setLayout((prev) => {
      const si = prev.findIndex((p) => p.id === draggingPanelId);
      const ti = prev.findIndex((p) => p.id === targetId);
      if (si < 0 || ti < 0) return prev;
      const next = [...prev];
      const [moved] = next.splice(si, 1);
      next.splice(ti, 0, moved);
      return next;
    });
    setDragging(null);
  };

  const beginResize = (event: React.PointerEvent<HTMLButtonElement>, panel: WorkspacePanel) => {
    event.preventDefault();
    event.stopPropagation();
    resizeRef.current = { panelId: panel.id, startX: event.clientX, startY: event.clientY, startW: panel.w, startH: panel.h };

    const moveListener = (e: PointerEvent) => {
      const r = resizeRef.current;
      if (!r || !containerRef.current) return;
      const colUnit = containerRef.current.clientWidth / 12;
      const rowUnit = 170;
      setLayout((prev) =>
        prev.map((item) =>
          item.id !== r.panelId ? item : {
            ...item,
            w: clamp(Math.round(r.startW + (e.clientX - r.startX) / colUnit), item.minW, item.maxW),
            h: clamp(Math.round(r.startH + (e.clientY - r.startY) / rowUnit), item.minH, item.maxH),
          }
        )
      );
    };
    const upListener = () => {
      resizeRef.current = null;
      window.removeEventListener('pointermove', moveListener);
      window.removeEventListener('pointerup', upListener);
    };
    window.addEventListener('pointermove', moveListener);
    window.addEventListener('pointerup', upListener);
  };

  /* ── Series data ──────────────────────────────────────────────────────── */
  const comparisonSeries = useMemo(() => [
    { id: 'close', color: '#3b82f6', lineWidth: 2, data: candles.map((c) => ({ time: c.time, value: c.close })) },
    { id: 'ema20', color: '#f59e0b', lineWidth: 2, data: ema20 },
    { id: 'vwap',  color: '#a78bfa', lineWidth: 2, data: vwap  },
  ], [candles, ema20, vwap]);

  const momentumSeries = useMemo(() => [
    { id: 'momentum',  color: '#22d3ee', lineWidth: 2, data: momentum  },
    { id: 'benchmark', color: '#f97316', lineWidth: 2, data: benchmark },
  ], [momentum, benchmark]);

  const changeTone = changePct >= 0 ? '#26a69a' : '#ef5350';
  const displaySymbol = tvSymbol.split(':').pop() ?? tvSymbol;

  return (
    <section
      className="rounded-lg overflow-hidden"
      style={{ background: 'var(--tv-bg-surface)', border: '1px solid var(--tv-border)' }}
    >
      {/* ── Header ── */}
      <div
        className="px-4 py-3 border-b"
        style={{ borderColor: 'var(--tv-border)', background: 'var(--tv-bg-base)' }}
      >
        {/* Row 1: symbol search + price chip + controls */}
        <div className="flex flex-wrap items-center gap-3 mb-3">
          {/* Symbol search input */}
          <div className="relative flex items-center flex-1 min-w-[200px] max-w-[340px]">
            <div
              className="flex items-center gap-2 rounded-md px-3 py-2 w-full"
              style={{ background: 'var(--tv-bg-elevated)', border: '1px solid var(--tv-border)' }}
            >
              <Search size={13} style={{ color: 'var(--tv-text-muted)', flexShrink: 0 }} />
              <input
                className="bg-transparent outline-none text-[13px] font-mono font-semibold w-full"
                style={{ color: 'var(--tv-text-primary)' }}
                placeholder="NSE:RELIANCE, TCS, INFY…"
                value={searchInput}
                onChange={(e) => { setSearchInput(e.target.value.toUpperCase()); setShowChips(true); }}
                onFocus={() => setShowChips(true)}
                onBlur={() => setTimeout(() => setShowChips(false), 150)}
                onKeyDown={handleKeyDown}
              />
              {searchInput && (
                <button
                  onClick={() => { setSearchInput(''); setShowChips(true); }}
                  style={{ color: 'var(--tv-text-muted)' }}
                >
                  <X size={12} />
                </button>
              )}
            </div>
            <button
              onClick={() => applySymbol(searchInput)}
              className="ml-2 tv-btn tv-btn-primary text-[11px] py-1.5 px-3 flex-shrink-0"
            >
              Load
            </button>

            {/* Dropdown suggestions */}
            {showChips && (
              <div
                className="absolute top-full left-0 mt-1 z-50 rounded-md overflow-hidden shadow-xl w-full"
                style={{ background: 'var(--tv-bg-elevated)', border: '1px solid var(--tv-border)' }}
              >
                {QUICK_SYMBOLS
                  .filter((q) =>
                    !searchInput ||
                    q.label.includes(searchInput.replace('NSE:', '').replace('BSE:', ''))
                  )
                  .slice(0, 8)
                  .map((q) => (
                    <button
                      key={q.value}
                      onMouseDown={() => applySymbol(q.value)}
                      className="w-full text-left px-3 py-2 text-[12px] flex items-center justify-between hover:bg-[var(--tv-bg-surface)] transition-colors"
                      style={{ color: 'var(--tv-text-primary)' }}
                    >
                      <span className="font-semibold">{q.label}</span>
                      <span className="text-[10px]" style={{ color: 'var(--tv-text-muted)' }}>
                        {q.value.split(':')[0]}
                      </span>
                    </button>
                  ))
                }
              </div>
            )}
          </div>

          {/* Live price chip */}
          <div
            className="flex items-center gap-2 rounded-md px-3 py-2 text-[13px]"
            style={{ background: 'var(--tv-bg-elevated)', border: '1px solid var(--tv-border)' }}
            suppressHydrationWarning
          >
            <span className="font-mono font-bold" style={{ color: 'var(--tv-text-primary)' }}>
              {displaySymbol}
            </span>
            <span className="font-mono font-semibold" style={{ color: 'var(--tv-text-primary)' }} suppressHydrationWarning>
              {lastPrice.toFixed(2)}
            </span>
            <span className="font-mono font-semibold text-[12px]" style={{ color: changeTone }} suppressHydrationWarning>
              {`${changePct >= 0 ? '+' : ''}${changePct.toFixed(2)}%`}
            </span>
          </div>

          {/* Feed status */}
          <div
            className="flex items-center gap-1.5 rounded-md px-3 py-2 text-[11px]"
            style={{ background: 'var(--tv-bg-elevated)', border: '1px solid var(--tv-border)' }}
            suppressHydrationWarning
          >
            <span
              className="h-1.5 w-1.5 rounded-full"
              style={{ background: source === 'live' ? '#26a69a' : '#f7a600' }}
            />
            <span style={{ color: 'var(--tv-text-muted)' }}>Feed:</span>
            <span className="font-semibold uppercase" style={{ color: source === 'live' ? '#26a69a' : '#f7a600' }}>
              {source === 'live' ? 'Yahoo Finance Live' : 'Simulated'}
            </span>
          </div>

          <button
            type="button"
            className="tv-btn tv-btn-ghost text-[11px] py-1.5 px-3 flex items-center gap-1.5 ml-auto"
            onClick={() => setLayout(INITIAL_LAYOUT)}
          >
            <RotateCcw size={12} /> Reset Layout
          </button>
        </div>

        {/* Row 2: quick-select chips */}
        <div className="flex flex-wrap items-center gap-1.5">
          <span className="text-[10px] mr-1" style={{ color: 'var(--tv-text-muted)' }}>Quick:</span>
          {QUICK_SYMBOLS.slice(0, 18).map((q) => {
            const isActive = tvSymbol === q.value;
            return (
              <button
                key={q.value}
                onClick={() => applySymbol(q.value)}
                className="rounded px-2 py-0.5 text-[10px] font-semibold transition-all"
                style={isActive
                  ? { background: 'rgba(41,98,255,0.18)', border: '1px solid rgba(41,98,255,0.5)', color: '#2962ff' }
                  : { background: 'var(--tv-bg-elevated)', border: '1px solid var(--tv-border)', color: 'var(--tv-text-muted)' }
                }
              >
                {q.label}
              </button>
            );
          })}
        </div>
      </div>

      {/* ── Panels ── */}
      <div ref={containerRef} className="grid grid-cols-1 gap-4 p-4 lg:grid-cols-12">
        {layout.map((panel) => (
          <article
            key={panel.id}
            className={`group relative col-span-1 overflow-hidden rounded-md ${
              draggingPanelId === panel.id ? 'opacity-50' : ''
            } ${COL_SPAN_CLASS[panel.w] ?? 'lg:col-span-6'}`}
            style={{
              minHeight: `${panel.h * 170}px`,
              background: 'var(--tv-bg-base)',
              border: '1px solid var(--tv-border)',
            }}
            onDragOver={(e) => e.preventDefault()}
            onDrop={() => onDrop(panel.id)}
          >
            {/* Panel header */}
            <header
              draggable
              onDragStart={() => setDragging(panel.id)}
              onDragEnd={() => setDragging(null)}
              className="flex cursor-grab items-center justify-between px-3 py-2 border-b active:cursor-grabbing"
              style={{ borderColor: 'var(--tv-border)' }}
            >
              <div className="flex items-center gap-2 text-[12px]">
                <GripVertical size={13} style={{ color: 'var(--tv-text-muted)' }} />
                <span className="font-medium" style={{ color: 'var(--tv-text-primary)' }}>
                  {panel.kind === 'main' ? `${displaySymbol} — ${panel.title}` : panel.title}
                </span>
              </div>
              <span className="text-[10px]" style={{ color: 'var(--tv-text-muted)' }}>Drag · Resize ↘</span>
            </header>

            {/* Panel body */}
            <div className="h-[calc(100%-41px)]">
              {/* ── Price Panel: candlestick chart powered by Yahoo Finance data ── */}
              {panel.kind === 'main' && (
                loading ? (
                  <div className="flex h-full items-center justify-center gap-2" style={{ color: 'var(--tv-text-muted)' }}>
                    <Loader2 size={18} className="animate-spin" />
                    <span className="text-[13px]">Loading {displaySymbol} data…</span>
                  </div>
                ) : (
                  <AdvancedTradingChart
                    candles={candles}
                    ema20={ema20}
                    ema50={ema50}
                    vwap={vwap}
                    overlays={overlays}
                    height={panel.h * 170 - 41}
                  />
                )
              )}

              {panel.kind === 'comparison' && (
                <MultiSeriesLineChart series={comparisonSeries} height={panel.h * 170 - 41} />
              )}

              {panel.kind === 'momentum' && (
                <MultiSeriesLineChart series={momentumSeries} height={panel.h * 170 - 41} />
              )}

              {panel.kind === 'orderflow' && (
                <OrderflowPanel orderBook={orderBook} timeSales={timeSales} />
              )}
            </div>

            {/* Resize handle */}
            <button
              type="button"
              onPointerDown={(e) => beginResize(e, panel)}
              className="absolute bottom-1 right-1 h-5 w-5 cursor-se-resize rounded text-[11px] opacity-0 transition group-hover:opacity-60"
              style={{ color: 'var(--tv-text-muted)' }}
              aria-label={`Resize ${panel.title}`}
            >
              ↘
            </button>
          </article>
        ))}
      </div>
    </section>
  );
}
