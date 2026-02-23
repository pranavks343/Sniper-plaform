'use client';

import { useMemo, useState, memo } from 'react';
import { AlertCircle, Loader2 } from 'lucide-react';

const SYMBOL_OVERRIDES: Record<string, string> = {
  'NSE:NIFTY50': 'NSE:NIFTY1!',
  'NSE:NIFTY': 'NSE:NIFTY1!',
  'NSE:BANKNIFTY': 'NSE:BANKNIFTY1!',
  'NSE:FINNIFTY': 'NSE:FINNIFTY1!',
};

function resolveSymbol(raw: string): string {
  const upper = raw.trim().toUpperCase();
  if (upper.includes(':')) return SYMBOL_OVERRIDES[upper] ?? upper;
  const withExchange = `NSE:${upper}`;
  return SYMBOL_OVERRIDES[withExchange] ?? withExchange;
}

function buildWidgetUrl(symbol: string, interval: string): string {
  const params = new URLSearchParams({
    symbol,
    interval,
    timezone: 'Asia/Kolkata',
    theme: 'dark',
    style: '1',
    locale: 'en',
    toolbar_bg: '#131722',
    enable_publishing: 'false',
    allow_symbol_change: 'true',
    withdateranges: 'true',
    hide_side_toolbar: 'false',
    details: 'true',
    hotlist: 'true',
    calendar: 'false',
    save_image: 'false',
  });
  return `https://www.tradingview.com/widgetembed/?${params.toString()}#{"utm_source":"widget","utm_medium":"widget","utm_campaign":"chart"}`;
}

type Props = {
  symbol?: string;
  interval?: string;
  height?: number;
  className?: string;
};

function TradingViewChartInner({
  symbol = 'NSE:NIFTY50',
  interval = 'D',
  height = 500,
  className,
}: Props) {
  const [status, setStatus] = useState<'loading' | 'ready' | 'error'>('loading');
  const embedSymbol = useMemo(() => resolveSymbol(symbol), [symbol]);
  const iframeSrc = useMemo(() => buildWidgetUrl(embedSymbol, interval), [embedSymbol, interval]);

  return (
    <div
      className={className ?? 'w-full'}
      style={{ height, position: 'relative', borderRadius: 6, overflow: 'hidden' }}
    >
      <iframe
        key={iframeSrc}
        src={iframeSrc}
        style={{
          width: '100%',
          height: '100%',
          border: 'none',
          display: status === 'error' ? 'none' : 'block',
        }}
        allow="autoplay; fullscreen"
        sandbox="allow-same-origin allow-scripts allow-popups allow-forms"
        loading="eager"
        onLoad={() => setStatus('ready')}
        onError={() => setStatus('error')}
      />

      {status === 'loading' && (
        <div
          style={{
            position: 'absolute',
            inset: 0,
            background: '#131722',
            display: 'flex',
            flexDirection: 'column',
            borderRadius: 6,
            overflow: 'hidden',
            zIndex: 10,
          }}
        >
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
          <div style={{ position: 'absolute', inset: 0, display: 'flex', alignItems: 'center', justifyContent: 'center', background: 'rgba(19,23,34,0.65)' }}>
            <div className="flex flex-col items-center gap-3">
              <Loader2 size={24} className="animate-spin" style={{ color: '#2962ff' }} />
              <p className="text-[12px]" style={{ color: '#787b86' }}>
                Loading TradingView chart…
              </p>
            </div>
          </div>
        </div>
      )}

      {status === 'error' && (
        <div
          style={{
            position: 'absolute',
            inset: 0,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            background: 'rgba(239,83,80,0.06)',
            border: '1px solid rgba(239,83,80,0.25)',
            borderRadius: 6,
            zIndex: 10,
          }}
        >
          <div className="flex flex-col items-center gap-2 text-center px-6">
            <AlertCircle size={22} style={{ color: '#ef5350' }} />
            <p className="text-[13px] font-semibold" style={{ color: '#ef5350' }}>Chart unavailable</p>
            <p className="text-[11px]" style={{ color: '#787b86' }}>Could not load TradingView chart. Please check your internet connection and try refreshing.</p>
          </div>
        </div>
      )}
    </div>
  );
}

export const TradingViewChart = memo(TradingViewChartInner);
