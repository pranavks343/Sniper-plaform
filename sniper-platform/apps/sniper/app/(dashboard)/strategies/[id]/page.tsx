'use client';

import { useEffect } from 'react';
import Link from 'next/link';

import { Button } from '@sniper/framework';
import { Card } from '@sniper/framework';
import { useCopilotStore } from '@/store/copilot-store';

export default function StrategyDetailPage({ params }: { params: { id: string } }) {
  const { setSelectedStrategy } = useCopilotStore();

  // Set the focused strategy so the AI Copilot bubble becomes strategy-aware
  useEffect(() => {
    setSelectedStrategy(params.id);
    return () => setSelectedStrategy(null);
  }, [params.id, setSelectedStrategy]);

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
