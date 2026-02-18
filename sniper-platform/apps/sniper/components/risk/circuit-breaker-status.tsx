import { AlertOctagon, CheckCircle2, ShieldAlert, ShieldCheck } from 'lucide-react';
import { Badge } from '@sniper/framework';

export function CircuitBreakerStatus({ active, reason }: { active: boolean; reason?: string }) {
  return (
    <div
      className="rounded-md p-4 flex items-start gap-4"
      style={{
        background: active ? 'rgba(239,83,80,0.06)' : 'rgba(38,166,154,0.06)',
        border: `1px solid ${active ? 'rgba(239,83,80,0.3)' : 'rgba(38,166,154,0.3)'}`,
      }}
    >
      {active ? (
        <ShieldAlert size={24} style={{ color: '#ef5350', flexShrink: 0 }} />
      ) : (
        <ShieldCheck size={24} style={{ color: '#26a69a', flexShrink: 0 }} />
      )}

      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2 mb-1">
          <span
            className="text-[14px] font-semibold"
            style={{ color: active ? '#ef5350' : '#26a69a' }}
          >
            Circuit Breaker
          </span>
          <Badge tone={active ? 'danger' : 'success'} dot>
            {active ? 'Trading Halted' : 'Trading Active'}
          </Badge>
        </div>
        <p className="text-[12px]" style={{ color: 'var(--tv-text-secondary)' }}>
          {reason ?? 'No active breaker. Portfolio within all risk limits.'}
        </p>
      </div>

      {active && (
        <button
          className="tv-btn tv-btn-ghost text-[12px] flex-shrink-0"
          style={{ borderColor: 'rgba(239,83,80,0.4)', color: '#ef5350' }}
        >
          Override
        </button>
      )}
    </div>
  );
}
