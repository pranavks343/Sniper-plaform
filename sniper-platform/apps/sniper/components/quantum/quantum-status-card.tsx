import { Badge } from '@sniper/framework';
import type { QuantumStatus } from '@/types/quantum';

export function QuantumStatusCard({ status }: { status: QuantumStatus | null }) {
  if (!status) {
    return <div className="card-shell text-muted">Loading quantum status...</div>;
  }

  const tone = status.available ? 'success' : 'danger';
  return (
    <div className="card-shell">
      <div className="flex items-center justify-between">
        <h3 className="font-heading text-xl text-ink">Quantum Status</h3>
        <Badge tone={tone}>{status.available ? 'Online' : 'Offline'}</Badge>
      </div>
      <p className="mt-3 text-sm text-muted">Provider: <span className="text-ink">{status.provider}</span></p>
      <p className="text-sm text-muted">Backend: <span className="text-ink">{status.backend}</span></p>
      <p className="text-sm text-muted">Credits: <span className="font-mono text-ink">{status.credits.toFixed(2)}</span></p>
      <p className="text-sm text-muted">Last solve: <span className="text-ink">{status.last_solve ?? 'N/A'}</span></p>
    </div>
  );
}
