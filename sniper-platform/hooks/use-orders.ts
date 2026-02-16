'use client';

import { useEffect, useMemo, useState } from 'react';

import { apiClient } from '@/lib/api-client';
import type { Order } from '@/types/trading';

export function useOrders() {
  const [orders, setOrders] = useState<Order[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    apiClient.execution
      .listOrders()
      .then(setOrders)
      .catch((err: Error) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  const placeOrder = async (payload: Record<string, unknown>) => {
    const order = await apiClient.execution.placeOrder(payload);
    setOrders((prev) => [order, ...prev]);
    return order;
  };

  const cancelOrder = async (orderId: string) => {
    setOrders((prev) => prev.map((order) => (order.id === orderId ? { ...order, status: 'CANCELLED' } : order)));
  };

  return useMemo(() => ({ orders, loading, error, placeOrder, cancelOrder }), [orders, loading, error]);
}
