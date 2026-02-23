'use client';

import { useCallback, useEffect, useRef, useState } from 'react';
import gsap from 'gsap';
import {
  Activity,
  BarChart3,
  CheckCircle2,
  FlaskConical,
  Play,
  RotateCcw,
  Settings,
  TrendingDown,
  TrendingUp,
} from 'lucide-react';
import { Badge } from '@/lib/ui';
import { apiClient } from '@/lib/api-client';
import { useStrategies } from '@/hooks/use-strategies';

/* ─── Types ───────────────────────────────────────────────────────────────── */
type BacktestRun = {
  jobId:        string;
  strategyId:   string;
  strategyName: string;
  symbol:       string;
  from:         string;
  to:           string;
  capital:      number;
  status:       'pending' | 'running' | 'completed' | 'failed';
  progress:     number;
  // populated after completion
  netPnl?:       number;
  totalReturn?:  number;
  annReturn?:    number;
  sharpe?:       number;
  sortino?:      number;
  maxDrawdown?:  number;
  winRate?:      number;
  avgWin?:       number;
  avgLoss?:      number;
  totalTrades?:  number;
  profitFactor?: number;
  calmar?:       number;
  equity?:       number[];
};

/* ─── Equity curve (SVG sparkline) ───────────────────────────────────────── */
function EquityCurve({ data, color, height = 80 }: { data: number[]; color: string; height?: number }) {
  const w = 300, h = height;
  const min = Math.min(...data);
  const max = Math.max(...data);
  const range = max - min || 1;
  const pts = data.map((v, i) => `${(i / (data.length - 1)) * w},${h - ((v - min) / range) * (h - 4) - 2}`);
  const polyline = pts.join(' ');
  const fill = `${polyline} ${w},${h} 0,${h}`;

  return (
    <svg viewBox={`0 0 ${w} ${h}`} className="w-full" style={{ height }}>
      <defs>
        <linearGradient id={`eqgrad-${color.replace('#', '')}`} x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor={color} stopOpacity={0.25} />
          <stop offset="100%" stopColor={color} stopOpacity={0} />
        </linearGradient>
      </defs>
      <polygon points={fill} fill={`url(#eqgrad-${color.replace('#', '')})`} />
      <polyline points={polyline} fill="none" stroke={color} strokeWidth={1.5} strokeLinecap="round" />
    </svg>
  );
}

function MetricCell({ label, value, good }: { label: string; value: string; good?: boolean | null }) {
  return (
    <div className="text-center py-3 px-2">
      <p className="panel-caption mb-1">{label}</p>
      <p
        className="text-[13px] font-mono font-semibold"
        style={{ color: good === true ? '#26a69a' : good === false ? '#ef5350' : 'var(--tv-text-primary)' }}
      >
        {value}
      </p>
    </div>
  );
}

