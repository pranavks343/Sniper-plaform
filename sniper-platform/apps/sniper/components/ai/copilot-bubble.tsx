'use client';

import { useEffect, useRef } from 'react';
import { usePathname } from 'next/navigation';
import gsap from 'gsap';
import { BrainCircuit, X } from 'lucide-react';

import { TradingCopilot } from './trading-copilot';
import { useCopilotStore } from '@/store/copilot-store';

/** Floating bubble + slide-over panel that lives in the dashboard layout. */
export function CopilotBubble() {
  const pathname = usePathname();
  const { copilotOpen, toggleCopilot, closeCopilot, selectedStrategyId } = useCopilotStore();
  const panelRef = useRef<HTMLDivElement>(null);

  // Derive page string from pathname
  const page = (() => {
    if (!pathname) return 'dashboard';
    if (pathname === '/dashboard') return 'dashboard';
    if (pathname.includes('/strategies/new')) return 'strategies-builder';
    if (pathname.includes('/builder')) return 'strategies-builder';
    if (pathname.includes('/strategies')) return 'strategies';
    if (pathname.includes('/live-trading')) return 'live-trading';
    if (pathname.includes('/backtesting')) return 'backtesting';
    if (pathname.includes('/risk')) return 'risk';
    if (pathname.includes('/analytics')) return 'analytics';
    if (pathname.includes('/assistant')) return 'assistant';
    return 'dashboard';
  })();

  // Animate panel open/close
  useEffect(() => {
    if (!panelRef.current) return;
    if (copilotOpen) {
      gsap.fromTo(panelRef.current,
        { opacity: 0, y: 20, scale: 0.97 },
        { opacity: 1, y: 0, scale: 1, duration: 0.25, ease: 'power3.out' }
      );
    }
  }, [copilotOpen]);

  return (
    <>
      {/* Floating panel */}
      {copilotOpen && (
        <div
          ref={panelRef}
          className="fixed bottom-20 right-4 z-50 shadow-2xl"
          style={{ width: 380, height: 580 }}
        >
          <TradingCopilot
            page={page}
            strategyId={selectedStrategyId}
            onClose={closeCopilot}
            showClose
          />
        </div>
      )}

      {/* Floating action button */}
      <button
        onClick={toggleCopilot}
        aria-label={copilotOpen ? 'Close AI Copilot' : 'Open AI Copilot'}
        className="fixed bottom-4 right-4 z-50 flex h-12 w-12 items-center justify-center rounded-full shadow-xl transition-all hover:scale-110 active:scale-95"
        style={{
          background: copilotOpen ? '#ef5350' : 'linear-gradient(135deg, #26a69a, #2962ff)',
          color: 'white',
          boxShadow: '0 4px 24px rgba(38,166,154,0.4)',
        }}
      >
        {copilotOpen ? <X size={20} /> : <BrainCircuit size={20} />}
      </button>
    </>
  );
}
