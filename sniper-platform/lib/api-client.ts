import axios from 'axios';

import type { QuantumStatus, QuantumUsage } from '@/types/quantum';
import type { RiskMetrics, RiskViolation } from '@/types/risk';
import type { Strategy } from '@/types/strategy';
import type { Order, Position, Trade } from '@/types/trading';

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_BASE_URL ?? 'http://localhost:8000/api/v1',
  timeout: 10000
});

api.interceptors.request.use((config) => {
  if (typeof window !== 'undefined') {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    const message = error?.response?.data?.detail ?? error.message;
    return Promise.reject(new Error(message));
  }
);

export const apiClient = {
  strategy: {
    getAll: async (): Promise<Strategy[]> => (await api.get('/strategy/')).data,
    getById: async (id: string): Promise<Strategy> => (await api.get(`/strategy/${id}`)).data,
    create: async (payload: Partial<Strategy>): Promise<Strategy> => (await api.post('/strategy/', payload)).data,
    update: async (id: string, payload: Partial<Strategy>): Promise<Strategy> => (await api.put(`/strategy/${id}`, payload)).data,
    remove: async (id: string): Promise<void> => {
      await api.delete(`/strategy/${id}`);
    },
    activate: async (id: string): Promise<Strategy> => (await api.post(`/strategy/${id}/activate`)).data,
    deactivate: async (id: string): Promise<Strategy> => (await api.post(`/strategy/${id}/deactivate`)).data
  },
  execution: {
    placeOrder: async (payload: Record<string, unknown>): Promise<Order> => (await api.post('/execution/order', payload)).data,
    listOrders: async (): Promise<Order[]> => (await api.get('/execution/orders')).data,
    getPositions: async (): Promise<Position[]> => (await api.get('/execution/positions')).data,
    getTrades: async (): Promise<Trade[]> => (await api.get('/execution/trades')).data
  },
  risk: {
    getMetrics: async (): Promise<RiskMetrics> => (await api.get('/risk/metrics')).data,
    getViolations: async (): Promise<RiskViolation[]> => (await api.get('/risk/violations')).data
  },
  quantum: {
    getStatus: async (): Promise<QuantumStatus> => (await api.get('/quantum/status')).data,
    getUsage: async (): Promise<QuantumUsage> => (await api.get('/quantum/usage')).data
  },
  backtest: {
    create: async (payload: Record<string, unknown>): Promise<{ job_id: string }> => (await api.post('/backtest/', payload)).data,
    status: async (jobId: string): Promise<{ status: string; progress: number }> => (await api.get(`/backtest/${jobId}`)).data,
    results: async (jobId: string): Promise<Record<string, unknown>> => (await api.get(`/backtest/${jobId}/results`)).data,
    list: async (): Promise<Record<string, unknown>[]> => (await api.get('/backtest/')).data
  }
};
