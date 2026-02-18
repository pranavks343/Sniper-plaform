'use client';

import { useEffect, useRef } from 'react';
import gsap from 'gsap';
import { BrainCircuit, Cpu, Layers, ShieldCheck, TrendingUp, Zap } from 'lucide-react';
import { Badge } from '@sniper/framework';
import { TradingCopilot } from '@/components/ai/trading-copilot';
import { useCopilotStore } from '@/store/copilot-store';

/* ── Capability tiles ─────────────────────────────────────────────────────── */
const CAPABILITIES = [
  {
    icon: Layers,
    color: '#2962ff',
    title: 'Regime-Aware',
    desc: 'Knows the current market regime (HMM-detected: BULL / BEAR / VOLATILE / RANGING) and calibrates advice accordingly.',
  },
  {
    icon: BrainCircuit,
    color: '#26a69a',
    title: 'Strategy-Aware',
    desc: 'Reads the selected strategy parameters, type, and last backtest results to give specific actionable feedback.',
  },
  {
    icon: ShieldCheck,
    color: '#f7a600',
    title: 'Risk-Aware',
    desc: 'Has live access to your delta exposure, VaR, drawdown %, and circuit-breaker thresholds.',
  },
  {
    icon: Cpu,
    color: '#9c27b0',
    title: 'RL-Powered Execution',
    desc: 'Backed by the PPO execution model that continuously optimises order placement under the current regime.',
  },
  {
    icon: TrendingUp,
    color: '#26a69a',
    title: 'Backtest Interpreter',
    desc: 'Explains Sharpe, Calmar, max drawdown, and win-rate in the context of your strategy\'s goals.',
  },
  {
    icon: Zap,
    color: '#2962ff',
    title: 'Instant Context',
    desc: 'No need to paste data — the copilot automatically fetches your live positions, regime, and risk state before answering.',
  },
];

/* ─── Page ────────────────────────────────────────────────────────────────── */
export default function AssistantPage() {
  const { selectedStrategyId } = useCopilotStore();
  const pageRef   = useRef<HTMLDivElement>(null);
  const headerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!pageRef.current) return;
    const ctx = gsap.context(() => {
      gsap.fromTo(
        headerRef.current,
        { opacity: 0, y: -16 },
        { opacity: 1, y: 0, duration: 0.4, ease: 'power3.out' },
      );
      gsap.fromTo(
        '.cap-tile',
        { opacity: 0, y: 18, scale: 0.97 },
        { opacity: 1, y: 0, scale: 1, duration: 0.35, ease: 'power3.out', stagger: 0.07, delay: 0.15 },
      );
      gsap.fromTo(
        '.chat-panel',
        { opacity: 0, x: 20 },
        { opacity: 1, x: 0, duration: 0.45, ease: 'power3.out', delay: 0.1 },
      );
    }, pageRef);
    return () => ctx.revert();
  }, []);

  return (
    <div ref={pageRef} className="flex flex-col gap-4 h-full">

      {/* ── Header ── */}
      <div ref={headerRef} className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <p className="panel-caption mb-1">Context-Aware Intelligence</p>
          <h1 className="text-[17px] font-semibold tracking-tight" style={{ color: 'var(--tv-text-primary)' }}>
            AI Trading Copilot
          </h1>
        </div>
        <div className="flex items-center gap-2">
          <Badge tone="success" dot>Live Context</Badge>
          {selectedStrategyId && (
            <Badge tone="blue">
              <Zap size={10} className="mr-1" />
              Strategy Loaded
            </Badge>
          )}
        </div>
      </div>

      {/* ── Main layout: left = capabilities / right = chat ── */}
      <div className="flex flex-col xl:flex-row gap-4 flex-1 min-h-0">

        {/* ── Left: capability tiles ── */}
        <div className="xl:w-72 flex-shrink-0 space-y-2">
          <p
            className="text-[10px] uppercase tracking-[0.14em] px-1"
            style={{ color: 'var(--tv-text-muted)' }}
          >
            Capabilities
          </p>
          {CAPABILITIES.map((c) => (
            <div
              key={c.title}
              className="cap-tile tv-panel px-3 py-3 flex items-start gap-3"
            >
              <div
                className="flex h-7 w-7 flex-shrink-0 items-center justify-center rounded-lg"
                style={{
                  background: `${c.color}20`,
                  border: `1px solid ${c.color}40`,
                }}
              >
                <c.icon size={14} style={{ color: c.color }} />
              </div>
              <div className="min-w-0">
                <p
                  className="text-[12px] font-semibold mb-0.5"
                  style={{ color: 'var(--tv-text-primary)' }}
                >
                  {c.title}
                </p>
                <p className="text-[11px] leading-relaxed" style={{ color: 'var(--tv-text-muted)' }}>
                  {c.desc}
                </p>
              </div>
            </div>
          ))}

          {/* Tips */}
          <div
            className="cap-tile rounded-lg px-3 py-3 mt-2"
            style={{ background: 'rgba(41,98,255,0.06)', border: '1px solid rgba(41,98,255,0.15)' }}
          >
            <p className="text-[11px] font-semibold mb-1.5" style={{ color: '#2962ff' }}>
              💡 Tips
            </p>
            <ul className="space-y-1.5 text-[11px]" style={{ color: 'var(--tv-text-muted)' }}>
              <li>• Select a strategy in the Library first — copilot will become strategy-aware.</li>
              <li>• Ask "why did my algo pause?" for real-time algo status.</li>
              <li>• Ask "explain my current regime" for the HMM model output.</li>
              <li>• Use Shift+Enter for multi-line questions.</li>
            </ul>
          </div>
        </div>

        {/* ── Right: full-height chat ── */}
        <div className="chat-panel flex-1 min-h-0" style={{ minHeight: 500 }}>
          <TradingCopilot
            page="assistant"
            strategyId={selectedStrategyId}
            includePositions
          />
        </div>
      </div>
    </div>
  );
}
