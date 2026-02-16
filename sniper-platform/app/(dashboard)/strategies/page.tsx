'use client';

import Link from 'next/link';

import { StrategyCards } from '@/components/strategy/strategy-cards';
import { Button } from '@/components/ui/button';
import { useStrategies } from '@/hooks/use-strategies';

export default function StrategiesPage() {
  const { strategies } = useStrategies();

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="font-heading text-3xl">Strategies</h1>
        <Link href="/dashboard/strategies/new">
          <Button>New Strategy</Button>
        </Link>
      </div>
      <StrategyCards strategies={strategies} />
    </div>
  );
}
