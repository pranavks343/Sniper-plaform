'use client';

import Link from 'next/link';

import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';

export default function StrategyDetailPage({ params }: { params: { id: string } }) {
  return (
    <Card>
      <h1 className="font-heading text-3xl">Strategy {params.id.slice(0, 8)}</h1>
      <p className="mt-3 text-sm text-slate-600 dark:text-slate-300">Edit strategy parameters, activation state, and live performance controls.</p>
      <div className="mt-4">
        <Link href={`/dashboard/strategies/${params.id}/builder`}>
          <Button>Open Visual Builder</Button>
        </Link>
      </div>
    </Card>
  );
}
