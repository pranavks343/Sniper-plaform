'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { ArrowRight, BrainCircuit, FlaskConical } from 'lucide-react';

/**
 * Paper trading has been removed.
 * Strategy validation now happens via the Backtesting engine (historical simulation).
 * This page redirects users to the Backtesting page.
 */
export default function PaperTradingRedirectPage() {
  const router = useRouter();

  useEffect(() => {
    const t = setTimeout(() => router.replace('/dashboard/backtesting'), 3000);
    return () => clearTimeout(t);
  }, [router]);

  return (
    <div className="flex flex-col items-center justify-center min-h-[60vh] gap-6 text-center">
      <div
        className="flex h-16 w-16 items-center justify-center rounded-2xl"
        style={{ background: 'rgba(41,98,255,0.1)', border: '1px solid rgba(41,98,255,0.2)' }}
      >
        <BrainCircuit size={28} style={{ color: '#2962ff' }} />
      </div>
      <div>
        <h1 className="text-[20px] font-bold tracking-tight mb-2" style={{ color: 'var(--tv-text-primary)' }}>
          Manual Trading Removed
        </h1>
        <p className="text-[14px] max-w-md" style={{ color: 'var(--tv-text-secondary)' }}>
          Sniper is a fully algorithmic platform. Paper trading (manual simulation) has been replaced by the{' '}
          <strong>Backtesting Engine</strong> — validate strategies on historical data before going live.
        </p>
      </div>
      <div className="flex items-center gap-3">
        <Link href="/dashboard/backtesting">
          <button className="tv-btn tv-btn-primary flex items-center gap-2">
            <FlaskConical size={14} /> Go to Backtesting
            <ArrowRight size={13} />
          </button>
        </Link>
        <Link href="/dashboard/strategies">
          <button className="tv-btn tv-btn-ghost flex items-center gap-2">
            <BrainCircuit size={14} /> Strategy Library
          </button>
        </Link>
      </div>
      <p className="text-[11px]" style={{ color: 'var(--tv-text-muted)' }}>
        Redirecting to Backtesting in 3 seconds…
      </p>
    </div>
  );
}
