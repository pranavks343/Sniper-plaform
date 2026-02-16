import Link from 'next/link';

import type { Strategy } from '@/types/strategy';

import { Badge } from '../ui/badge';
import { Button } from '../ui/button';

export function StrategyCards({ strategies }: { strategies: Strategy[] }) {
  return (
    <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
      {strategies.map((strategy) => (
        <div key={strategy.id} className="card-shell">
          <div className="flex items-start justify-between">
            <div>
              <h3 className="font-heading text-lg">{strategy.name}</h3>
              <p className="text-xs text-slate-500">{strategy.type}</p>
            </div>
            <Badge tone={strategy.status === 'active' ? 'success' : 'default'}>{strategy.status}</Badge>
          </div>
          <div className="mt-4 flex gap-2">
            <Link href={`/dashboard/strategies/${strategy.id}`}>
              <Button className="bg-slate-800">Edit</Button>
            </Link>
            <Link href={`/dashboard/strategies/${strategy.id}/builder`}>
              <Button>Builder</Button>
            </Link>
          </div>
        </div>
      ))}
    </div>
  );
}
