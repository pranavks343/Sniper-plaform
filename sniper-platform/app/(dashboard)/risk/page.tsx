'use client';

import { CircuitBreakerStatus } from '@/components/risk/circuit-breaker-status';
import { GreeksDashboard } from '@/components/risk/greeks-dashboard';
import { Badge } from '@/components/ui/badge';
import { useRiskMetrics } from '@/hooks/use-risk-metrics';
import { AlertTriangle, BarChart2, Clock, ShieldCheck } from 'lucide-react';

const SEVERITY_TONE: Record<string, 'danger' | 'warning' | 'muted'> = {
  critical: 'danger',
  high:     'danger',
  medium:   'warning',
  low:      'muted',
};

export default function RiskPage() {
  const { metrics, greeks, violations, circuitBreakerActive } = useRiskMetrics();

  const tradingAllowed = metrics?.trading_allowed !== false;

  return (
    <div className="space-y-4 animate-fadein">

      {/* Page header */}
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <p className="panel-caption mb-1">Supervision Layer</p>
          <h1 className="text-[17px] font-semibold tracking-tight" style={{ color: 'var(--tv-text-primary)' }}>
            Risk Dashboard
          </h1>
        </div>
        <div className="flex items-center gap-2">
          <Badge tone={tradingAllowed ? 'success' : 'danger'} dot>
            {tradingAllowed ? 'Trading Allowed' : 'Trading Restricted'}
          </Badge>
          {circuitBreakerActive && (
            <Badge tone="danger">
              <AlertTriangle size={10} className="mr-1" />
              Circuit Breaker Active
            </Badge>
          )}
        </div>
      </div>

      {/* Circuit breaker */}
      <CircuitBreakerStatus
        active={circuitBreakerActive}
        reason={tradingAllowed ? undefined : 'Limit breach detected — trading halted automatically.'}
      />

      {/* Greeks gauges */}
      <div>
        <div className="flex items-center gap-2 mb-3">
          <BarChart2 size={14} style={{ color: 'var(--tv-text-secondary)' }} />
          <span className="panel-title">Greeks Exposure</span>
        </div>
        <GreeksDashboard
          greeks={{
            delta: greeks.delta ?? 0,
            gamma: greeks.gamma ?? 0,
            theta: greeks.theta ?? 0,
            vega:  greeks.vega  ?? 0,
          }}
        />
      </div>

      {/* Violation history */}
      <div
        className="rounded-md overflow-hidden"
        style={{ background: 'var(--tv-bg-surface)', border: '1px solid var(--tv-border)' }}
      >
        <div
          className="flex items-center justify-between px-4 py-3 border-b"
          style={{ borderColor: 'var(--tv-border)' }}
        >
          <div className="flex items-center gap-2">
            <span className="panel-title">Violation History</span>
            {violations.length > 0 && (
              <Badge tone="danger">{violations.length}</Badge>
            )}
          </div>
          <div className="flex items-center gap-1.5 text-[11px]" style={{ color: 'var(--tv-text-muted)' }}>
            <Clock size={11} />
            Live
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="tv-table">
            <thead>
              <tr>
                <th>Type</th>
                <th>Severity</th>
                <th className="text-right">Value</th>
                <th className="text-right">Limit</th>
                <th>Action Taken</th>
              </tr>
            </thead>
            <tbody>
              {violations.length ? (
                violations.map((v, i) => (
                  <tr key={i}>
                    <td>
                      <span className="font-medium" style={{ color: 'var(--tv-text-primary)' }}>
                        {v.type}
                      </span>
                    </td>
                    <td>
                      <Badge tone={SEVERITY_TONE[v.severity?.toLowerCase()] ?? 'muted'}>
                        {v.severity}
                      </Badge>
                    </td>
                    <td className="text-right font-mono" style={{ color: '#ef5350' }}>
                      {v.value}
                    </td>
                    <td className="text-right font-mono" style={{ color: 'var(--tv-text-secondary)' }}>
                      {v.limit}
                    </td>
                    <td className="text-[12px]" style={{ color: 'var(--tv-text-secondary)' }}>
                      {v.action_taken}
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={5} className="py-10 text-center">
                    <div className="flex flex-col items-center gap-2">
                      <ShieldCheck size={20} style={{ color: '#26a69a' }} />
                      <span className="text-[13px]" style={{ color: 'var(--tv-text-muted)' }}>
                        No violations — all limits within bounds
                      </span>
                    </div>
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
