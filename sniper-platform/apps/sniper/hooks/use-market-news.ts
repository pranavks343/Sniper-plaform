'use client';

import { useCallback, useEffect, useRef, useState } from 'react';

export interface NewsItem {
  title: string;
  link: string;
  source: string;
  pubDate: string;
  relativeTime: string;
}

const POLL_INTERVAL_MS = 120_000;

const MIN_LOADING_MS = 400;

export function useMarketNews() {
  const [news, setNews] = useState<NewsItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [newItems, setNewItems] = useState<NewsItem[]>([]);
  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const isFirstFetch = useRef(true);
  const prevLinksRef = useRef<Set<string>>(new Set());

  const fetchData = useCallback(async () => {
    if (isFirstFetch.current) setLoading(true);
    const start = Date.now();
    try {
      const res = await fetch('/api/market-news', { cache: 'no-store' });
      const json = await res.json();
      if (json.news && json.news.length > 0) {
        const incoming = json.news as NewsItem[];
        const newLinks = new Set(incoming.map((n) => n.link));
        if (!isFirstFetch.current) {
          const added = incoming.filter((n) => !prevLinksRef.current.has(n.link));
          if (added.length > 0) setNewItems(added);
        }
        prevLinksRef.current = newLinks;
        setNews(incoming);
        setError(null);
      } else if (json.error) {
        setError(json.error);
      }
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to fetch news');
    } finally {
      isFirstFetch.current = false;
      const elapsed = Date.now() - start;
      if (elapsed < MIN_LOADING_MS) {
        setTimeout(() => setLoading(false), MIN_LOADING_MS - elapsed);
      } else {
        setLoading(false);
      }
    }
  }, []);

  useEffect(() => {
    fetchData();
    timerRef.current = setInterval(fetchData, POLL_INTERVAL_MS);
    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
    };
  }, [fetchData]);

  const clearNewItems = useCallback(() => setNewItems([]), []);

  return { news, loading, error, newItems, clearNewItems };
}
