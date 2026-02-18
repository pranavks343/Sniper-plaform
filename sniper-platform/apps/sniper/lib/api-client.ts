import axios from 'axios';

import type { AuthResponse } from '@/types/auth';
import type { QuantumConfigUpdate, QuantumConnectionInfo, QuantumStatus, QuantumUsage } from '@/types/quantum';
import type { Greeks, RiskLimits, RiskMetrics, RiskViolation } from '@/types/risk';
import type { Strategy } from '@/types/strategy';
import type { Order, Position, Trade } from '@/types/trading';

const DEFAULT_API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? 'http://localhost:8000/api/v1';
const AI_CHAT_TIMEOUT_MS = 70000;
const BACKEND_HEALTH_PROBE_TIMEOUT_MS = 2500;

function getHealthUrl(baseURL: string): string {
  try {
    const parsed = new URL(baseURL);
    return `${parsed.protocol}//${parsed.host}/health`;
  } catch {
    return 'http://localhost:8000/health';
  }
}

async function isBackendHealthy(baseURL: string): Promise<boolean> {
  if (typeof fetch === 'undefined') return false;
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), BACKEND_HEALTH_PROBE_TIMEOUT_MS);
  try {
    const response = await fetch(getHealthUrl(baseURL), {
      method: 'GET',
      signal: controller.signal,
      cache: 'no-store',
    });
    return response.ok;
  } catch {
    return false;
  } finally {
    clearTimeout(timeoutId);
  }
}

const api = axios.create({
  baseURL: DEFAULT_API_BASE_URL,
  // Default timeout for non-AI endpoints; AI chat overrides with a larger timeout.
  timeout: 35000,
});

function isAuthRequest(url: string | undefined): boolean {
  if (!url) return false;
  const path = url.startsWith('http') ? new URL(url).pathname : url;
  return path.startsWith('auth/') || path === 'auth/login' || path === 'auth/register';
}

api.interceptors.request.use(async (config) => {
  if (typeof window === 'undefined') return config;
  let token = localStorage.getItem('token');
  if (!token && config.url && !isAuthRequest(config.url)) {
    await new Promise((r) => setTimeout(r, 150));
    token = localStorage.getItem('token');
  }
  // #region agent log
  fetch('http://127.0.0.1:7243/ingest/8a34fab1-5df0-4a2d-9afe-dbecd9ff02e1',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'api-client.ts:request-interceptor',message:'outgoing request token state',data:{url:config.url,hasToken:!!token,tokenLength:token?.length??0,tokenStart:token?token.slice(0,12):'NONE'},timestamp:Date.now(),hypothesisId:'H1'})}).catch(()=>{});
  // #endregion
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const isNetworkOrTimeout =
      !error?.response &&
      (error?.message === 'Network Error' || error?.code === 'ECONNABORTED' || error?.code === 'ERR_NETWORK');

    const baseURL = (api.defaults.baseURL ?? '') as string;
    const timeoutOnAI = error?.code === 'ECONNABORTED' && String(error?.config?.url ?? '').includes('/ai/chat');
    const backendHealthy = timeoutOnAI ? await isBackendHealthy(baseURL) : false;

    const status = error?.response?.status;
    const detail = error?.response?.data?.detail;
    const isAuthError =
      status === 401 ||
      status === 403 ||
      (typeof detail === 'string' && /missing authorization|unauthorized|invalid token/i.test(detail));

    if (isAuthError && typeof window !== 'undefined') {
      // #region agent log
      fetch('http://127.0.0.1:7243/ingest/8a34fab1-5df0-4a2d-9afe-dbecd9ff02e1',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'api-client.ts:response-interceptor',message:'401 redirect triggered',data:{url:error?.config?.url,status:error?.response?.status,detail:error?.response?.data?.detail,wouldRedirect:true},timestamp:Date.now(),hypothesisId:'H1'})}).catch(()=>{});
      // #endregion
      window.location.href = '/login';
      return Promise.reject(new Error('Session expired or not signed in. Redirecting to login.'));
    }

    const message = isNetworkOrTimeout
      ? (error?.code === 'ECONNABORTED'
          ? (backendHealthy
              ? 'AI response timed out before completion. Please retry, or shorten the prompt/context.'
              : 'Backend is not responding. Please ensure the backend service is running and reachable.')
          : 'Unable to reach the backend. Please check your connection and ensure the backend service is available.')
      : (error?.response?.status === 504
          ? 'AI provider timed out. Please retry in a few seconds.'
          : (error?.response?.data?.detail ?? error?.message ?? 'Request failed'));

    return Promise.reject(
      new Error(typeof message === 'string' ? message : JSON.stringify(message)),
    );
  },
);

