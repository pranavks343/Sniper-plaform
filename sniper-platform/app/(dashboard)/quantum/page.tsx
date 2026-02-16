'use client';

import { useState } from 'react';

import { QuantumStatusCard } from '@/components/quantum/quantum-status-card';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Switch } from '@/components/ui/switch';
import { useQuantumStatus } from '@/hooks/use-quantum-status';

export default function QuantumPage() {
  const { status, usage, refresh, loading } = useQuantumStatus();
  const [routingEnabled, setRoutingEnabled] = useState(true);
  const [portfolioEnabled, setPortfolioEnabled] = useState(true);
  const [hedgingEnabled, setHedgingEnabled] = useState(true);

  return (
    <div className="space-y-6">
      <h1 className="font-heading text-3xl">Quantum Control Panel</h1>
      <QuantumStatusCard status={status} />

      <Card>
        <h2 className="font-heading text-xl">Configuration</h2>
        <div className="mt-4 grid gap-4 md:grid-cols-2">
          <div className="flex items-center justify-between">
            <span>Routing Optimization</span>
            <Switch checked={routingEnabled} onChange={() => setRoutingEnabled((v) => !v)} />
          </div>
          <div className="flex items-center justify-between">
            <span>Portfolio Optimization</span>
            <Switch checked={portfolioEnabled} onChange={() => setPortfolioEnabled((v) => !v)} />
          </div>
          <div className="flex items-center justify-between">
            <span>Hedging Optimization</span>
            <Switch checked={hedgingEnabled} onChange={() => setHedgingEnabled((v) => !v)} />
          </div>
          <Input placeholder="Timeout (ms)" defaultValue={5000} />
        </div>
      </Card>

      <div className="grid gap-4 md:grid-cols-3">
        <Card>Total Solves: {usage?.total_solves ?? 0}</Card>
        <Card>Avg Solve: {(usage?.avg_solve_time_ms ?? 0).toFixed(2)} ms</Card>
        <Card>Monthly Cost: ₹{(usage?.cost_this_month ?? 0).toFixed(2)}</Card>
      </div>

      <Button onClick={() => void refresh()} disabled={loading}>
        {loading ? 'Testing...' : 'Test Connection'}
      </Button>
    </div>
  );
}
