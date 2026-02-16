'use client';

import { useState } from 'react';

import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Select } from '@/components/ui/select';
import { useStrategies } from '@/hooks/use-strategies';

export default function NewStrategyPage() {
  const { createStrategy } = useStrategies();
  const [name, setName] = useState('Momentum v1');
  const [type, setType] = useState('momentum');

  const submit = async () => {
    await createStrategy({ name, type, parameters: { ema_fast: 20, ema_slow: 50 } });
    setName('');
  };

  return (
    <Card className="max-w-xl">
      <h1 className="font-heading text-3xl">Create Strategy</h1>
      <div className="mt-4 space-y-3">
        <Input value={name} onChange={(e) => setName(e.target.value)} placeholder="Name" />
        <Select value={type} onChange={(e) => setType(e.target.value)}>
          <option value="momentum">Momentum</option>
          <option value="mean_reversion">Mean Reversion</option>
          <option value="options">Options</option>
        </Select>
        <Button onClick={submit}>Save Strategy</Button>
      </div>
    </Card>
  );
}
