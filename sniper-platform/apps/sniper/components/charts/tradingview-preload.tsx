'use client';

import { useEffect } from 'react';

/**
 * Renders nothing. When mounted (e.g. in dashboard layout), it adds
 * DNS prefetch + preconnect hints for tradingview.com so the iframe
 * loads faster when the user opens the live-trading page.
 */
export function TradingViewPreload() {
  useEffect(() => {
    const dnsPrefetchId = 'tradingview-dns-prefetch';
    if (!document.getElementById(dnsPrefetchId)) {
      const dnsPrefetch = document.createElement('link');
      dnsPrefetch.id = dnsPrefetchId;
      dnsPrefetch.rel = 'dns-prefetch';
      dnsPrefetch.href = 'https://www.tradingview.com';
      document.head.appendChild(dnsPrefetch);
    }

    const preconnectId = 'tradingview-preconnect';
    if (!document.getElementById(preconnectId)) {
      const preconnect = document.createElement('link');
      preconnect.id = preconnectId;
      preconnect.rel = 'preconnect';
      preconnect.href = 'https://www.tradingview.com';
      preconnect.crossOrigin = 'anonymous';
      document.head.appendChild(preconnect);
    }

    return () => {
      document.getElementById(dnsPrefetchId)?.remove();
      document.getElementById(preconnectId)?.remove();
    };
  }, []);

  return null;
}