export const apiClient = {
  auth: {
    register: async (payload: { email: string; password: string }): Promise<AuthResponse> =>
      (await api.post('/auth/register', payload)).data,
    login: async (payload: { email: string; password: string }): Promise<AuthResponse> =>
      (await api.post('/auth/login', payload)).data,
  },
  strategy: {
    getAll:     async (): Promise<Strategy[]>                        => (await api.get('/strategy/')).data,
    getById:    async (id: string): Promise<Strategy>                => (await api.get(`/strategy/${id}`)).data,
    create:     async (payload: Partial<Strategy>): Promise<Strategy> =>
      (await api.post('/strategy/', payload)).data,
    update:     async (id: string, payload: Partial<Strategy>): Promise<Strategy> =>
      (await api.put(`/strategy/${id}`, payload)).data,
    remove:     async (id: string): Promise<void>                    => { await api.delete(`/strategy/${id}`); },
    activate:   async (id: string): Promise<Strategy>                => (await api.post(`/strategy/${id}/activate`)).data,
    deactivate: async (id: string): Promise<Strategy>                => (await api.post(`/strategy/${id}/deactivate`)).data,
  },
  execution: {
    placeOrder:   async (payload: Record<string, unknown>): Promise<Order> =>
      (await api.post('/execution/order', payload)).data,
    listOrders:   async (): Promise<Order[]>    => (await api.get('/execution/orders')).data,
    getPositions: async (): Promise<Position[]> => (await api.get('/execution/positions')).data,
    getTrades:    async (): Promise<Trade[]>    => (await api.get('/execution/trades')).data,
  },
  risk: {
    getMetrics:    async (): Promise<RiskMetrics>  => (await api.get('/risk/metrics')).data,
    // /risk/greeks is pure in-memory — no DB, no Convex — always responds instantly
    getGreeks:     async (): Promise<Greeks>        => (await api.get('/risk/greeks')).data,
    getLimits:     async (): Promise<RiskLimits>    => (await api.get('/risk/limits')).data,
    getViolations: async (): Promise<RiskViolation[]> => (await api.get('/risk/violations')).data,
  },
  quantum: {
    getStatus:    async (): Promise<QuantumStatus>          => (await api.get('/quantum/status')).data,
    getUsage:     async (): Promise<QuantumUsage>           => (await api.get('/quantum/usage')).data,
    test:         async (): Promise<QuantumConnectionInfo>  => (await api.post('/quantum/test')).data,
    connect:      async (payload: { api_token?: string } = {}): Promise<QuantumConnectionInfo> =>
      (await api.post('/quantum/connect', payload)).data,
    disconnect:   async (): Promise<{ connected: boolean }> => (await api.post('/quantum/disconnect')).data,
    updateConfig: async (payload: QuantumConfigUpdate): Promise<QuantumConfigUpdate> =>
      (await api.put('/quantum/config', payload)).data,
  },
  ai: {
    chat: async (payload: {
      message: string;
      context?: {
        strategy_id?: string | null;
        page?: string | null;
        include_regime?: boolean;
        include_risk?: boolean;
        include_positions?: boolean;
        include_backtest?: boolean;
      };
    }): Promise<{ reply: string }> => (
      await api.post('/ai/chat', payload, { timeout: AI_CHAT_TIMEOUT_MS })
    ).data,
  },
  backtest: {
    create:  async (payload: Record<string, unknown>): Promise<{ job_id: string }> =>
      (await api.post('/backtest/', payload)).data,
    status:  async (jobId: string): Promise<{ status: string; progress: number }> =>
      (await api.get(`/backtest/${jobId}`)).data,
    results: async (jobId: string): Promise<Record<string, unknown>> =>
      (await api.get(`/backtest/${jobId}/results`)).data,
    list:    async (): Promise<Record<string, unknown>[]> => (await api.get('/backtest/')).data,
  },
};
