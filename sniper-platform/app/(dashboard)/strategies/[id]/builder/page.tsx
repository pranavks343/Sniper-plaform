'use client';

import { Card } from '@/components/ui/card';

export default function StrategyBuilderPage({ params }: { params: { id: string } }) {
  return (
    <div className="grid gap-4 lg:grid-cols-5">
      <Card className="lg:col-span-1">
        <h2 className="font-heading text-xl">Components</h2>
        <ul className="mt-3 space-y-2 text-sm">
          <li>EMA</li>
          <li>SMA</li>
          <li>RSI</li>
          <li>MACD</li>
          <li>ADX</li>
          <li>Bollinger</li>
          <li>ATR</li>
          <li>Regime Filter</li>
          <li>Buy/Sell Action</li>
        </ul>
      </Card>
      <Card className="lg:col-span-3">
        <h2 className="font-heading text-xl">Canvas</h2>
        <div className="mt-3 min-h-80 rounded-xl border border-dashed border-slate-400 p-4 text-sm text-slate-600 dark:border-slate-700 dark:text-slate-300">
          [EMA 20] → [Price &gt; EMA] → [AND] ← [Volume &gt; Avg] → [Buy]
        </div>
      </Card>
      <Card className="lg:col-span-1">
        <h2 className="font-heading text-xl">Node Properties</h2>
        <p className="mt-3 text-sm">Selected node: EMA 20</p>
        <pre className="mt-3 rounded-lg bg-slate-100 p-3 text-xs dark:bg-slate-800">if ema20_cross and volume_confirmed: BUY</pre>
      </Card>
    </div>
  );
}
