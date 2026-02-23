'use client';

import { useEffect, useState } from 'react';
import { EquityCurveChart } from '@/components/charts/equity-curve-chart';
import { Card } from '@/lib/ui';
import { Badge } from '@/lib/ui';
import { usePositions } from '@/hooks/use-positions';
import { useRiskMetrics } from '@/hooks/use-risk-metrics';
import { useMarketRegime } from '@/hooks/use-market-regime';
import { useMarketNewsContext } from '@/components/providers/market-news-provider';
import { apiClient } from '@/lib/api-client';
import {
  Activity,
  BarChart3,
  BrainCircuit,
  ChevronDown,
  ChevronUp,
  FlaskConical,
  RefreshCw,
  ShieldCheck,
  TrendingDown,
  TrendingUp,
  Zap,
} from 'lucide-react';

type BacktestMetrics = {
  net_pnl: number;
  total_return: number;
  sharpe: number;
  sortino: number;
  max_drawdown: number;
  win_rate: number;
  profit_factor: number;
  calmar: number;
  avg_win: number;
  avg_loss: number;
  total_trades: number;
  ann_return: number;
};

function MetricCard({
  label, value, sub, icon: Icon, color,
}: {
  label: string; value: string; sub?: string;
  icon: React.ElementType; color: string;
}) {
  return (
    <div className="metric-card">
      <div className="flex items-center justify-between mb-1">
        <span className="panel-caption">{label}</span>
        <Icon size={13} style={{ color }} />
      </div>
      <p className="text-[22px] font-bold font-mono" style={{ color }}>{value}</p>
      {sub && <p className="text-[11px] mt-0.5" style={{ color: 'var(--tv-text-muted)' }}>{sub}</p>}
    </div>
  );
}

const REGIME_CONFIG: Record<string, {
  color: string;
  bgColor: string;
  borderColor: string;
  icon: React.ElementType;
  tone: 'success' | 'danger' | 'warning' | 'blue';
}> = {
  TRENDING: {
    color: '#26a69a',
    bgColor: 'rgba(38,166,154,0.08)',
    borderColor: 'rgba(38,166,154,0.25)',
    icon: TrendingUp,
    tone: 'success',
  },
  VOLATILE: {
    color: '#ef5350',
    bgColor: 'rgba(239,83,80,0.08)',
    borderColor: 'rgba(239,83,80,0.25)',
    icon: Activity,
    tone: 'danger',
  },
  MEAN_REVERTING: {
    color: '#2962ff',
    bgColor: 'rgba(41,98,255,0.08)',
    borderColor: 'rgba(41,98,255,0.25)',
    icon: RefreshCw,
    tone: 'blue',
  },
};

