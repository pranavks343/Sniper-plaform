import { Card } from '@/components/ui/card';

function Gauge({ label, value, limit }: { label: string; value: number; limit: number }) {
  const usage = Math.min(100, Math.abs((value / limit) * 100));
  const tone = usage > 90 ? 'bg-danger' : usage > 70 ? 'bg-warning' : 'bg-success';

  return (
    <Card>
      <p className="text-sm text-slate-500">{label}</p>
      <p className="mt-2 text-2xl font-semibold">{value.toFixed(2)}</p>
      <div className="mt-3 h-2 rounded-full bg-slate-200 dark:bg-slate-700">
        <div className={`h-2 rounded-full ${tone}`} style={{ width: `${usage}%` }} />
      </div>
      <p className="mt-2 text-xs text-slate-500">{usage.toFixed(0)}% of limit</p>
    </Card>
  );
}

export function GreeksDashboard({ greeks }: { greeks: { delta: number; gamma: number; theta: number; vega: number } }) {
  return (
    <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
      <Gauge label="Delta" value={greeks.delta} limit={0.3} />
      <Gauge label="Gamma" value={greeks.gamma} limit={0.05} />
      <Gauge label="Theta" value={greeks.theta} limit={10000} />
      <Gauge label="Vega" value={greeks.vega} limit={10000} />
    </div>
  );
}
