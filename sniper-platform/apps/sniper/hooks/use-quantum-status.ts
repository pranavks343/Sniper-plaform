'use client';

import { useCallback, useEffect, useState } from 'react';

import { apiClient } from '@/lib/api-client';
import type { QuantumConfigUpdate, QuantumConnectionInfo, QuantumStatus, QuantumUsage } from '@/types/quantum';

export function useQuantumStatus() {
  const [status, setStatus] = useState<QuantumStatus | null>(null);
  const [usage, setUsage] = useState<QuantumUsage | null>(null);
  const [connectionInfo, setConnectionInfo] = useState<QuantumConnectionInfo | null>(null);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const refresh = useCallback(async () => {
    try {
      setLoading(true);
      const [s, u] = await Promise.all([apiClient.quantum.getStatus(), apiClient.quantum.getUsage()]);
      setStatus(s);
      setUsage(u);
      setError(null);
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setLoading(false);
    }
  }, []);

  const testConnection = useCallback(async () => {
    try {
      setActionLoading(true);
      const result = await apiClient.quantum.test();
      setConnectionInfo(result);
      setError(null);
      await refresh();
      return result;
    } catch (err) {
      setError((err as Error).message);
      return null;
    } finally {
      setActionLoading(false);
    }
  }, [refresh]);

  const connect = useCallback(
    async (apiToken?: string) => {
      try {
        setActionLoading(true);
        const result = await apiClient.quantum.connect(apiToken ? { api_token: apiToken } : {});
        setConnectionInfo(result);
        setError(null);
        await refresh();
        return result;
      } catch (err) {
        setError((err as Error).message);
        return null;
      } finally {
        setActionLoading(false);
      }
    },
    [refresh]
  );

  const disconnect = useCallback(async () => {
    try {
      setActionLoading(true);
      const result = await apiClient.quantum.disconnect();
      setConnectionInfo({ connected: result.connected });
      setError(null);
      await refresh();
      return result;
    } catch (err) {
      setError((err as Error).message);
      return null;
    } finally {
      setActionLoading(false);
    }
  }, [refresh]);

  const updateConfig = useCallback(async (payload: QuantumConfigUpdate) => {
    try {
      setActionLoading(true);
      await apiClient.quantum.updateConfig(payload);
      setError(null);
      await refresh();
      return true;
    } catch (err) {
      setError((err as Error).message);
      return false;
    } finally {
      setActionLoading(false);
    }
  }, [refresh]);

  useEffect(() => {
    void refresh();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return {
    status,
    usage,
    connectionInfo,
    credits: status?.credits ?? 0,
    loading,
    actionLoading,
    error,
    refresh,
    testConnection,
    connect,
    disconnect,
    updateConfig,
  };
}