export default function AnalyticsPage() {
  const { positions, loading: posLoading } = usePositions();
  const { metrics, greeks, greeksLoading, setPortfolioState } = useRiskMetrics();
  const { data: regimeData, loading: regimeLoading } = useMarketRegime();
  const { news, loading: newsLoading } = useMarketNewsContext();

  const [btMetrics, setBtMetrics] = useState<BacktestMetrics | null>(null);
  const [btEquity, setBtEquity] = useState<number[]>([]);
  const [btLoading, setBtLoading] = useState(true);

  useEffect(() => {
    (async () => {
      try {
        const runs = await apiClient.backtest.list();
        const completed = runs.filter((r) => r.status === 'completed');
        if (completed.length === 0) { setBtLoading(false); return; }
        const latest = completed[0];
        const jobId = String(latest.job_id ?? latest.id ?? '');
        if (!jobId) { setBtLoading(false); return; }
        const results = await apiClient.backtest.results(jobId);
        const m = (results.metrics ?? results) as Record<string, unknown>;
        setBtMetrics({
          net_pnl: Number(m.net_pnl ?? 0),
          total_return: Number(m.total_return ?? 0),
          sharpe: Number(m.sharpe ?? 0),
          sortino: Number(m.sortino ?? 0),
          max_drawdown: Number(m.max_drawdown ?? 0),
          win_rate: Number(m.win_rate ?? 0),
          profit_factor: Number(m.profit_factor ?? 0),
          calmar: Number(m.calmar ?? 0),
          avg_win: Number(m.avg_win ?? 0),
          avg_loss: Number(m.avg_loss ?? 0),
          total_trades: Number(m.total_trades ?? 0),
          ann_return: Number(m.ann_return ?? 0),
        });
        const eq = Array.isArray(results.equity_curve)
          ? (results.equity_curve as Record<string, unknown>[]).map((e) => Number(e.equity ?? e.value ?? 0))
          : [];
        if (eq.length > 1) setBtEquity(eq);
      } catch { /* no backtest data available */ }
      setBtLoading(false);
    })();
  }, []);

  const [testOpen, setTestOpen] = useState(false);
  const [testDelta, setTestDelta] = useState('120');
  const [testGamma, setTestGamma] = useState('0.25');
  const [testTheta, setTestTheta] = useState('-45');
  const [testVega, setTestVega] = useState('180');
  const [testSaving, setTestSaving] = useState(false);

  const handleApplyTest = async () => {
    setTestSaving(true);
    try {
      await setPortfolioState({
        delta: parseFloat(testDelta) || 0,
        gamma: parseFloat(testGamma) || 0,
        theta: parseFloat(testTheta) || 0,
        vega:  parseFloat(testVega) || 0,
      });
    } catch { /* handled by store */ }
    setTestSaving(false);
  };

  const handleResetTest = async () => {
    setTestSaving(true);
    setTestDelta('0');
    setTestGamma('0');
    setTestTheta('0');
    setTestVega('0');
    try {
      await setPortfolioState({ delta: 0, gamma: 0, theta: 0, vega: 0 });
    } catch { /* handled by store */ }
    setTestSaving(false);
  };

  const totalPnl   = positions.reduce((a, p) => a + p.pnl, 0);
  const hasData    = positions.length > 0;

  const realEquityPoints = hasData
    ? positions.map((_, i) => {
        const runningPnl = positions.slice(0, i + 1).reduce((a, p) => a + p.pnl, 0);
        return 1_000_000 + runningPnl;
      })
    : [];

  const sampleEquityPoints = (() => {
    const pts: number[] = [1_000_000];
    const rng = (s: number) => { s = Math.sin(s) * 10000; return s - Math.floor(s); };
    for (let i = 1; i <= 60; i++) {
      const drift = 400 + Math.sin(i / 8) * 300;
      const noise = (rng(i * 137.5) - 0.45) * 2000;
      pts.push(Math.round(pts[i - 1] + drift + noise));
    }
    return pts;
  })();

  const equityPoints = realEquityPoints.length > 1
    ? realEquityPoints
    : btEquity.length > 1
      ? btEquity
      : sampleEquityPoints;
  const equitySource: 'live' | 'backtest' | 'sample' = realEquityPoints.length > 1
    ? 'live'
    : btEquity.length > 1
      ? 'backtest'
      : 'sample';
  const isDemo = equitySource === 'sample';

  const nifty = regimeData?.nifty;
  const bankNifty = regimeData?.bankNifty;
  const cfg = nifty ? REGIME_CONFIG[nifty.regime] ?? REGIME_CONFIG.MEAN_REVERTING : null;
  const bnCfg = bankNifty ? REGIME_CONFIG[bankNifty.regime] ?? REGIME_CONFIG.MEAN_REVERTING : null;

  return (
    <div className="space-y-5 animate-fadein">

      <div>
        <p className="panel-caption mb-1">Performance Analysis</p>
        <h1 className="text-[17px] font-semibold tracking-tight" style={{ color: 'var(--tv-text-primary)' }}>
          Analytics
        </h1>
      </div>

      {hasData ? (
        <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
          <MetricCard
            label="Open P&L"
            value={`${totalPnl >= 0 ? '+' : ''}₹${Math.abs(totalPnl).toLocaleString()}`}
            sub={`${positions.length} open position${positions.length !== 1 ? 's' : ''}`}
            icon={TrendingUp}
            color={totalPnl >= 0 ? '#26a69a' : '#ef5350'}
          />
          <MetricCard
            label="Portfolio Delta"
            value={(metrics?.delta ?? 0).toFixed(1)}
            sub="Net delta exposure"
            icon={BarChart3}
            color={Math.abs(metrics?.delta ?? 0) < 500 ? '#2962ff' : '#f7a600'}
          />
          <MetricCard
            label="Gamma"
            value={(metrics?.gamma ?? 0).toFixed(3)}
            sub="Rate of delta change"
            icon={BarChart3}
            color="#9c27b0"
          />
          <MetricCard
            label="Vega"
            value={(metrics?.vega ?? 0).toFixed(1)}
            sub="Volatility sensitivity"
            icon={ShieldCheck}
            color="#f7a600"
          />
        </div>
      ) : btMetrics ? (
        <div>
          <div className="flex items-center gap-2 mb-3">
            <span className="text-[12px] font-semibold" style={{ color: 'var(--tv-text-muted)' }}>
              From latest backtest
            </span>
            <Badge tone="blue">Backtest</Badge>
          </div>
          <div className="grid gap-3 grid-cols-2 sm:grid-cols-3 xl:grid-cols-6">
            <MetricCard
              label="Net P&L"
              value={`${btMetrics.net_pnl >= 0 ? '+' : ''}₹${Math.abs(btMetrics.net_pnl).toLocaleString()}`}
              sub={`${btMetrics.total_trades} trades`}
              icon={TrendingUp}
              color={btMetrics.net_pnl >= 0 ? '#26a69a' : '#ef5350'}
            />
            <MetricCard
              label="Win Rate"
              value={`${btMetrics.win_rate.toFixed(1)}%`}
              sub={btMetrics.win_rate > 55 ? 'Above average' : 'Below target'}
              icon={BarChart3}
              color={btMetrics.win_rate > 55 ? '#26a69a' : '#ef5350'}
            />
            <MetricCard
              label="Sharpe Ratio"
              value={btMetrics.sharpe.toFixed(2)}
              sub="Risk-adjusted return"
              icon={ShieldCheck}
              color={btMetrics.sharpe > 1 ? '#26a69a' : '#f7a600'}
            />
            <MetricCard
              label="Max Drawdown"
              value={`${btMetrics.max_drawdown.toFixed(1)}%`}
              sub="Worst peak-to-trough"
              icon={TrendingDown}
              color={btMetrics.max_drawdown < 15 ? '#26a69a' : '#ef5350'}
            />
            <MetricCard
              label="Profit Factor"
              value={btMetrics.profit_factor.toFixed(2)}
              sub="Gross profit / loss"
              icon={Zap}
              color={btMetrics.profit_factor > 1.5 ? '#26a69a' : '#f7a600'}
            />
            <MetricCard
              label="Total Return"
              value={`${btMetrics.total_return >= 0 ? '+' : ''}${btMetrics.total_return.toFixed(2)}%`}
              sub={`Ann. ${btMetrics.ann_return.toFixed(1)}%`}
              icon={Activity}
              color={btMetrics.total_return >= 0 ? '#26a69a' : '#ef5350'}
            />
          </div>
        </div>
      ) : (
        <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
          <MetricCard
            label="Open P&L"
            value="—"
            sub="No open positions"
            icon={TrendingUp}
            color="#26a69a"
          />
          <MetricCard
            label="Portfolio Delta"
            value="0.0"
            sub="Run a backtest or start trading"
            icon={BarChart3}
            color="#2962ff"
          />
          <MetricCard
            label="Win Rate"
            value="—"
            sub="No data yet"
            icon={BarChart3}
            color="#9c27b0"
          />
          <MetricCard
            label="Sharpe Ratio"
            value="—"
            sub="No data yet"
            icon={ShieldCheck}
            color="#f7a600"
          />
        </div>
      )}

      {/* ── Market Regime Analysis (real data from Yahoo Finance) ── */}
      <div
        className="rounded-md overflow-hidden"
        style={{ background: 'var(--tv-bg-surface)', border: '1px solid var(--tv-border)' }}
      >
        <div
          className="flex items-center justify-between px-4 py-3 border-b"
          style={{ borderColor: 'var(--tv-border)' }}
        >
          <div className="flex items-center gap-2">
            <BrainCircuit size={14} style={{ color: '#2962ff' }} />
            <span className="text-[13px] font-semibold" style={{ color: 'var(--tv-text-primary)' }}>
              Market Regime Analysis
            </span>
            <Badge tone="blue">HMM-Detected</Badge>
          </div>
          {regimeData?.updatedAt && (
            <span className="text-[10px]" style={{ color: 'var(--tv-text-muted)' }}>
              Updated {new Date(regimeData.updatedAt).toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit' })} IST
            </span>
          )}
        </div>

        {regimeLoading ? (
          <div className="px-4 py-12 flex items-center justify-center">
            <span className="text-[13px]" style={{ color: 'var(--tv-text-muted)' }}>Analyzing market data…</span>
          </div>
        ) : nifty && cfg ? (
          <div className="p-4 space-y-4">
            {/* NIFTY regime */}
            <div className="grid gap-4 xl:grid-cols-3">
              <div
                className="rounded-lg p-4 xl:col-span-1"
                style={{ background: cfg.bgColor, border: `1px solid ${cfg.borderColor}` }}
              >
                <div className="flex items-center gap-2 mb-3">
                  <div
                    className="flex h-9 w-9 items-center justify-center rounded-lg"
                    style={{ background: `${cfg.color}20`, border: `1px solid ${cfg.color}40` }}
                  >
                    <cfg.icon size={18} style={{ color: cfg.color }} />
                  </div>
                  <div>
                    <p className="text-[10px] font-medium" style={{ color: 'var(--tv-text-muted)' }}>NIFTY 50 Regime</p>
                    <p className="text-[18px] font-bold tracking-tight" style={{ color: cfg.color }}>
                      {nifty.regime.replace('_', ' ')}
                    </p>
                  </div>
                </div>
                <div className="mb-3">
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-[10px]" style={{ color: 'var(--tv-text-muted)' }}>Confidence</span>
                    <span className="text-[12px] font-mono font-semibold" style={{ color: cfg.color }}>
                      {(nifty.confidence * 100).toFixed(0)}%
                    </span>
                  </div>
                  <div className="h-1.5 rounded-full overflow-hidden" style={{ background: 'var(--tv-bg-elevated)' }}>
                    <div
                      className="h-full rounded-full"
                      style={{ width: `${nifty.confidence * 100}%`, background: cfg.color }}
                    />
                  </div>
                </div>
                <p className="text-[11px] leading-relaxed" style={{ color: 'var(--tv-text-secondary)' }}>
                  {nifty.description}
                </p>
              </div>

              {/* Technical indicators */}
              <div className="xl:col-span-2 grid grid-cols-2 sm:grid-cols-3 gap-3">
                {[
                  {
                    label: 'Hurst Exponent',
                    value: nifty.hurst.toFixed(3),
                    hint: nifty.hurst > 0.55 ? 'Trending' : nifty.hurst < 0.45 ? 'Mean-reverting' : 'Random walk',
                    color: nifty.hurst > 0.55 ? '#26a69a' : nifty.hurst < 0.45 ? '#2962ff' : '#f7a600',
                  },
                  {
                    label: 'ADX (14)',
                    value: nifty.adx.toFixed(1),
                    hint: nifty.adx > 25 ? 'Strong trend' : 'Weak trend',
                    color: nifty.adx > 25 ? '#26a69a' : '#f7a600',
                  },
                  {
                    label: 'Annualized Vol',
                    value: `${(nifty.volatility * 100).toFixed(1)}%`,
                    hint: nifty.volatility > 0.25 ? 'High' : nifty.volatility > 0.15 ? 'Moderate' : 'Low',
                    color: nifty.volatility > 0.25 ? '#ef5350' : '#26a69a',
                  },
                  {
                    label: 'NIFTY Price',
                    value: nifty.currentPrice.toLocaleString('en-IN', { minimumFractionDigits: 2 }),
                    hint: nifty.currentPrice > (nifty.sma20 ?? 0) ? 'Above SMA-20' : 'Below SMA-20',
                    color: nifty.currentPrice > (nifty.sma20 ?? 0) ? '#26a69a' : '#ef5350',
                  },
                  {
                    label: 'SMA-20',
                    value: (nifty.sma20 ?? 0).toLocaleString('en-IN', { minimumFractionDigits: 2 }),
                    hint: '20-day moving average',
                    color: 'var(--tv-text-primary)',
                  },
                  {
                    label: 'SMA-50',
                    value: (nifty.sma50 ?? 0).toLocaleString('en-IN', { minimumFractionDigits: 2 }),
                    hint: (nifty.sma20 ?? 0) > (nifty.sma50 ?? 0) ? 'Golden cross' : 'Death cross',
                    color: (nifty.sma20 ?? 0) > (nifty.sma50 ?? 0) ? '#26a69a' : '#ef5350',
                  },
                ].map((ind) => (
                  <div
                    key={ind.label}
                    className="rounded-md p-3"
                    style={{ background: 'var(--tv-bg-elevated)', border: '1px solid var(--tv-border)' }}
                  >
                    <p className="panel-caption mb-1">{ind.label}</p>
                    <p className="text-[16px] font-bold font-mono" style={{ color: ind.color }}>{ind.value}</p>
                    <p className="text-[10px] mt-0.5" style={{ color: 'var(--tv-text-muted)' }}>{ind.hint}</p>
                  </div>
                ))}
              </div>
            </div>

            {/* BANKNIFTY regime (if available) */}
            {bankNifty && bnCfg && (
              <div
                className="rounded-lg p-3 flex flex-wrap items-center gap-4"
                style={{ background: bnCfg.bgColor, border: `1px solid ${bnCfg.borderColor}` }}
              >
                <div className="flex items-center gap-2">
                  <bnCfg.icon size={14} style={{ color: bnCfg.color }} />
                  <span className="text-[12px] font-semibold" style={{ color: bnCfg.color }}>
                    BANKNIFTY: {bankNifty.regime.replace('_', ' ')}
                  </span>
                  <Badge tone={bnCfg.tone}>{(bankNifty.confidence * 100).toFixed(0)}%</Badge>
                </div>
                <span className="text-[12px] font-mono" style={{ color: 'var(--tv-text-primary)' }}>
                  ₹{bankNifty.currentPrice.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                </span>
                <span className="text-[11px]" style={{ color: 'var(--tv-text-muted)' }}>
                  Hurst: {bankNifty.hurst.toFixed(3)} · ADX: {bankNifty.adx.toFixed(1)} · Vol: {(bankNifty.volatility * 100).toFixed(1)}%
                </span>
              </div>
            )}

            {/* Momentum summary */}
            {nifty.shortTermMomentum !== undefined && (
              <div className="grid grid-cols-2 gap-3">
                <div
                  className="rounded-md p-3 flex items-center gap-3"
                  style={{ background: 'var(--tv-bg-elevated)', border: '1px solid var(--tv-border)' }}
                >
                  {(nifty.shortTermMomentum ?? 0) >= 0 ? (
                    <TrendingUp size={16} style={{ color: '#26a69a' }} />
                  ) : (
                    <TrendingDown size={16} style={{ color: '#ef5350' }} />
                  )}
                  <div>
                    <p className="panel-caption">5-Day Momentum</p>
                    <p
                      className="text-[14px] font-bold font-mono"
                      style={{ color: (nifty.shortTermMomentum ?? 0) >= 0 ? '#26a69a' : '#ef5350' }}
                    >
                      {(nifty.shortTermMomentum ?? 0) >= 0 ? '+' : ''}
                      {((nifty.shortTermMomentum ?? 0) * 100).toFixed(3)}%
                    </p>
                  </div>
                </div>
                <div
                  className="rounded-md p-3 flex items-center gap-3"
                  style={{ background: 'var(--tv-bg-elevated)', border: '1px solid var(--tv-border)' }}
                >
                  {(nifty.mediumTermMomentum ?? 0) >= 0 ? (
                    <TrendingUp size={16} style={{ color: '#26a69a' }} />
                  ) : (
                    <TrendingDown size={16} style={{ color: '#ef5350' }} />
                  )}
                  <div>
                    <p className="panel-caption">20-Day Momentum</p>
                    <p
                      className="text-[14px] font-bold font-mono"
                      style={{ color: (nifty.mediumTermMomentum ?? 0) >= 0 ? '#26a69a' : '#ef5350' }}
                    >
                      {(nifty.mediumTermMomentum ?? 0) >= 0 ? '+' : ''}
                      {((nifty.mediumTermMomentum ?? 0) * 100).toFixed(3)}%
                    </p>
                  </div>
                </div>
              </div>
            )}
          </div>
        ) : (
          <div className="px-4 py-12 flex items-center justify-center">
            <span className="text-[13px]" style={{ color: 'var(--tv-text-muted)' }}>
              Unable to load regime data
            </span>
          </div>
        )}
      </div>

      {/* Market news is in sidebar under Information; analytics uses it for regime/strategy context */}
      {news.length > 0 && (
        <p className="text-[11px]" style={{ color: 'var(--tv-text-muted)' }}>
          Using {news.length} market headline{news.length !== 1 ? 's' : ''} for regime and strategy context. View in sidebar → Information → Market News.
        </p>
      )}

      {/* ── Equity Curve ── */}
      <Card>
        <div className="flex items-center justify-between mb-3">
          <h2 className="font-heading text-xl">Equity Curve</h2>
          {equitySource === 'sample' && <Badge tone="warning">Sample Data</Badge>}
          {equitySource === 'backtest' && <Badge tone="blue">From Backtest</Badge>}
        </div>
        {posLoading || btLoading ? (
          <div className="h-32 flex items-center justify-center rounded-md"
            style={{ background: 'var(--tv-bg-elevated)', border: '1px solid var(--tv-border)' }}>
            <p className="text-[13px]" style={{ color: 'var(--tv-text-muted)' }}>Loading…</p>
          </div>
        ) : (
          <>
            <EquityCurveChart values={equityPoints} />
            {equitySource === 'sample' && (
              <p className="text-[11px] mt-2 text-center" style={{ color: 'var(--tv-text-muted)' }}>
                Showing sample equity curve. Run a backtest or start trading to see real data.
              </p>
            )}
            {equitySource === 'backtest' && (
              <p className="text-[11px] mt-2 text-center" style={{ color: 'var(--tv-text-muted)' }}>
                Showing equity curve from your latest completed backtest.
              </p>
            )}
          </>
        )}
      </Card>

      {/* ── Test Portfolio State ── */}
      <Card>
        <button
          type="button"
          onClick={() => setTestOpen(!testOpen)}
          className="w-full flex items-center justify-between"
        >
          <div className="flex items-center gap-2">
            <FlaskConical size={16} style={{ color: '#f7a600' }} />
            <h2 className="font-heading text-lg">Test Portfolio State</h2>
            <Badge tone="warning">Dev Tool</Badge>
          </div>
          {testOpen
            ? <ChevronUp size={16} style={{ color: 'var(--tv-text-muted)' }} />
            : <ChevronDown size={16} style={{ color: 'var(--tv-text-muted)' }} />
          }
        </button>
        {testOpen && (
          <div className="mt-4">
            <p className="text-[12px] mb-3" style={{ color: 'var(--tv-text-muted)' }}>
              Enter values below and click Apply to see them reflected in the Greeks Exposure section.
            </p>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-3">
              {[
                { label: 'Delta', value: testDelta, set: setTestDelta, hint: 'Price sensitivity', color: '#2962ff' },
                { label: 'Gamma', value: testGamma, set: setTestGamma, hint: 'Delta acceleration', color: '#9c27b0' },
                { label: 'Theta', value: testTheta, set: setTestTheta, hint: 'Daily time decay (₹)', color: '#ef5350' },
                { label: 'Vega',  value: testVega,  set: setTestVega,  hint: 'Volatility sensitivity', color: '#f7a600' },
              ].map((field) => (
                <div key={field.label}>
                  <label className="block text-[11px] font-semibold mb-1" style={{ color: field.color }}>
                    {field.label}
                  </label>
                  <input
                    type="number"
                    step="any"
                    value={field.value}
                    onChange={(e) => field.set(e.target.value)}
                    className="w-full rounded-md px-3 py-2 text-[13px] font-mono outline-none"
                    style={{
                      background: 'var(--tv-bg-elevated)',
                      border: '1px solid var(--tv-border)',
                      color: 'var(--tv-text-primary)',
                    }}
                    placeholder={`e.g. ${field.label === 'Gamma' ? '0.25' : field.label === 'Theta' ? '-45' : '120'}`}
                  />
                  <span className="block text-[10px] mt-0.5" style={{ color: 'var(--tv-text-muted)' }}>
                    {field.hint}
                  </span>
                </div>
              ))}
            </div>
            <div className="flex items-center gap-2">
              <button
                type="button"
                onClick={handleApplyTest}
                disabled={testSaving}
                className="tv-btn tv-btn-primary text-[12px] py-1.5 px-4"
              >
                {testSaving ? 'Applying…' : 'Apply'}
              </button>
              <button
                type="button"
                onClick={handleResetTest}
                disabled={testSaving}
                className="tv-btn tv-btn-ghost text-[12px] py-1.5 px-4"
              >
                Reset to Zero
              </button>
            </div>
          </div>
        )}
      </Card>

      {/* ── Greeks Exposure ── */}
      <Card>
        <div className="flex items-center justify-between mb-3">
          <h2 className="font-heading text-xl">Greeks Exposure</h2>
          {greeksLoading && (
            <span className="text-[11px]" style={{ color: 'var(--tv-text-muted)' }}>Loading…</span>
          )}
          {!greeksLoading && metrics?.trading_allowed === false && (
            <span className="text-[11px] font-semibold" style={{ color: '#ef5350' }}>
              Circuit Breaker Active
            </span>
          )}
        </div>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
          {[
            {
              label: 'Delta',
              value: greeks.delta.toFixed(2),
              color: '#2962ff',
              hint: 'Price sensitivity',
              limit: metrics ? `Limit: ${metrics.delta !== undefined ? '±500' : '—'}` : null,
            },
            {
              label: 'Gamma',
              value: greeks.gamma.toFixed(4),
              color: '#9c27b0',
              hint: 'Delta acceleration',
              limit: null,
            },
            {
              label: 'Theta',
              value: greeks.theta.toFixed(2),
              color: '#ef5350',
              hint: 'Daily time decay (₹)',
              limit: null,
            },
            {
              label: 'Vega',
              value: greeks.vega.toFixed(2),
              color: '#f7a600',
              hint: 'Volatility sensitivity',
              limit: metrics ? `Limit: 10,000` : null,
            },
          ].map((g) => (
            <div
              key={g.label}
              className="flex flex-col items-center justify-center py-4 rounded-md"
              style={{
                background: `color-mix(in srgb, ${g.color}12, var(--tv-bg-elevated) 88%)`,
                border: `1px solid ${g.color}22`,
              }}
            >
              <p className="panel-caption mb-1">{g.label}</p>
              <p className="text-[22px] font-bold font-mono" style={{ color: g.color }}>
                {g.value}
              </p>
              <p className="text-[10px] mt-1" style={{ color: 'var(--tv-text-muted)' }}>
                {g.hint}
              </p>
              {g.limit && (
                <p className="text-[10px] mt-0.5" style={{ color: 'var(--tv-text-muted)' }}>
                  {g.limit}
                </p>
              )}
            </div>
          ))}
        </div>
      </Card>

      {/* ── Open Positions with per-stock Greeks ── */}
      {hasData && (
        <Card>
          <h2 className="mb-3 font-heading text-xl">Open Positions &amp; Greeks</h2>
          <div className="overflow-x-auto">
            <table className="tv-table w-full">
              <thead>
                <tr>
                  <th>Symbol</th>
                  <th className="text-right">Qty</th>
                  <th className="text-right">Avg Price</th>
                  <th className="text-right">Current</th>
                  <th className="text-right">P&L</th>
                  <th className="text-right" style={{ color: '#2962ff' }}>Delta</th>
                  <th className="text-right" style={{ color: '#9c27b0' }}>Gamma</th>
                  <th className="text-right" style={{ color: '#ef5350' }}>Theta</th>
                  <th className="text-right" style={{ color: '#f7a600' }}>Vega</th>
                </tr>
              </thead>
              <tbody>
                {positions.map((p) => (
                  <tr key={p.symbol}>
                    <td className="font-semibold" style={{ color: 'var(--tv-text-primary)' }}>{p.symbol}</td>
                    <td className="text-right font-mono">{p.quantity}</td>
                    <td className="text-right font-mono">₹{p.avg_price.toFixed(2)}</td>
                    <td className="text-right font-mono">₹{p.current_price.toFixed(2)}</td>
                    <td className="text-right font-mono font-semibold"
                      style={{ color: p.pnl >= 0 ? '#26a69a' : '#ef5350' }}>
                      {p.pnl >= 0 ? '+' : ''}₹{p.pnl.toFixed(2)}
                    </td>
                    <td className="text-right font-mono" style={{ color: '#2962ff' }}>{p.delta.toFixed(2)}</td>
                    <td className="text-right font-mono" style={{ color: '#9c27b0' }}>{p.gamma.toFixed(4)}</td>
                    <td className="text-right font-mono" style={{ color: '#ef5350' }}>{p.theta.toFixed(2)}</td>
                    <td className="text-right font-mono" style={{ color: '#f7a600' }}>{p.vega.toFixed(2)}</td>
                  </tr>
                ))}
              </tbody>
              <tfoot>
                <tr style={{ borderTop: '2px solid var(--tv-border)' }}>
                  <td colSpan={5} className="font-semibold text-right" style={{ color: 'var(--tv-text-muted)' }}>
                    Portfolio Total
                  </td>
                  <td className="text-right font-mono font-semibold" style={{ color: '#2962ff' }}>
                    {positions.reduce((s, p) => s + p.delta, 0).toFixed(2)}
                  </td>
                  <td className="text-right font-mono font-semibold" style={{ color: '#9c27b0' }}>
                    {positions.reduce((s, p) => s + p.gamma, 0).toFixed(4)}
                  </td>
                  <td className="text-right font-mono font-semibold" style={{ color: '#ef5350' }}>
                    {positions.reduce((s, p) => s + p.theta, 0).toFixed(2)}
                  </td>
                  <td className="text-right font-mono font-semibold" style={{ color: '#f7a600' }}>
                    {positions.reduce((s, p) => s + p.vega, 0).toFixed(2)}
                  </td>
                </tr>
              </tfoot>
            </table>
          </div>
        </Card>
      )}

      {!hasData && !posLoading && (
        <Card>
          <div className="py-8 flex flex-col items-center gap-3 text-center">
            <BarChart3 size={28} style={{ color: 'var(--tv-text-muted)' }} />
            <p className="text-[14px] font-semibold" style={{ color: 'var(--tv-text-primary)' }}>
              No trading data yet
            </p>
            <p className="text-[12px]" style={{ color: 'var(--tv-text-muted)' }}>
              Analytics will populate as your strategies execute trades.
              Each stock position will show its own Delta, Gamma, Theta, and Vega.
            </p>
          </div>
        </Card>
      )}
    </div>
  );
}
