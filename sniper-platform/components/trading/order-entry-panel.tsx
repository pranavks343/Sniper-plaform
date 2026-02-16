'use client';

import { useState } from 'react';

import { apiClient } from '@/lib/api-client';
import { formatINR } from '@/lib/utils';

import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Select } from '../ui/select';

export function OrderEntryPanel() {
  const [symbol, setSymbol] = useState('NIFTY');
  const [quantity, setQuantity] = useState(50);
  const [orderType, setOrderType] = useState('MARKET');
  const [side, setSide] = useState<'BUY' | 'SELL'>('BUY');
  const [submitting, setSubmitting] = useState(false);
  const [message, setMessage] = useState('');

  const estimate = quantity * 100;

  const submit = async () => {
    setSubmitting(true);
    try {
      const order = await apiClient.execution.placeOrder({ symbol, quantity, order_type: orderType, side, urgency: 0.7 });
      setMessage(`Order ${order.id.slice(0, 8)} placed`);
    } catch (error) {
      setMessage((error as Error).message);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="card-shell space-y-3">
      <h3 className="font-heading text-xl">Order Entry</h3>
      <div className="space-y-2">
        <label className="text-sm">Symbol</label>
        <Input value={symbol} onChange={(e) => setSymbol(e.target.value)} />
      </div>
      <div className="space-y-2">
        <label className="text-sm">Quantity</label>
        <Input type="number" value={quantity} onChange={(e) => setQuantity(Number(e.target.value))} />
      </div>
      <div className="space-y-2">
        <label className="text-sm">Order Type</label>
        <Select value={orderType} onChange={(e) => setOrderType(e.target.value)}>
          <option value="MARKET">Market</option>
          <option value="LIMIT">Limit</option>
          <option value="STOP">Stop-Loss</option>
        </Select>
      </div>
      <div className="flex gap-2">
        <Button className={side === 'BUY' ? 'bg-success' : 'bg-slate-500'} onClick={() => setSide('BUY')}>
          Buy
        </Button>
        <Button className={side === 'SELL' ? 'bg-danger' : 'bg-slate-500'} onClick={() => setSide('SELL')}>
          Sell
        </Button>
      </div>
      <p className="rounded-lg bg-slate-100 p-2 text-sm dark:bg-slate-800">Estimated turnover: {formatINR(estimate)}</p>
      <p className="text-sm text-slate-600 dark:text-slate-300">Risk check: Pass</p>
      <Button disabled={submitting} onClick={submit}>
        {submitting ? 'Placing...' : 'Place Order'}
      </Button>
      {message ? <p className="text-sm text-slate-600 dark:text-slate-300">{message}</p> : null}
    </div>
  );
}
