import { Badge } from '@/components/ui/badge';
import type { QuantumStatus } from '@/types/quantum';

export function QuantumStatusCard({ status }: { status: QuantumStatus | null }) {
  if (!status) {
    return <div className="card-shell">Loading quantum status...</div>;
  }

  const tone = status.available ? 'success' : 'danger';
  return (
    <div className="card-shell">
      <div className="flex items-center justify-between">
        <h3 className="font-heading text-xl">Quantum Status</h3>
        <Badge tone={tone}>{status.available ? 'Online' : 'Offline'}</Badge>
      </div>
      <p className="mt-3 text-sm">Provider: {status.provider}</p>
      <p className="text-sm">Backend: {status.backend}</p>
      <p className="text-sm">Credits: {status.credits.toFixed(2)}</p>
      <p className="text-sm">Last solve: {status.last_solve ?? 'N/A'}</p>
    </div>
  );
}
