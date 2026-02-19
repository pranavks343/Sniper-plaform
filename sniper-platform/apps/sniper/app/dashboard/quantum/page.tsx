'use client';

import { useState } from 'react';

import { QuantumStatusCard } from '@/components/quantum/quantum-status-card';
import { Button, Card, Input, Switch } from '@/lib/ui';
import { useQuantumStatus } from '@/hooks/use-quantum-status';

export default function QuantumPage() {
  const {
    status,
    usage,
    connectionInfo,
    refresh,
    loading,
    actionLoading,
    error,
    connect,
    disconnect,
    testConnection,
    updateConfig,
  } = useQuantumStatus();
  const [routingEnabled, setRoutingEnabled] = useState(true);
  const [portfolioEnabled, setPortfolioEnabled] = useState(true);
  const [hedgingEnabled, setHedgingEnabled] = useState(true);
  const [timeoutMs, setTimeoutMs] = useState(5000);
  const [apiToken, setApiToken] = useState('');
  const [message, setMessage] = useState<string | null>(null);

  const onConnect = async () => {
    const result = await connect(apiToken.trim() || undefined);
    if (result?.connected) {
      setMessage('Quantum client connected.');
    } else {
      setMessage('Quantum client is still offline.');
    }
  };

  const onDisconnect = async () => {
    const result = await disconnect();
    if (result?.connected === false) {
      setMessage('Quantum client disconnected.');
    }
  };

  const onTest = async () => {
    const result = await testConnection();
    if (result) {
      setMessage(result.connected ? 'Connection test passed.' : 'Connection test completed: client is offline.');
    }
  };

  const onSaveConfig = async () => {
    const ok = await updateConfig({
      enable_quantum_routing: routingEnabled,
      enable_quantum_portfolio: portfolioEnabled,
      enable_quantum_hedging: hedgingEnabled,
      quantum_timeout_ms: timeoutMs,
    });
    setMessage(ok ? 'Quantum configuration saved.' : 'Failed to save quantum configuration.');
  };

  return (
    <div className="space-y-6">
      <h1 className="font-heading text-3xl">Quantum Control Panel</h1>
      <QuantumStatusCard status={status} />

      <Card>
        <h2 className="font-heading text-xl">Connection</h2>
        <p className="mt-2 text-sm text-muted">
          Connect using `IBM_QUANTUM_TOKEN` from backend `.env`, or paste a token below for this session.
        </p>
        <div className="mt-4 grid gap-3 md:grid-cols-[1fr_auto_auto_auto]">
          <Input
            placeholder="IBM Quantum API token (optional)"
            value={apiToken}
            onChange={(event) => setApiToken(event.target.value)}
          />
          <Button onClick={() => void onConnect()} disabled={loading || actionLoading}>
            {actionLoading ? 'Connecting...' : 'Connect'}
          </Button>
          <Button variant="ghost" onClick={() => void onTest()} disabled={loading || actionLoading}>
            Test
          </Button>
          <Button variant="danger" onClick={() => void onDisconnect()} disabled={loading || actionLoading}>
            Disconnect
          </Button>
        </div>
        <div className="mt-3 text-sm text-muted">
          Connected: <span className="text-ink">{(connectionInfo?.connected ?? status?.available) ? 'Yes' : 'No'}</span>
          {connectionInfo?.backend ? (
            <>
              {' '}· Backend: <span className="text-ink">{connectionInfo.backend}</span>
            </>
          ) : null}
        </div>
        {connectionInfo?.available_backends?.length ? (
          <div className="mt-2 text-sm text-muted">
            Available: <span className="text-ink">{connectionInfo.available_backends.join(', ')}</span>
          </div>
        ) : null}
        {message ? <p className="mt-2 text-sm text-brand">{message}</p> : null}
        {error ? <p className="mt-2 text-sm text-red-400">{error}</p> : null}
      </Card>

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
          <Input
            placeholder="Timeout (ms)"
            type="number"
            value={timeoutMs}
            onChange={(event) => setTimeoutMs(Number(event.target.value || 0))}
          />
        </div>
        <div className="mt-4">
          <Button onClick={() => void onSaveConfig()} disabled={loading || actionLoading}>
            Save Configuration
          </Button>
        </div>
      </Card>

      <div className="grid gap-4 md:grid-cols-3">
        <Card>Total Solves: {usage?.total_solves ?? 0}</Card>
        <Card>Avg Solve: {(usage?.avg_solve_time_ms ?? 0).toFixed(2)} ms</Card>
        <Card>Monthly Cost: ₹{(usage?.cost_this_month ?? 0).toFixed(2)}</Card>
      </div>

      <Button onClick={() => void refresh()} disabled={loading || actionLoading}>
        {loading ? 'Refreshing...' : 'Refresh Status'}
      </Button>
    </div>
  );
}
