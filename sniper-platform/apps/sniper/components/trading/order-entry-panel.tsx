'use client';

import { useEffect, useMemo, useState } from 'react';
import { AlertCircle, CheckCircle2, Info, Loader2 } from 'lucide-react';

import { apiClient } from '@/lib/api-client';
import { formatINR } from '@sniper/framework';
import type { RiskLimits, RiskMetrics } from '@/types/risk';

const ORDER_TYPES = ['MARKET', 'LIMIT', 'STOP-LIMIT', 'STOP'];
const PRODUCTS    = ['MIS', 'NRML', 'CNC'];

export function OrderEntryPanel() {
  const [symbol,      setSymbol]      = useState('NIFTY');
  const [quantity,    setQuantity]    = useState(50);
  const [orderType,   setOrderType]   = useState('MARKET');
  const [product,     setProduct]     = useState('MIS');
  const [limitPrice,  setLimitPrice]  = useState('');
  const [side,        setSide]        = useState<'BUY' | 'SELL'>('BUY');
  const [submitting,  setSubmitting]  = useState(false);
  const [message,     setMessage]     = useState('');
  const [messageType, setMessageType] = useState<'success' | 'error' | ''>('');
  const [riskMetrics, setRiskMetrics] = useState<RiskMetrics | null>(null);
  const [riskLimits,  setRiskLimits]  = useState<RiskLimits  | null>(null);
  const [riskError,   setRiskError]   = useState<string | null>(null);

  const estimate    = quantity * 100;
  const signedDelta = side === 'BUY' ? quantity : -quantity;

  const riskSnapshot = useMemo(() => {
    if (!riskMetrics || !riskLimits) return { ready: false, pass: false, reason: 'Loading risk data...' };
    const nextDelta = Math.abs((riskMetrics.delta ?? 0) + signedDelta);
    const nextGamma = Math.abs(riskMetrics.gamma ?? 0);
    if (!riskMetrics.trading_allowed)  return { ready: true, pass: false, reason: 'Trading disabled by risk engine.' };
    if (quantity <= 0 || !Number.isFinite(quantity)) return { ready: true, pass: false, reason: 'Quantity must be > 0.' };
    if (nextDelta > riskLimits.max_delta) return { ready: true, pass: false, reason: `Delta breach: ${nextDelta.toFixed(0)} > ${riskLimits.max_delta.toFixed(0)}` };
    if (nextGamma > riskLimits.max_gamma) return { ready: true, pass: false, reason: `Gamma breach: ${nextGamma.toFixed(3)} > ${riskLimits.max_gamma.toFixed(3)}` };
    return { ready: true, pass: true, reason: `Δ ${nextDelta.toFixed(0)} / ${riskLimits.max_delta.toFixed(0)} limit` };
  }, [quantity, riskLimits, riskMetrics, signedDelta]);

  useEffect(() => {
    let cancelled = false;
    const refresh = async () => {
      try {
        const [m, l] = await Promise.all([apiClient.risk.getMetrics(), apiClient.risk.getLimits()]);
        if (cancelled) return;
        setRiskMetrics(m);
        setRiskLimits(l);
        setRiskError(null);
      } catch (e) {
        if (!cancelled) setRiskError((e as Error).message);
      }
    };
    void refresh();
    const id = window.setInterval(() => void refresh(), 5000);
    return () => { cancelled = true; window.clearInterval(id); };
  }, []);

  const submit = async () => {
    if (!riskSnapshot.pass) {
      setMessage(`Order blocked: ${riskSnapshot.reason}`);
      setMessageType('error');
      return;
    }
    setSubmitting(true);
    try {
      const order = await apiClient.execution.placeOrder({ symbol, quantity, order_type: orderType, side, urgency: 0.7 });
      setMessage(`Order ${order.id.slice(0, 8)} placed successfully`);
      setMessageType('success');
    } catch (e) {
      setMessage((e as Error).message);
      setMessageType('error');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="tv-panel overflow-hidden">
      {/* Panel header */}
      <div
        className="flex items-center justify-between px-4 py-3 border-b"
        style={{ borderColor: 'var(--tv-border)' }}
      >
        <span className="panel-title">Order Entry</span>
        <span className="status-chip blue text-[10px]">NSE · Derivatives</span>
      </div>

      <div className="p-4 space-y-3">

        {/* Buy / Sell toggle */}
        <div className="flex gap-2">
          <button
            className={`order-side-btn ${side === 'BUY' ? 'buy-active' : 'buy-inactive'}`}
            onClick={() => setSide('BUY')}
          >
            ▲ BUY
          </button>
          <button
            className={`order-side-btn ${side === 'SELL' ? 'sell-active' : 'sell-inactive'}`}
            onClick={() => setSide('SELL')}
          >
            ▼ SELL
          </button>
        </div>

        {/* Symbol */}
        <div className="space-y-1">
          <label className="panel-caption">Symbol</label>
          <input
            className="tv-input"
            value={symbol}
            onChange={(e) => setSymbol(e.target.value.toUpperCase())}
            placeholder="e.g. NIFTY, BANKNIFTY"
          />
        </div>

        {/* Qty + Product row */}
        <div className="grid grid-cols-2 gap-2">
          <div className="space-y-1">
            <label className="panel-caption">Quantity (Lots)</label>
            <input
              className="tv-input"
              type="number"
              min={1}
              value={quantity}
              onChange={(e) => setQuantity(Number(e.target.value) || 0)}
            />
          </div>
          <div className="space-y-1">
            <label className="panel-caption">Product</label>
            <select
              className="tv-select"
              value={product}
              onChange={(e) => setProduct(e.target.value)}
            >
              {PRODUCTS.map((p) => <option key={p} value={p}>{p}</option>)}
            </select>
          </div>
        </div>

        {/* Order type pills */}
        <div className="space-y-1">
          <label className="panel-caption">Order Type</label>
          <div className="flex gap-1 flex-wrap">
            {ORDER_TYPES.map((t) => (
              <button
                key={t}
                onClick={() => setOrderType(t)}
                className="rounded px-2.5 py-1 text-[11px] font-semibold transition"
                style={{
                  background: orderType === t ? 'var(--tv-blue-light)' : 'var(--tv-bg-elevated)',
                  border: `1px solid ${orderType === t ? 'rgba(41,98,255,0.4)' : 'var(--tv-border-light)'}`,
                  color: orderType === t ? 'var(--tv-blue)' : 'var(--tv-text-secondary)',
                }}
              >
                {t}
              </button>
            ))}
          </div>
        </div>

        {/* Limit price (conditional) */}
        {(orderType === 'LIMIT' || orderType === 'STOP-LIMIT') && (
          <div className="space-y-1">
            <label className="panel-caption">Limit Price</label>
            <input
              className="tv-input"
              type="number"
              value={limitPrice}
              onChange={(e) => setLimitPrice(e.target.value)}
              placeholder="Enter limit price"
            />
          </div>
        )}

        {/* Estimated value */}
        <div
          className="rounded px-3 py-2 flex items-center justify-between"
          style={{ background: 'var(--tv-bg-elevated)', border: '1px solid var(--tv-border)' }}
        >
          <span className="panel-caption">Est. Turnover</span>
          <span className="text-[13px] font-mono font-semibold" style={{ color: 'var(--tv-text-primary)' }}>
            {formatINR(estimate)}
          </span>
        </div>

        {/* Risk check */}
        <div
          className="rounded px-3 py-2 flex items-start gap-2"
          style={{
            background: riskSnapshot.pass ? 'rgba(38,166,154,0.06)' : 'rgba(239,83,80,0.06)',
            border: `1px solid ${riskSnapshot.pass ? 'rgba(38,166,154,0.25)' : 'rgba(239,83,80,0.25)'}`,
          }}
        >
          {!riskSnapshot.ready ? (
            <Loader2 size={13} className="animate-spin mt-0.5 flex-shrink-0" style={{ color: 'var(--tv-text-muted)' }} />
          ) : riskSnapshot.pass ? (
            <CheckCircle2 size={13} className="mt-0.5 flex-shrink-0" style={{ color: '#26a69a' }} />
          ) : (
            <AlertCircle size={13} className="mt-0.5 flex-shrink-0" style={{ color: '#ef5350' }} />
          )}
          <div>
            <span className="text-[11px] font-medium" style={{ color: riskSnapshot.pass ? '#26a69a' : '#ef5350' }}>
              {riskSnapshot.ready ? (riskSnapshot.pass ? 'Risk Check Passed' : 'Risk Check Failed') : 'Checking...'}
            </span>
            <p className="text-[11px] mt-0.5" style={{ color: 'var(--tv-text-muted)' }}>
              {riskSnapshot.reason}
            </p>
          </div>
        </div>

        {riskError && (
          <div className="flex items-center gap-1.5 text-[11px]" style={{ color: '#f7a600' }}>
            <Info size={11} />
            Risk API unavailable: {riskError}
          </div>
        )}

        {/* Submit */}
        <button
          disabled={submitting || !riskSnapshot.pass}
          onClick={submit}
          className={`order-submit-btn ${side === 'BUY' ? 'is-buy' : 'is-sell'} w-full py-2.5 text-[13px] font-bold uppercase tracking-wide text-white disabled:opacity-50 disabled:cursor-not-allowed`}
          style={{
            background: side === 'BUY'
              ? (submitting || !riskSnapshot.pass ? 'rgba(38,166,154,0.35)' : undefined)
              : (submitting || !riskSnapshot.pass ? 'rgba(239,83,80,0.35)' : undefined),
            border: 'none',
          }}
        >
          {submitting ? (
            <span className="flex items-center justify-center gap-2">
              <Loader2 size={14} className="animate-spin" />
              Placing Order...
            </span>
          ) : (
            `${side} ${symbol}`
          )}
        </button>

        {/* Feedback message */}
        {message && (
          <div
            className="rounded px-3 py-2 text-[12px]"
            style={{
              background: messageType === 'success' ? 'rgba(38,166,154,0.08)' : 'rgba(239,83,80,0.08)',
              border: `1px solid ${messageType === 'success' ? 'rgba(38,166,154,0.3)' : 'rgba(239,83,80,0.3)'}`,
              color: messageType === 'success' ? '#26a69a' : '#ef5350',
            }}
          >
            {message}
          </div>
        )}
      </div>
    </div>
  );
}
