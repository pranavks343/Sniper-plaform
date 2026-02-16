'use client';

import { useEffect, useRef } from 'react';

import { createChart } from 'lightweight-charts';

export function TradingViewChart() {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!containerRef.current) {
      return;
    }

    const chart = createChart(containerRef.current, {
      layout: { background: { color: 'transparent' }, textColor: '#64748b' },
      width: containerRef.current.clientWidth,
      height: 340,
      grid: {
        vertLines: { color: 'rgba(148, 163, 184, 0.2)' },
        horzLines: { color: 'rgba(148, 163, 184, 0.2)' }
      }
    });

    const candle = (chart as any).addCandlestickSeries();
    candle.setData(
      Array.from({ length: 60 }, (_, i) => ({
        time: (Math.floor(Date.now() / 1000) - (60 - i) * 60) as never,
        open: 22500 + Math.sin(i) * 30,
        high: 22520 + Math.sin(i) * 35,
        low: 22470 + Math.sin(i) * 25,
        close: 22510 + Math.sin(i + 1) * 28
      }))
    );

    const resize = () => {
      if (!containerRef.current) {
        return;
      }
      chart.applyOptions({ width: containerRef.current.clientWidth });
    };

    window.addEventListener('resize', resize);
    return () => {
      window.removeEventListener('resize', resize);
      chart.remove();
    };
  }, []);

  return <div ref={containerRef} className="w-full" />;
}
