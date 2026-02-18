'use client';

import { useEffect, useRef } from 'react';

import type { CandlePoint, LinePoint, OverlayVisibility } from '@/types/chart';
import { createChart, CandlestickSeries, HistogramSeries, LineSeries } from 'lightweight-charts';

type AdvancedTradingChartProps = {
  candles: CandlePoint[];
  ema20: LinePoint[];
  ema50: LinePoint[];
  vwap: LinePoint[];
  overlays: OverlayVisibility;
  height: number;
};

export function AdvancedTradingChart({ candles, ema20, ema50, vwap, overlays, height }: AdvancedTradingChartProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const chartRef = useRef<any>(null);
  const candleSeriesRef = useRef<any>(null);
  const volumeSeriesRef = useRef<any>(null);
  const ema20Ref = useRef<any>(null);
  const ema50Ref = useRef<any>(null);
  const vwapRef = useRef<any>(null);

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
        vertLines: { color: 'rgba(30, 41, 59, 0.55)' },
        horzLines: { color: 'rgba(30, 41, 59, 0.55)' }
      },
      crosshair: {
        vertLine: { color: 'rgba(99, 102, 241, 0.5)' },
        horzLine: { color: 'rgba(99, 102, 241, 0.5)' }
      }
    });

    const candleSeries = chart.addSeries(CandlestickSeries, {
      upColor: '#22c55e',
      downColor: '#ef4444',
      borderVisible: false,
      wickUpColor: '#22c55e',
      wickDownColor: '#ef4444'
    });

    const volumeSeries = chart.addSeries(HistogramSeries, {
      priceScaleId: '',
      color: 'rgba(59, 130, 246, 0.35)',
      priceFormat: { type: 'volume' }
    });

    const ema20Series = chart.addSeries(LineSeries, { color: '#f59e0b', lineWidth: 2 });
    const ema50Series = chart.addSeries(LineSeries, { color: '#06b6d4', lineWidth: 2 });
    const vwapSeries = chart.addSeries(LineSeries, { color: '#a78bfa', lineWidth: 2, lineStyle: 1 });

    chartRef.current = chart;
    candleSeriesRef.current = candleSeries;
    volumeSeriesRef.current = volumeSeries;
    ema20Ref.current = ema20Series;
    ema50Ref.current = ema50Series;
    vwapRef.current = vwapSeries;

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
    };
  }, [height]);

  useEffect(() => {
    if (!candleSeriesRef.current || !volumeSeriesRef.current) {
      return;
    }
    candleSeriesRef.current.setData(candles);
    volumeSeriesRef.current.setData(
      candles.map((candle) => ({
        time: candle.time,
        value: candle.volume,
        color: candle.close >= candle.open ? 'rgba(34,197,94,0.35)' : 'rgba(239,68,68,0.35)'
      }))
    );
    chartRef.current?.timeScale().fitContent();
  }, [candles]);

  useEffect(() => {
    ema20Ref.current?.setData(ema20);
  }, [ema20]);

  useEffect(() => {
    ema50Ref.current?.setData(ema50);
  }, [ema50]);

  useEffect(() => {
    vwapRef.current?.setData(vwap);
  }, [vwap]);

  useEffect(() => {
    ema20Ref.current?.applyOptions({ visible: overlays.ema20 });
    ema50Ref.current?.applyOptions({ visible: overlays.ema50 });
    vwapRef.current?.applyOptions({ visible: overlays.vwap });
  }, [overlays]);

  return <div ref={containerRef} className="h-full w-full" />;
}
