import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';

export function CircuitBreakerStatus({ active, reason }: { active: boolean; reason?: string }) {
  return (
    <div className="card-shell">
      <div className="flex items-center justify-between">
        <h3 className="font-heading text-xl">Circuit Breaker</h3>
        <Badge tone={active ? 'danger' : 'success'}>{active ? 'Trading Halted' : 'Trading Active'}</Badge>
      </div>
      <p className="mt-2 text-sm text-slate-600 dark:text-slate-300">{reason ?? 'No active breaker. Portfolio within limits.'}</p>
      {active ? <Button className="mt-4 bg-brand">Deactivate</Button> : null}
    </div>
  );
}
