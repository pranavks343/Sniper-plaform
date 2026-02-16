'use client';

import Link from 'next/link';
import { useEffect, useState } from 'react';

import { apiClient } from '@/lib/api-client';

import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';

export default function BacktestingListPage() {
  const [jobs, setJobs] = useState<Record<string, unknown>[]>([]);

  useEffect(() => {
    apiClient.backtest.list().then(setJobs).catch(() => setJobs([]));
  }, []);

  return (
    <Card>
      <div className="mb-4 flex items-center justify-between">
        <h1 className="font-heading text-3xl">Backtests</h1>
        <Link href="/dashboard/backtesting/new">
          <Button>New Backtest</Button>
        </Link>
      </div>
      <table className="w-full text-sm">
        <thead>
          <tr className="text-left text-slate-500">
            <th>Job ID</th>
            <th>Status</th>
            <th>Progress</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {jobs.map((job) => (
            <tr key={String(job.job_id)} className="border-t border-slate-200/70 dark:border-slate-800">
              <td>{String(job.job_id).slice(0, 10)}</td>
              <td>{String(job.status)}</td>
              <td>{Math.round((Number(job.progress) || 0) * 100)}%</td>
              <td>
                <Link href={`/dashboard/backtesting/${job.job_id}`} className="text-brand underline">
                  View Results
                </Link>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </Card>
  );
}
