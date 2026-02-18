/**
 * Shared TradingView widget script loader.
 * Used by TradingViewChart and by the dashboard preloader so the script
 * can start loading as soon as the user enters the dashboard.
 */

export const TRADINGVIEW_SCRIPT_ID = 'tradingview-tv-js';
export const TRADINGVIEW_SCRIPT_SRC = 'https://s3.tradingview.com/tv.js';

export function loadTradingViewScript(): Promise<void> {
  if (typeof window === 'undefined') return Promise.resolve();
  const w = window as Window & { TradingView?: { widget: unknown } };
  if (w.TradingView?.widget) return Promise.resolve();

  return new Promise((resolve, reject) => {
    const existing = document.getElementById(TRADINGVIEW_SCRIPT_ID) as HTMLScriptElement | null;
    if (existing) {
      if (existing.dataset.loaded === 'true') {
        resolve();
        return;
      }
      existing.addEventListener('load', () => resolve(), { once: true });
      existing.addEventListener('error', () => reject(new Error('TradingView script failed')), { once: true });
      return;
    }
    const s = document.createElement('script');
    s.id = TRADINGVIEW_SCRIPT_ID;
    s.src = TRADINGVIEW_SCRIPT_SRC;
    s.async = true;
    s.onload = () => {
      s.dataset.loaded = 'true';
      resolve();
    };
    s.onerror = () => reject(new Error('TradingView script failed'));
    document.head.appendChild(s);
  });
}
