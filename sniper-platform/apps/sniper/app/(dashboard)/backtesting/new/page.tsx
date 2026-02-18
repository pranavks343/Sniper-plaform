'use client';

import Link from 'next/link';
import { useState } from 'react';

import { apiClient } from '@/lib/api-client';

import { Button } from '@sniper/framework';
import { Card } from '@sniper/framework';
import { Input } from '@sniper/framework';
import { Select } from '@sniper/framework';

export default function NewBacktestPage() {
  const [strategyId, setStrategyId] = useState('strategy-1');
  const [capital, setCapital] = useState(1_000_000);
  const [jobId, setJobId] = useState<string | null>(null);

  const submit = async () => {
    const payload = {
      strategy_id: strategyId,
      start_date: new Date(Date.now() - 30 * 24 * 3600 * 1000).toISOString(),
      end_date: new Date().toISOString(),
      initial_capital: capital,
      transaction_cost_model: 'realistic'
    };
    const res = await apiClient.backtest.create(payload);
    setJobId(res.job_id);
  };

  return (
    <Card className="max-w-xl">
      <h1 className="font-heading text-3xl">New Backtest</h1>
      <div className="mt-4 space-y-3">
        <Input value={strategyId} onChange={(e) => setStrategyId(e.target.value)} placeholder="Strategy ID" />
        <Input type="number" value={capital} onChange={(e) => setCapital(Number(e.target.value))} placeholder="Initial Capital" />
        <Select defaultValue="realistic">
          <option value="realistic">Realistic Costs</option>
          <option value="zero">Zero Costs</option>
        </Select>
        <Button onClick={submit}>Run Backtest</Button>
      </div>
      {jobId ? (
        <p className="mt-4 text-sm">
          Job created: {jobId.slice(0, 10)}.{' '}
          <Link href={`/dashboard/backtesting/${jobId}`} className="text-brand underline">
            View Results
          </Link>
        </p>
      ) : null}
    </Card>
  );
}