/* ─── Page ────────────────────────────────────────────────────────────────── */
export default function BacktestingPage() {
  const pageRef   = useRef<HTMLDivElement>(null);
  const pollRef   = useRef<ReturnType<typeof setInterval> | null>(null);
  const { strategies } = useStrategies();

  const [runs, setRuns]         = useState<BacktestRun[]>([]);
  const [selected, setSelected] = useState<BacktestRun | null>(null);
  const [configOpen, setConfigOpen] = useState(false);

  // Config form state
  const [cfgStrategyId, setCfgStrategyId] = useState('');
  const [cfgSymbol, setCfgSymbol]         = useState('NIFTY');
  const [cfgStrategyType, setCfgStrategyType] = useState('momentum');
  const [cfgFrom, setCfgFrom]             = useState('');
  const [cfgTo, setCfgTo]                 = useState('');
  const [cfgCapital, setCfgCapital]       = useState('1000000');
  const [isRunning, setIsRunning]         = useState(false);
  const [progress, setProgress]           = useState(0);
  const [runError, setRunError]           = useState<string | null>(null);

  // Fetch full results for a completed run (metrics + equity curve)
  const loadResults = useCallback(async (jobId: string) => {
    try {
      const results = await apiClient.backtest.results(jobId);
      const completed = mapApiRun({ ...results, job_id: jobId, status: 'completed', progress: 1 });
      setRuns((prev) => prev.map((r) => r.jobId === jobId ? completed : r));
      setSelected(completed);
    } catch { /* ignore */ }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Load existing backtest runs on mount, then auto-load results for first completed run
  useEffect(() => {
    apiClient.backtest.list()
      .then(async (data) => {
        const mapped = data.map((r) => mapApiRun(r));
        setRuns(mapped);
        // Auto-select and load results for the first completed run
        const firstCompleted = mapped.find((r) => r.status === 'completed');
        if (firstCompleted) {
          setSelected(firstCompleted);
          loadResults(firstCompleted.jobId);
        } else if (mapped.length > 0) {
          setSelected(mapped[0]);
        }
      })
      .catch(() => {/* backend may not have runs yet */});
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Set default strategy when strategies load
  useEffect(() => {
    if (strategies.length > 0 && !cfgStrategyId) {
      setCfgStrategyId(strategies[0].id);
    }
  }, [strategies, cfgStrategyId]);

  useEffect(() => {
    if (!pageRef.current) return;
    const ctx = gsap.context(() => {
      gsap.fromTo('.bt-header', { opacity: 0, y: -14 }, { opacity: 1, y: 0, duration: 0.4, ease: 'power3.out' });
      gsap.fromTo('.bt-panel',  { opacity: 0, y: 20  }, { opacity: 1, y: 0, duration: 0.45, ease: 'power3.out', stagger: 0.07, delay: 0.1 });
    }, pageRef);
    return () => ctx.revert();
  }, []);

  const mapApiRun = (r: Record<string, unknown>): BacktestRun => {
    const metrics = (r.metrics ?? {}) as Record<string, unknown>;
    // config holds symbol/strategy_type when they aren't top-level
    const config  = (r.config  ?? {}) as Record<string, unknown>;

    // Equity curve: backend sends [{t, value, timestamp}, ...]
    const equity = Array.isArray(r.equity_curve)
      ? (r.equity_curve as Record<string, unknown>[]).map((e) => Number(e.value ?? e.equity ?? 0))
      : [];

    // Symbol: top-level > config > metrics
    const symbol = String(r.symbol ?? config.symbol ?? metrics.symbol ?? '--');

    // Dates
    const from = String(r.start_date ?? r.from ?? config.start_date ?? '');
    const to   = String(r.end_date   ?? r.to   ?? config.end_date   ?? '');

    // ── Metrics ──
    // Backend now sends percentages as actual % values (e.g. win_rate=33.33, total_return=-1.23)
    // and net_pnl / avg_win / avg_loss in ₹.
    const netPnl       = Number(metrics.net_pnl       ?? metrics.total_pnl ?? 0);
    const totalReturn  = Number(metrics.total_return   ?? 0);   // already in %
    const annReturn    = Number(metrics.ann_return     ?? (Number(metrics.cagr ?? 0) * 100));
    const sharpe       = Number(metrics.sharpe         ?? 0);
    const sortino      = Number(metrics.sortino        ?? 0);
    // max_drawdown: backend sends positive %; older runs sent negative decimal → normalise
    const rawDD        = Number(metrics.max_drawdown   ?? 0);
    const maxDrawdown  = rawDD <= 0 ? Math.abs(rawDD) * 100 : rawDD;   // always positive %
    // win_rate: backend sends %; older runs sent fraction → normalise
    const rawWR        = Number(metrics.win_rate       ?? 0);
    const winRate      = rawWR <= 1 ? rawWR * 100 : rawWR;             // always %
    const profitFactor = Number(metrics.profit_factor  ?? 0);
    const calmar       = Number(metrics.calmar         ?? 0);
    const avgWin       = Number(metrics.avg_win        ?? 0);
    const avgLoss      = Number(metrics.avg_loss       ?? 0);
    const totalTrades  = Number(metrics.total_trades   ?? metrics.num_trades ?? 0);

    return {
      jobId:        String(r.job_id ?? r.id ?? ''),
      strategyId:   String(r.strategy_id ?? config.strategy_id ?? ''),
      strategyName: String(r.strategy_name ?? config.strategy_name ?? r.strategy_id ?? 'Strategy'),
      symbol,
      from,
      to,
      capital:      Number(r.initial_capital ?? config.initial_capital ?? 1_000_000),
      status:       (r.status as BacktestRun['status']) ?? 'pending',
      progress:     Number(r.progress ?? 0),
      netPnl,
      totalReturn,
      annReturn,
      sharpe,
      sortino,
      maxDrawdown,
      winRate,
      avgWin,
      avgLoss,
      totalTrades,
      profitFactor,
      calmar,
      equity,
    };
  };

  const pollStatus = useCallback((jobId: string) => {
    if (pollRef.current) clearInterval(pollRef.current);
    pollRef.current = setInterval(async () => {
      try {
        const status = await apiClient.backtest.status(jobId);
        setProgress(status.progress * 100);
        setRuns((prev) => prev.map((r) => r.jobId === jobId ? { ...r, progress: status.progress * 100, status: status.status as BacktestRun['status'] } : r));

        if (status.status === 'completed' || status.status === 'failed') {
          clearInterval(pollRef.current!);
          pollRef.current = null;
          setIsRunning(false);

          if (status.status === 'completed') {
            const results = await apiClient.backtest.results(jobId);
            const completed = mapApiRun({ ...results, job_id: jobId, status: 'completed', progress: 1 });
            setRuns((prev) => prev.map((r) => r.jobId === jobId ? completed : r));
            setSelected(completed);
          }
        }
      } catch {
        clearInterval(pollRef.current!);
        pollRef.current = null;
        setIsRunning(false);
      }
    }, 1500);
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const runBacktest = async () => {
    setRunError(null);
    if (!cfgSymbol.trim()) { setRunError('Please enter a symbol (e.g. NIFTY, RELIANCE)'); return; }

    try {
      setIsRunning(true);
      setProgress(0);
      const strategy = strategies.find((s) => s.id === cfgStrategyId);
      const { job_id } = await apiClient.backtest.create({
        strategy_id:            cfgStrategyId || undefined,
        symbol:                 cfgSymbol.trim(),
        strategy_type:          cfgStrategyType,
        start_date:             cfgFrom ? new Date(cfgFrom).toISOString() : undefined,
        end_date:               cfgTo   ? new Date(cfgTo).toISOString()   : undefined,
        initial_capital:        Number(cfgCapital),
        transaction_cost_model: 'realistic',
      });

      const newRun: BacktestRun = {
        jobId:        job_id,
        strategyId:   cfgStrategyId,
        strategyName: strategy?.name ?? cfgStrategyType,
        symbol:       cfgSymbol,
        from:         cfgFrom,
        to:           cfgTo,
        capital:      Number(cfgCapital),
        status:       'running',
        progress:     0,
      };
      setRuns((prev) => [newRun, ...prev]);
      setSelected(newRun);
      setConfigOpen(false);
      pollStatus(job_id);
    } catch (err) {
      setIsRunning(false);
      setRunError(err instanceof Error ? err.message : 'Failed to start backtest');
    }
  };

  const completedRuns = runs.filter((r) => r.status === 'completed');
  const pnlUp = (selected?.netPnl ?? 0) >= 0;

  return (
    <div ref={pageRef} className="space-y-4">

      {/* Header */}
      <div className="bt-header flex flex-wrap items-center justify-between gap-3">
        <div>
          <p className="panel-caption mb-1">Historical Simulation Engine</p>
          <h1 className="text-[17px] font-semibold tracking-tight" style={{ color: 'var(--tv-text-primary)' }}>
            Backtesting
          </h1>
        </div>
        <div className="flex items-center gap-2">
          {completedRuns.length > 0 && (
            <Badge tone="blue">{completedRuns.length} Completed Run{completedRuns.length !== 1 ? 's' : ''}</Badge>
          )}
          <button
            onClick={() => setConfigOpen((v) => !v)}
            className="tv-btn tv-btn-primary flex items-center gap-1.5"
          >
            <Play size={13} /> Run New Backtest
          </button>
        </div>
      </div>

      {/* Config panel */}
      {configOpen && (
        <div className="bt-panel tv-panel p-5">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <Settings size={14} style={{ color: 'var(--tv-blue)' }} />
              <h2 className="panel-title">Backtest Configuration</h2>
            </div>
            <button onClick={() => setConfigOpen(false)} className="tv-btn tv-btn-ghost text-[11px] py-1 px-2">
              Close
            </button>
          </div>

          {strategies.length === 0 ? (
            <div className="rounded-md px-4 py-6 text-center"
              style={{ background: 'rgba(41,98,255,0.06)', border: '1px solid rgba(41,98,255,0.15)' }}>
              <p className="text-[13px] font-semibold" style={{ color: 'var(--tv-text-primary)' }}>No strategies found</p>
              <p className="text-[12px] mt-1" style={{ color: 'var(--tv-text-muted)' }}>
                Create a strategy first before running a backtest
              </p>
            </div>
          ) : (
            <>
              <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
                <div>
                  <label className="panel-caption mb-1.5 block">Strategy</label>
                  <select
                    className="tv-select w-full"
                    value={cfgStrategyId}
                    onChange={(e) => {
                      const sid = e.target.value;
                      setCfgStrategyId(sid);
                      const s = strategies.find((st) => st.id === sid);
                      if (s?.parameters) {
                        const p = s.parameters as Record<string, unknown>;
                        if (p.symbol)        setCfgSymbol(String(p.symbol));
                        if (p.strategy_type) setCfgStrategyType(String(p.strategy_type));
                      }
                    }}
                  >
                    <option value="">— Select strategy —</option>
                    {strategies.map((s) => (
                      <option key={s.id} value={s.id}>{s.name}</option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="panel-caption mb-1.5 block">Symbol</label>
                  <input
                    className="tv-input w-full"
                    type="text"
                    placeholder="e.g. NIFTY, RELIANCE, TCS"
                    value={cfgSymbol}
                    onChange={(e) => setCfgSymbol(e.target.value.toUpperCase())}
                  />
                </div>
                <div>
                  <label className="panel-caption mb-1.5 block">Strategy Type</label>
                  <select
                    className="tv-select w-full"
                    value={cfgStrategyType}
                    onChange={(e) => setCfgStrategyType(e.target.value)}
                  >
                    <option value="momentum">Momentum</option>
                    <option value="mean_reversion">Mean Reversion</option>
                    <option value="breakout">Breakout</option>
                    <option value="ema_crossover">EMA Crossover</option>
                  </select>
                </div>
                <div>
                  <label className="panel-caption mb-1.5 block">Initial Capital (₹)</label>
                  <input
                    className="tv-input w-full"
                    type="number"
                    value={cfgCapital}
                    onChange={(e) => setCfgCapital(e.target.value)}
                  />
                </div>
                <div>
                  <label className="panel-caption mb-1.5 block">Transaction Cost Model</label>
                  <select className="tv-select w-full" defaultValue="realistic">
                    <option value="realistic">Realistic</option>
                    <option value="zero">Zero Cost</option>
                  </select>
                </div>
                <div>
                  <label className="panel-caption mb-1.5 block">From Date</label>
                  <input
                    type="date"
                    className="tv-input w-full"
                    value={cfgFrom}
                    onChange={(e) => setCfgFrom(e.target.value)}
                  />
                </div>
                <div>
                  <label className="panel-caption mb-1.5 block">To Date</label>
                  <input
                    type="date"
                    className="tv-input w-full"
                    value={cfgTo}
                    onChange={(e) => setCfgTo(e.target.value)}
                  />
                </div>
              </div>

              {isRunning && (
                <div className="mt-4">
                  <div className="flex items-center justify-between mb-1.5">
                    <span className="text-[12px] font-medium" style={{ color: 'var(--tv-text-primary)' }}>
                      Running simulation…
                    </span>
                    <span className="text-[12px] font-mono" style={{ color: 'var(--tv-text-muted)' }}>
                      {Math.round(progress)}%
                    </span>
                  </div>
                  <div className="h-2 rounded-full overflow-hidden" style={{ background: 'var(--tv-bg-elevated)' }}>
                    <div
                      className="h-full rounded-full transition-all"
                      style={{ width: `${progress}%`, background: 'linear-gradient(90deg, #2962ff, #26a69a)' }}
                    />
                  </div>
                </div>
              )}

              {runError && (
                <p className="mt-3 text-[12px]" style={{ color: '#ef5350' }}>{runError}</p>
              )}

              <div className="mt-4 flex items-center gap-2">
                <button
                  onClick={runBacktest}
                  disabled={isRunning}
                  className="tv-btn tv-btn-primary flex items-center gap-1.5 disabled:opacity-50"
                >
                  {isRunning
                    ? <><RotateCcw size={13} className="animate-spin" /> Running…</>
                    : <><Play size={13} /> Run Backtest</>
                  }
                </button>
                {progress === 100 && !isRunning && (
                  <div className="flex items-center gap-1.5 text-[12px]" style={{ color: '#26a69a' }}>
                    <CheckCircle2 size={13} /> Simulation complete
                  </div>
                )}
              </div>
            </>
          )}
        </div>
      )}

      {/* Empty state */}
      {runs.length === 0 && !configOpen && (
        <div className="bt-panel tv-panel py-16 flex flex-col items-center gap-4 text-center">
          <div className="h-14 w-14 rounded-full flex items-center justify-center"
            style={{ background: 'var(--tv-bg-elevated)' }}>
            <FlaskConical size={24} style={{ color: 'var(--tv-text-muted)' }} />
          </div>
          <div>
            <p className="text-[14px] font-semibold" style={{ color: 'var(--tv-text-primary)' }}>
              No backtest runs yet
            </p>
            <p className="text-[12px] mt-1" style={{ color: 'var(--tv-text-muted)' }}>
              Configure and run a backtest to simulate your strategy on historical data
            </p>
          </div>
          <button
            onClick={() => setConfigOpen(true)}
            className="tv-btn tv-btn-primary flex items-center gap-1.5"
          >
            <Play size={13} /> Run New Backtest
          </button>
        </div>
      )}

      {/* Results layout */}
      {runs.length > 0 && (
        <div className="grid gap-4 xl:grid-cols-4">
          {/* Runs list */}
          <div className="bt-panel tv-panel overflow-hidden xl:col-span-1">
            <div className="px-4 py-3 border-b" style={{ borderColor: 'var(--tv-border)' }}>
              <span className="panel-title">Backtest Runs</span>
            </div>
            <div className="divide-y" style={{ borderColor: 'var(--tv-border)' }}>
              {runs.map((run) => (
                <button
                  key={run.jobId}
                  onClick={() => {
                    if (run.status !== 'completed') return;
                    setSelected(run);
                    // Load full results (metrics + equity) if not already loaded
                    if (!run.equity?.length || !run.totalTrades) {
                      loadResults(run.jobId);
                    }
                  }}
                  className="w-full text-left px-4 py-3 transition-colors hover:bg-[var(--tv-bg-elevated)]"
                  style={{
                    background:  selected?.jobId === run.jobId ? 'var(--tv-bg-elevated)' : 'transparent',
                    borderLeft:  selected?.jobId === run.jobId ? '2px solid #2962ff' : '2px solid transparent',
                    cursor:      run.status === 'completed' ? 'pointer' : 'default',
                  }}
                >
                  <div className="flex items-center justify-between gap-2 mb-1">
                    <span className="text-[12px] font-semibold truncate" style={{ color: 'var(--tv-text-primary)' }}>
                      {run.strategyName}
                    </span>
                    <Badge
                      tone={run.status === 'completed' ? 'success' : run.status === 'running' ? 'warning' : run.status === 'failed' ? 'danger' : 'muted'}
                      dot={run.status === 'running'}
                    >
                      {run.status === 'running' ? 'Running' : run.status === 'completed' ? 'Done' : run.status === 'failed' ? 'Failed' : 'Pending'}
                    </Badge>
                  </div>
                  <div className="flex items-center gap-2 text-[10px]" style={{ color: 'var(--tv-text-muted)' }}>
                    <span>{run.symbol}</span>
                    {run.from && <><span>·</span><span>{run.from}</span></>}
                  </div>
                  {run.status === 'completed' && run.netPnl !== undefined && (
                    <p className="text-[12px] font-mono mt-1" style={{ color: run.netPnl >= 0 ? '#26a69a' : '#ef5350' }}>
                      {run.netPnl >= 0 ? '+' : ''}₹{run.netPnl.toLocaleString()}
                    </p>
                  )}
                  {run.status === 'running' && (
                    <div className="mt-2 h-1 rounded-full overflow-hidden" style={{ background: 'var(--tv-bg-base)' }}>
                      <div className="h-full rounded-full" style={{ width: `${run.progress}%`, background: '#f7a600' }} />
                    </div>
                  )}
                </button>
              ))}
            </div>
          </div>

          {/* Results panel */}
          <div className="space-y-4 xl:col-span-3">
            {selected && selected.status === 'completed' ? (
              <>
                {/* Equity curve */}
                <div className="bt-panel tv-panel overflow-hidden">
                  <div className="flex items-center justify-between px-4 py-3 border-b" style={{ borderColor: 'var(--tv-border)' }}>
                    <div className="flex items-center gap-2">
                      {pnlUp
                        ? <TrendingUp size={14} style={{ color: '#26a69a' }} />
                        : <TrendingDown size={14} style={{ color: '#ef5350' }} />
                      }
                      <span className="panel-title">Equity Curve — {selected.strategyName}</span>
                    </div>
                    <span className="text-[12px] font-mono" style={{ color: 'var(--tv-text-muted)' }}>
                      {selected.from} → {selected.to}
                    </span>
                  </div>
                  <div className="p-4">
                    {selected.equity && selected.equity.length > 1 ? (
                      <EquityCurve
                        data={selected.equity}
                        color={pnlUp ? '#26a69a' : '#ef5350'}
                        height={140}
                      />
                    ) : (
                      <div className="h-36 flex items-center justify-center text-[13px]"
                        style={{ color: 'var(--tv-text-muted)' }}>
                        No equity curve data available
                      </div>
                    )}
                  </div>
                </div>

                {/* Key metrics */}
                <div className="bt-panel tv-panel overflow-hidden">
                  <div className="px-4 py-3 border-b" style={{ borderColor: 'var(--tv-border)' }}>
                    <span className="panel-title">Performance Metrics</span>
                  </div>
                  <div className="grid grid-cols-3 sm:grid-cols-4 lg:grid-cols-6 divide-x divide-y"
                    style={{ borderColor: 'var(--tv-border)' }}>
                    <MetricCell label="Net P&L"
                      value={`${(selected.netPnl??0)>=0?'+':''}₹${Math.round(selected.netPnl??0).toLocaleString('en-IN')}`}
                      good={pnlUp} />
                    <MetricCell label="Total Return"
                      value={`${(selected.totalReturn??0)>=0?'+':''}${(selected.totalReturn??0).toFixed(2)}%`}
                      good={pnlUp} />
                    <MetricCell label="Sharpe Ratio"
                      value={(selected.sharpe??0).toFixed(2)}
                      good={(selected.sharpe??0) > 1} />
                    <MetricCell label="Sortino"
                      value={(selected.sortino??0).toFixed(2)}
                      good={(selected.sortino??0) > 1.5} />
                    <MetricCell label="Max Drawdown"
                      value={`${(selected.maxDrawdown??0).toFixed(2)}%`}
                      good={(selected.maxDrawdown??0) < 15} />
                    <MetricCell label="Win Rate"
                      value={`${(selected.winRate??0).toFixed(1)}%`}
                      good={(selected.winRate??0) > 55} />
                    <MetricCell label="Profit Factor"
                      value={(selected.profitFactor??0).toFixed(2)}
                      good={(selected.profitFactor??0) > 1.5} />
                    <MetricCell label="Calmar"
                      value={(selected.calmar??0).toFixed(2)}
                      good={(selected.calmar??0) > 1} />
                    <MetricCell label="Avg Win"
                      value={`₹${Math.round(selected.avgWin??0).toLocaleString('en-IN')}`}
                      good />
                    <MetricCell label="Avg Loss"
                      value={`₹${Math.round(Math.abs(selected.avgLoss??0)).toLocaleString('en-IN')}`}
                      good={null} />
                    <MetricCell label="Total Trades"
                      value={String(selected.totalTrades??0)}
                      good={null} />
                    <MetricCell label="Ann. Return"
                      value={`${(selected.annReturn??0)>=0?'+':''}${(selected.annReturn??0).toFixed(2)}%`}
                      good={(selected.annReturn??0) > 15} />
                  </div>
                </div>

                {/* Trade distribution */}
                <div className="bt-panel tv-panel p-4">
                  <h2 className="panel-title mb-3 flex items-center gap-2">
                    <Activity size={13} style={{ color: '#2962ff' }} /> Trade Distribution
                  </h2>
                  <div className="space-y-2.5">
                    {[
                      { label: 'Winning Trades', pct: selected.winRate ?? 0,                           color: '#26a69a' },
                      { label: 'Losing Trades',  pct: 100 - (selected.winRate ?? 0),                   color: '#ef5350' },
                      { label: 'Profit Factor',  pct: Math.min((selected.profitFactor ?? 0) * 33, 100),color: '#2962ff' },
                    ].map((r) => (
                      <div key={r.label}>
                        <div className="flex justify-between text-[11px] mb-1">
                          <span style={{ color: 'var(--tv-text-muted)' }}>{r.label}</span>
                          <span className="font-mono" style={{ color: r.color }}>{r.pct.toFixed(1)}%</span>
                        </div>
                        <div className="h-1.5 rounded-full overflow-hidden" style={{ background: 'var(--tv-bg-elevated)' }}>
                          <div className="h-full rounded-full" style={{ width: `${r.pct}%`, background: r.color }} />
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </>
            ) : selected && selected.status === 'running' ? (
              <div className="bt-panel tv-panel py-16 flex flex-col items-center gap-4 text-center">
                <RotateCcw size={28} className="animate-spin" style={{ color: '#f7a600' }} />
                <div>
                  <p className="text-[14px] font-semibold" style={{ color: 'var(--tv-text-primary)' }}>
                    Simulation in progress…
                  </p>
                  <p className="text-[12px] mt-1" style={{ color: 'var(--tv-text-muted)' }}>
                    {Math.round(selected.progress)}% complete
                  </p>
                </div>
              </div>
            ) : selected && selected.status === 'failed' ? (
              <div className="bt-panel tv-panel py-16 flex flex-col items-center gap-4 text-center">
                <BarChart3 size={28} style={{ color: '#ef5350' }} />
                <p className="text-[14px] font-semibold" style={{ color: '#ef5350' }}>Backtest failed</p>
              </div>
            ) : (
              <div className="bt-panel tv-panel py-16 flex flex-col items-center gap-4 text-center">
                <BarChart3 size={28} style={{ color: 'var(--tv-text-muted)' }} />
                <p className="text-[14px] font-semibold" style={{ color: 'var(--tv-text-primary)' }}>
                  Select a completed run to view results
                </p>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
