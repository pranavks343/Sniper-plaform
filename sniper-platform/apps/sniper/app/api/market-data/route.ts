import { NextResponse } from 'next/server';

const SYMBOL_MAP: Record<string, string> = {
  NIFTY: '^NSEI',
  BANKNIFTY: '^NSEBANK',
  SENSEX: '^BSESN',
  USDINR: 'INR=X',
};

interface TickerData {
  symbol: string;
  price: number;
  change: number;
  pct: number;
  prevClose: number;
}

export const revalidate = 0;
export const dynamic = 'force-dynamic';

async function fetchViaV8(yahooSymbol: string): Promise<{
  price: number;
  change: number;
  pct: number;
  prevClose: number;
} | null> {
  const url = `https://query1.finance.yahoo.com/v8/finance/chart/${encodeURIComponent(yahooSymbol)}?range=1d&interval=1d`;
  try {
    const res = await fetch(url, {
      headers: { 'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)' },
      next: { revalidate: 0 },
    });
    if (!res.ok) return null;
    const json = await res.json();
    const meta = json?.chart?.result?.[0]?.meta;
    if (!meta) return null;
    const price = meta.regularMarketPrice ?? 0;
    const prevClose = meta.chartPreviousClose ?? meta.previousClose ?? 0;
    const change = prevClose ? price - prevClose : 0;
    const pct = prevClose ? (change / prevClose) * 100 : 0;
    return { price, change, pct, prevClose };
  } catch {
    return null;
  }
}

async function fetchViaV7(): Promise<TickerData[]> {
  const yahooSymbols = Object.values(SYMBOL_MAP).join(',');
  const url = `https://query1.finance.yahoo.com/v7/finance/quote?symbols=${encodeURIComponent(yahooSymbols)}&fields=regularMarketPrice,regularMarketChange,regularMarketChangePercent,regularMarketPreviousClose`;
  const res = await fetch(url, {
    headers: { 'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)' },
    next: { revalidate: 0 },
  });
  if (!res.ok) throw new Error(`v7 responded ${res.status}`);
  const json = await res.json();
  const quotes = json?.quoteResponse?.result ?? [];
  const reverseMap: Record<string, string> = {};
  for (const [display, yahoo] of Object.entries(SYMBOL_MAP)) {
    reverseMap[yahoo] = display;
  }
  const tickers: TickerData[] = [];
  for (const q of quotes) {
    const displaySymbol = reverseMap[q.symbol];
    if (!displaySymbol) continue;
    tickers.push({
      symbol: displaySymbol,
      price: q.regularMarketPrice ?? 0,
      change: q.regularMarketChange ?? 0,
      pct: q.regularMarketChangePercent ?? 0,
      prevClose: q.regularMarketPreviousClose ?? 0,
    });
  }
  return tickers;
}

async function fetchViaV8Batch(): Promise<TickerData[]> {
  const entries = Object.entries(SYMBOL_MAP);
  const results = await Promise.all(
    entries.map(async ([displaySymbol, yahooSymbol]) => {
      const data = await fetchViaV8(yahooSymbol);
      if (!data) return null;
      return { symbol: displaySymbol, ...data } as TickerData;
    }),
  );
  return results.filter(Boolean) as TickerData[];
}

export async function GET() {
  try {
    let tickers: TickerData[] = [];

    try {
      tickers = await fetchViaV7();
    } catch {
      // v7 failed, fallback to v8 chart API
    }

    if (tickers.length === 0) {
      tickers = await fetchViaV8Batch();
    }

    const symbolOrder = Object.keys(SYMBOL_MAP);
    const ordered = symbolOrder
      .map((sym) => tickers.find((t) => t.symbol === sym))
      .filter(Boolean) as TickerData[];

    return NextResponse.json(
      { tickers: ordered, updatedAt: new Date().toISOString() },
      {
        headers: {
          'Cache-Control': 'public, s-maxage=10, stale-while-revalidate=30',
        },
      },
    );
  } catch (err) {
    const message = err instanceof Error ? err.message : 'Unknown error';
    return NextResponse.json(
      { tickers: [], error: message, updatedAt: new Date().toISOString() },
      { status: 502 },
    );
  }
}
