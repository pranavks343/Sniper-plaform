'use client';

import { useEffect, useRef } from 'react';

import type { LinePoint } from '@/types/chart';
import { createChart, LineSeries as LightweightLineSeries } from 'lightweight-charts';

type LineSeries = {
  id: string;
  color: string;
  lineWidth?: number;
  data: LinePoint[];
};

type MultiSeriesLineChartProps = {
  series: LineSeries[];
  height: number;
};

export function MultiSeriesLineChart({ series, height }: MultiSeriesLineChartProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const chartRef = useRef<any>(null);
  const seriesMapRef = useRef<Map<string, any>>(new Map());

  useEffect(() => {
    if (!containerRef.current) {
      return;
    }

    const chart = createChart(containerRef.current, {
      width: containerRef.current.clientWidth,
      height,
      layout: {
        background: { color: 'transparent' },
        textColor: '#94a3b8'
      },
      rightPriceScale: {
        borderColor: 'rgba(51, 65, 85, 0.8)'
      },
      timeScale: {
        borderColor: 'rgba(51, 65, 85, 0.8)',
        timeVisible: true,
        secondsVisible: false
      },
      grid: {
        vertLines: { color: 'rgba(30, 41, 59, 0.5)' },
        horzLines: { color: 'rgba(30, 41, 59, 0.5)' }
      }
    });

    chartRef.current = chart;

    const resizeObserver = new ResizeObserver(() => {
      if (!containerRef.current || !chartRef.current) {
        return;
      }
      chartRef.current.applyOptions({ width: containerRef.current.clientWidth, height });
    });
    resizeObserver.observe(containerRef.current);

    return () => {
      resizeObserver.disconnect();
      chart.remove();
      seriesMapRef.current.clear();
    };
  }, [height]);

  useEffect(() => {
    if (!chartRef.current) {
      return;
    }

    const existing = seriesMapRef.current;
    const incoming = new Set(series.map((item) => item.id));

    for (const [key, line] of existing.entries()) {
      if (!incoming.has(key)) {
        chartRef.current.removeSeries(line);
        existing.delete(key);
      }
    }

    for (const item of series) {
      if (!existing.has(item.id)) {
        existing.set(
          item.id,
          chartRef.current.addSeries(LightweightLineSeries, {
            color: item.color,
            lineWidth: item.lineWidth ?? 2
          })
        );
      }
      existing.get(item.id).setData(item.data);
    }

    chartRef.current.timeScale().fitContent();
  }, [series]);

  return <div ref={containerRef} className="h-full w-full" />;
}
