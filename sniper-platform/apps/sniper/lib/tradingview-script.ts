/**
 * Shared TradingView widget script loader.
 * Supports both the legacy tv.js and the modern embed-widget-advanced-chart.js.
 */

export const TRADINGVIEW_SCRIPT_ID = 'tradingview-tv-js';
export const TRADINGVIEW_SCRIPT_SRC = 'https://s3.tradingview.com/external-embedding/embed-widget-advanced-chart.js';

export function loadTradingViewScript(): Promise<void> {
  if (typeof window === 'undefined') return Promise.resolve();

  return new Promise((resolve, reject) => {
    const existing = document.querySelector(
      `script[src="${TRADINGVIEW_SCRIPT_SRC}"]`,
    ) as HTMLScriptElement | null;
    if (existing) {
      resolve();
      return;
    }

    const link = document.createElement('link');
    link.rel = 'preconnect';
    link.href = 'https://s3.tradingview.com';
    document.head.appendChild(link);

    const dns = document.createElement('link');
    dns.rel = 'dns-prefetch';
    dns.href = 'https://s3.tradingview.com';
    document.head.appendChild(dns);

    resolve();
  });
}
