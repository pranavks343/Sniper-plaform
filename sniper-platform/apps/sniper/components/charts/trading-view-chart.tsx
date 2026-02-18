'use client';

import { useEffect, useMemo, useRef, useState } from 'react';
import { AlertCircle, Loader2 } from 'lucide-react';
import { loadTradingViewScript } from '@/lib/tradingview-script';

/* ─── TradingView widget types ────────────────────────────────────────────── */
type TvWidgetConfig = {
  autosize:            boolean;
  container_id:        string;
  symbol:              string;
  interval:            string;
  timezone:            string;
  theme:               'dark' | 'light';
  style:               string;
  locale:              string;
  toolbar_bg:          string;
  enable_publishing:   boolean;
  hide_top_toolbar:    boolean;
  hide_legend:         boolean;
  save_image:          boolean;
  allow_symbol_change: boolean;
  withdateranges:      boolean;
  studies?:            string[];
  show_popup_button:   boolean;
};

declare global {
  interface Window {
    TradingView?: { widget: new (cfg: TvWidgetConfig) => unknown };
  }
}

/* ─── Helpers ─────────────────────────────────────────────────────────────── */

/** NSE index futures need a different ticker in the embed */
const SYMBOL_OVERRIDES: Record<string, string> = {
  'NSE:NIFTY50':   'NSE:NIFTY1!',
  'NSE:NIFTY':     'NSE:NIFTY1!',
  'NSE:BANKNIFTY': 'NSE:BANKNIFTY1!',
  'NSE:FINNIFTY':  'NSE:FINNIFTY1!',
};

function resolveSymbol(raw: string): string {
  const upper = raw.trim().toUpperCase();
  // Already has exchange prefix
  if (upper.includes(':')) {
    return SYMBOL_OVERRIDES[upper] ?? upper;
  }
  // Bare symbol — prefix with NSE
  const withExchange = `NSE:${upper}`;
  return SYMBOL_OVERRIDES[withExchange] ?? withExchange;
}

/* ─── Component ───────────────────────────────────────────────────────────── */
type Props = {
  symbol?:    string;
  interval?:  string;
  height?:    number;
  className?: string;
};

export function TradingViewChart({
  symbol   = 'NSE:NIFTY50',
  interval = 'D',
  height   = 400,
  className,
}: Props) {
  // Unique container id that stays stable across re-renders of same instance
  const containerId  = useMemo(() => `tv-${Math.random().toString(36).slice(2, 9)}`, []);
  const mountedRef   = useRef(true);
  const [status, setStatus] = useState<'loading' | 'ready' | 'error'>('loading');
  const [errMsg, setErrMsg] = useState('');

  const embedSymbol = useMemo(() => resolveSymbol(symbol), [symbol]);

  useEffect(() => {
    mountedRef.current = true;
    setStatus('loading');

    const container = document.getElementById(containerId);
    if (container) container.innerHTML = '';

    const mount = async () => {
      try {
        await loadTradingViewScript();
      } catch (e) {
        if (mountedRef.current) {
          setErrMsg('Could not load TradingView library. Check your internet connection.');
          setStatus('error');
        }
        return;
      }

      if (!mountedRef.current) return;

      const el = document.getElementById(containerId);
      if (!el || !window.TradingView?.widget) return;

      el.innerHTML = '';   // clear any previous widget

      // tv.js embed widget does NOT support onready — it silently ignores it.
      // Set ready immediately after construction; the widget manages its own iframe load.
      new window.TradingView.widget({
        autosize:            true,
        container_id:        containerId,
        symbol:              embedSymbol,
        interval,
        timezone:            'Asia/Kolkata',
        theme:               'dark',
        style:               '1',          // candlestick
        locale:              'en',
        toolbar_bg:          '#131722',
        enable_publishing:   false,
        hide_top_toolbar:    false,
        hide_legend:         false,
        save_image:          false,
        allow_symbol_change: true,
        withdateranges:      true,
        show_popup_button:   false,
      });

      if (mountedRef.current) setStatus('ready');
    };

    mount();

    return () => {
      mountedRef.current = false;
      const el = document.getElementById(containerId);
      if (el) el.innerHTML = '';
    };
  }, [containerId, embedSymbol, interval]);

  /*
   * IMPORTANT: The chart container div (id={containerId}) must ALWAYS be in
   * the DOM. TradingView's widget.new() targets it by id — if it isn't present
   * when the script resolves, getElementById returns null and the widget is
   * never created, leaving status stuck on 'loading' forever.
   *
   * Overlays (loading skeleton, error) are rendered on top via position:absolute.
   */
  return (
    <div
      className={className ?? 'w-full'}
      style={{ height, position: 'relative', borderRadius: 6, overflow: 'hidden' }}
    >
      {/* ── Always-present widget mount point ── */}
      <div
        id={containerId}
        style={{ width: '100%', height: '100%' }}
      />

      {/* ── Loading overlay (hidden once widget is constructed) ── */}
      {status === 'loading' && (
        <div
          style={{
            position: 'absolute', inset: 0,
            background: 'var(--tv-bg-base)',
            display: 'flex', flexDirection: 'column',
            borderRadius: 6, overflow: 'hidden',
          }}
        >
          {/* Skeleton */}
          <div style={{ padding: '12px', height: '100%', display: 'flex', flexDirection: 'column', gap: '8px' }}>
            <div style={{ height: '32px', background: 'rgba(255,255,255,0.04)', borderRadius: 4 }} className="animate-pulse" />
            <div style={{ flex: 1, background: 'rgba(255,255,255,0.02)', borderRadius: 4, position: 'relative' }}>
              <div style={{ position: 'absolute', bottom: '20%', left: '10%', right: '10%', height: '60%', display: 'flex', alignItems: 'flex-end', gap: '4px', opacity: 0.12 }}>
                {[40, 65, 45, 70, 55, 80, 60, 75, 50, 85, 65, 90, 70, 60, 75].map((h, i) => (
                  <div key={i} style={{ flex: 1, height: `${h}%`, background: i % 3 === 0 ? '#ef5350' : '#26a69a', borderRadius: 1 }} />
                ))}
              </div>
            </div>
          </div>
          {/* Spinner */}
          <div style={{ position: 'absolute', inset: 0, display: 'flex', alignItems: 'center', justifyContent: 'center', background: 'rgba(19,23,34,0.65)' }}>
            <div className="flex flex-col items-center gap-3">
              <Loader2 size={24} className="animate-spin" style={{ color: '#2962ff' }} />
              <p className="text-[12px]" style={{ color: 'var(--tv-text-muted)' }}>
                Loading TradingView chart…
              </p>
            </div>
          </div>
        </div>
      )}

      {/* ── Error overlay ── */}
      {status === 'error' && (
        <div
          style={{
            position: 'absolute', inset: 0,
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            background: 'rgba(239,83,80,0.06)',
            border: '1px solid rgba(239,83,80,0.25)',
            borderRadius: 6,
          }}
        >
          <div className="flex flex-col items-center gap-2 text-center px-6">
            <AlertCircle size={22} style={{ color: '#ef5350' }} />
            <p className="text-[13px] font-semibold" style={{ color: '#ef5350' }}>Chart unavailable</p>
            <p className="text-[11px]" style={{ color: 'var(--tv-text-muted)' }}>{errMsg}</p>
          </div>
        </div>
      )}
    </div>
  );
}
