'use client';

import { useEffect } from 'react';
import { loadTradingViewScript, TRADINGVIEW_SCRIPT_SRC } from '@/lib/tradingview-script';

/**
 * Renders nothing. When mounted (e.g. in dashboard layout), it:
 * 1. Adds DNS prefetch for TradingView domains for faster connection.
 * 2. Adds a preload link so the browser prioritizes fetching the TradingView script.
 * 3. Starts loading the script so it's ready when the user opens a page with the chart.
 *
 * This reduces perceived chart load time because the script is often already
 * downloaded and parsed by the time TradingViewChart mounts.
 */
export function TradingViewPreload() {
  useEffect(() => {
    // DNS prefetch for TradingView domains
    const dnsPrefetchId = 'tradingview-dns-prefetch';
    if (!document.getElementById(dnsPrefetchId)) {
      const dnsPrefetch = document.createElement('link');
      dnsPrefetch.id = dnsPrefetchId;
      dnsPrefetch.rel = 'dns-prefetch';
      dnsPrefetch.href = 'https://s3.tradingview.com';
      document.head.appendChild(dnsPrefetch);
    }

    // Preconnect for even faster connection (includes DNS + TCP + TLS)
    const preconnectId = 'tradingview-preconnect';
    if (!document.getElementById(preconnectId)) {
      const preconnect = document.createElement('link');
      preconnect.id = preconnectId;
      preconnect.rel = 'preconnect';
      preconnect.href = 'https://s3.tradingview.com';
      preconnect.crossOrigin = 'anonymous';
      document.head.appendChild(preconnect);
    }

    // Preload the script
    const linkId = 'tradingview-preload';
    if (!document.getElementById(linkId)) {
      const link = document.createElement('link');
      link.id = linkId;
      link.rel = 'preload';
      link.href = TRADINGVIEW_SCRIPT_SRC;
      link.as = 'script';
      document.head.appendChild(link);
    }

    // Start loading the script in the background (same as chart does).
    loadTradingViewScript().catch(() => {});

    return () => {
      document.getElementById(dnsPrefetchId)?.remove();
      document.getElementById(preconnectId)?.remove();
      document.getElementById(linkId)?.remove();
    };
  }, []);

  return null;
}
