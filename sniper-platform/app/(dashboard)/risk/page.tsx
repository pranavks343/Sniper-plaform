'use client';

import { CircuitBreakerStatus } from '@/components/risk/circuit-breaker-status';
import { GreeksDashboard } from '@/components/risk/greeks-dashboard';
import { Card } from '@/components/ui/card';
import { useRiskMetrics } from '@/hooks/use-risk-metrics';

export default function RiskPage() {
  const { metrics, greeks, violations, circuitBreakerActive } = useRiskMetrics();

  return (
    <div className="space-y-6">
      <h1 className="font-heading text-3xl">Risk Dashboard</h1>
      <GreeksDashboard greeks={{ delta: greeks.delta ?? 0, gamma: greeks.gamma ?? 0, theta: greeks.theta ?? 0, vega: greeks.vega ?? 0 }} />
      <CircuitBreakerStatus active={circuitBreakerActive} reason={metrics?.trading_allowed ? undefined : 'Limit breach detected'} />
      <Card>
        <h2 className="font-heading text-xl">Violation History</h2>
        <table className="mt-3 w-full text-sm">
          <thead>
            <tr className="text-left text-slate-500">
              <th>Type</th>
              <th>Severity</th>
              <th>Value</th>
              <th>Limit</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            {violations.map((violation, index) => (
              <tr key={index} className="border-t border-slate-200/70 dark:border-slate-800">
                <td>{violation.type}</td>
                <td>{violation.severity}</td>
                <td>{violation.value}</td>
                <td>{violation.limit}</td>
                <td>{violation.action_taken}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </Card>
    </div>
  );
}
