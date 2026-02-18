'use client';

import { useEffect, useRef, useState } from 'react';
import {
  Bot,
  BrainCircuit,
  ChevronDown,
  Loader2,
  Send,
  User,
  X,
  Zap,
} from 'lucide-react';
import { apiClient } from '@/lib/api-client';
import { Badge } from '@/components/ui/badge';

/* ─── Types ───────────────────────────────────────────────────────────────── */
type Role = 'user' | 'assistant';

interface Message {
  id: string;
  role: Role;
  text: string;
  ts: number;
}

export interface TradingCopilotProps {
  /** Which dashboard page we're on — forwarded to the backend for context */
  page?: string | null;
  /** Strategy currently in focus — forwarded for strategy-aware replies */
  strategyId?: string | null;
  /** Optional callback to close the panel */
  onClose?: () => void;
  /** Whether to show a close (×) button */
  showClose?: boolean;
  /** Include open positions in context */
  includePositions?: boolean;
}

/* ─── Suggested prompts by page ───────────────────────────────────────────── */
const PAGE_SUGGESTIONS: Record<string, string[]> = {
  dashboard:           ['How are my active strategies performing?', 'Which strategy is at most risk?', 'What does the current regime mean for my algos?'],
  strategies:          ['Is my selected strategy suited for the current regime?', 'Why might this strategy be paused?', 'How do I improve my win rate?'],
  'strategies-builder':['What conditions should I add for a trending regime?', 'How should I set stop loss for high-volatility?', 'Suggest position sizing rules.'],
  'live-trading':      ['Why did my algo pause?', 'Are my risk limits close to being breached?', 'How is the current regime affecting execution?'],
  backtesting:         ['What does a Sharpe of 2.1 mean?', 'How do I interpret max drawdown vs Calmar?', 'Is this backtest overfit?'],
  risk:                ['What does my current delta exposure mean?', 'How close am I to the circuit breaker?', 'How do I reduce vega exposure?'],
  analytics:           ['How do I improve my monthly win rate?', 'What patterns do you see in my trading?'],
  assistant:           ['Why did my algo pause?', 'Is the current regime good for options selling?', 'How should I adjust for VOLATILE regime?'],
};

const DEFAULT_SUGGESTIONS = [
  'Why did my algo pause?',
  'Is the current regime good for my strategy?',
  'Explain my current risk exposure.',
];

/* ─── Single message bubble ───────────────────────────────────────────────── */
function MessageBubble({ msg }: { msg: Message }) {
  const isUser = msg.role === 'user';
  return (
    <div className={`flex gap-2.5 ${isUser ? 'flex-row-reverse' : 'flex-row'}`}>
      <div
        className="flex h-7 w-7 flex-shrink-0 items-center justify-center rounded-full"
        style={{
          background: isUser ? 'rgba(41,98,255,0.15)' : 'rgba(38,166,154,0.15)',
          border: `1px solid ${isUser ? 'rgba(41,98,255,0.3)' : 'rgba(38,166,154,0.3)'}`,
        }}
      >
        {isUser
          ? <User size={13} style={{ color: '#2962ff' }} />
          : <Bot size={13} style={{ color: '#26a69a' }} />
        }
      </div>
      <div
        className={`max-w-[82%] rounded-xl px-3 py-2 text-[12px] leading-relaxed whitespace-pre-wrap ${isUser ? 'rounded-tr-sm' : 'rounded-tl-sm'}`}
        style={{
          background: isUser ? 'rgba(41,98,255,0.1)' : 'var(--tv-bg-elevated)',
          border: `1px solid ${isUser ? 'rgba(41,98,255,0.2)' : 'var(--tv-border)'}`,
          color: 'var(--tv-text-primary)',
        }}
      >
        {msg.text}
      </div>
    </div>
  );
}

