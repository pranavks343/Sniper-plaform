type Handler = (payload: unknown) => void;

class SocketChannel {
  private ws: WebSocket | null = null;
  private handlers = new Set<Handler>();
  private reconnectTimeout: ReturnType<typeof setTimeout> | null = null;

  constructor(private readonly url: string) {}

  connect() {
    if (this.ws && (this.ws.readyState === WebSocket.OPEN || this.ws.readyState === WebSocket.CONNECTING)) {
      return;
    }

    this.ws = new WebSocket(this.url);
    this.ws.onmessage = (event) => {
      try {
        const parsed = JSON.parse(event.data as string);
        this.handlers.forEach((handler) => handler(parsed));
      } catch {
        // ignore malformed frames
      }
    };

    this.ws.onerror = () => {
      // error event always triggers onclose — reconnect handled there
    };

    this.ws.onclose = () => {
      if (this.reconnectTimeout) {
        clearTimeout(this.reconnectTimeout);
      }
      this.reconnectTimeout = setTimeout(() => this.connect(), 1500);
    };
  }

  subscribe(handler: Handler) {
    this.handlers.add(handler);
    return () => this.handlers.delete(handler);
  }

  close() {
    this.ws?.close();
    if (this.reconnectTimeout) {
      clearTimeout(this.reconnectTimeout);
      this.reconnectTimeout = null;
    }
  }
}

const wsBase = process.env.NEXT_PUBLIC_WS_BASE_URL ?? 'ws://localhost:8000';

export const websocketClient = {
  market: new SocketChannel(`${wsBase}/ws/market`),
  orders: new SocketChannel(`${wsBase}/ws/orders`),
  positions: new SocketChannel(`${wsBase}/ws/positions`),
  risk: new SocketChannel(`${wsBase}/ws/risk`)
};