/* ─── Main component ──────────────────────────────────────────────────────── */
export function TradingCopilot({
  page,
  strategyId,
  onClose,
  showClose = false,
  includePositions = false,
}: TradingCopilotProps) {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: 'welcome',
      role: 'assistant',
      text: `I'm your AI Trading Copilot. I have access to your current market regime, risk metrics, and${strategyId ? ' selected strategy.' : ' portfolio data.'}\n\nAsk me anything — why an algo paused, whether your strategy suits the current regime, or how to interpret risk metrics.`,
      ts: Date.now(),
    },
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showSuggestions, setShowSuggestions] = useState(true);
  const bottomRef = useRef<HTMLDivElement>(null);
  const inputRef  = useRef<HTMLTextAreaElement>(null);

  const suggestions = page ? (PAGE_SUGGESTIONS[page] ?? DEFAULT_SUGGESTIONS) : DEFAULT_SUGGESTIONS;

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  // Update welcome message when strategy changes
  useEffect(() => {
    setMessages([{
      id: 'welcome',
      role: 'assistant',
      text: `I'm your AI Trading Copilot. I have access to your current market regime, risk metrics, and${strategyId ? ' selected strategy.' : ' portfolio data.'}\n\nAsk me anything — why an algo paused, whether your strategy suits the current regime, or how to interpret risk metrics.`,
      ts: Date.now(),
    }]);
    setShowSuggestions(true);
  }, [strategyId, page]);

  const send = async (text: string) => {
    const trimmed = text.trim();
    if (!trimmed || loading) return;

    setShowSuggestions(false);
    setError(null);
    setInput('');

    const userMsg: Message = { id: `u-${Date.now()}`, role: 'user', text: trimmed, ts: Date.now() };
    setMessages((prev) => [...prev, userMsg]);
    setLoading(true);

    try {
      const { reply } = await apiClient.ai.chat({
        message: trimmed,
        context: {
          strategy_id:      strategyId ?? null,
          page:             page ?? null,
          include_regime:   true,
          include_risk:     true,
          include_positions: includePositions,
          include_backtest:  !!strategyId,
        },
      });
      const botMsg: Message = { id: `a-${Date.now()}`, role: 'assistant', text: reply, ts: Date.now() };
      setMessages((prev) => [...prev, botMsg]);
    } catch (err) {
      const msg = err instanceof Error ? err.message : 'Request failed';
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      void send(input);
    }
  };

  return (
    <div
      className="flex flex-col overflow-hidden"
      style={{
        background: 'var(--tv-bg-surface)',
        border: '1px solid var(--tv-border)',
        borderRadius: 12,
        height: '100%',
      }}
    >
      {/* Header */}
      <div
        className="flex items-center gap-2.5 px-4 py-3 border-b flex-shrink-0"
        style={{ borderColor: 'var(--tv-border)', background: 'var(--tv-bg-elevated)' }}
      >
        <div
          className="flex h-7 w-7 items-center justify-center rounded-lg flex-shrink-0"
          style={{ background: 'rgba(38,166,154,0.15)', border: '1px solid rgba(38,166,154,0.3)' }}
        >
          <BrainCircuit size={14} style={{ color: '#26a69a' }} />
        </div>
        <div className="flex-1 min-w-0">
          <p className="text-[13px] font-semibold" style={{ color: 'var(--tv-text-primary)' }}>
            AI Trading Copilot
          </p>
          <p className="text-[10px]" style={{ color: 'var(--tv-text-muted)' }}>
            Strategy-aware · Regime-aware · Risk-aware
          </p>
        </div>
        <div className="flex items-center gap-1.5 flex-shrink-0">
          {strategyId && (
            <Badge tone="blue" className="text-[9px] py-0">
              <Zap size={9} className="mr-0.5" /> Strategy
            </Badge>
          )}
          <Badge tone="success" dot className="text-[9px] py-0">Live</Badge>
          {showClose && onClose && (
            <button
              onClick={onClose}
              className="ml-1 tv-btn tv-btn-icon"
              style={{ width: 24, height: 24 }}
              aria-label="Close copilot"
            >
              <X size={13} />
            </button>
          )}
        </div>
      </div>

      {/* Context info bar */}
      {(page || strategyId) && (
        <div
          className="flex items-center gap-3 px-4 py-1.5 border-b text-[10px] flex-shrink-0"
          style={{ borderColor: 'var(--tv-border)', color: 'var(--tv-text-muted)', background: 'var(--tv-bg-base)' }}
        >
          {page && <span>Page: <span style={{ color: 'var(--tv-text-secondary)' }}>{page}</span></span>}
          {strategyId && (
            <span>Strategy: <span style={{ color: '#26a69a' }}>{strategyId.slice(0, 8)}…</span></span>
          )}
        </div>
      )}

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-4 py-3 space-y-3">
        {messages.map((msg) => <MessageBubble key={msg.id} msg={msg} />)}

        {/* Loading indicator */}
        {loading && (
          <div className="flex gap-2.5">
            <div
              className="flex h-7 w-7 flex-shrink-0 items-center justify-center rounded-full"
              style={{ background: 'rgba(38,166,154,0.15)', border: '1px solid rgba(38,166,154,0.3)' }}
            >
              <Bot size={13} style={{ color: '#26a69a' }} />
            </div>
            <div
              className="flex items-center gap-1.5 rounded-xl px-3 py-2"
              style={{ background: 'var(--tv-bg-elevated)', border: '1px solid var(--tv-border)' }}
            >
              <Loader2 size={12} className="animate-spin" style={{ color: '#26a69a' }} />
              <span className="text-[11px]" style={{ color: 'var(--tv-text-muted)' }}>Analyzing context…</span>
            </div>
          </div>
        )}

        {/* Error */}
        {error && (
          <div
            className="rounded-lg px-3 py-2 text-[11px]"
            style={{ background: 'rgba(239,83,80,0.1)', border: '1px solid rgba(239,83,80,0.2)', color: '#ef5350' }}
          >
            {error}
          </div>
        )}

        <div ref={bottomRef} />
      </div>

      {/* Suggested prompts */}
      {showSuggestions && (
        <div className="px-4 pb-2 flex-shrink-0">
          <p className="panel-caption mb-1.5">Suggested questions</p>
          <div className="flex flex-col gap-1">
            {suggestions.map((s) => (
              <button
                key={s}
                onClick={() => void send(s)}
                className="text-left rounded-md px-2.5 py-1.5 text-[11px] transition-colors hover:bg-[var(--tv-bg-elevated)]"
                style={{ border: '1px solid var(--tv-border)', color: 'var(--tv-text-secondary)' }}
              >
                {s}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Input */}
      <div
        className="flex items-end gap-2 px-3 py-3 border-t flex-shrink-0"
        style={{ borderColor: 'var(--tv-border)' }}
      >
        <textarea
          ref={inputRef}
          rows={1}
          className="flex-1 resize-none rounded-lg px-3 py-2 text-[12px] outline-none"
          style={{
            background: 'var(--tv-bg-base)',
            border: '1px solid var(--tv-border)',
            color: 'var(--tv-text-primary)',
            minHeight: 36,
            maxHeight: 120,
          }}
          placeholder="Ask anything about your strategies, regime, or risk…"
          value={input}
          onChange={(e) => {
            setInput(e.target.value);
            // Auto-resize
            e.target.style.height = 'auto';
            e.target.style.height = `${e.target.scrollHeight}px`;
          }}
          onKeyDown={handleKeyDown}
          disabled={loading}
        />
        <button
          onClick={() => void send(input)}
          disabled={!input.trim() || loading}
          className="flex h-9 w-9 flex-shrink-0 items-center justify-center rounded-lg transition-all disabled:opacity-40"
          style={{ background: '#26a69a', color: 'white' }}
          aria-label="Send"
        >
          {loading ? <Loader2 size={14} className="animate-spin" /> : <Send size={14} />}
        </button>
      </div>
    </div>
  );
}
