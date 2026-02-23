'use client';

import { createContext, useCallback, useContext, useEffect, useState } from 'react';
import Link from 'next/link';
import { ExternalLink, Newspaper, X } from 'lucide-react';
import { useMarketNews, type NewsItem } from '@/hooks/use-market-news';

type MarketNewsContextValue = {
  news: NewsItem[];
  loading: boolean;
  error: string | null;
  newItems: NewsItem[];
  clearNewItems: () => void;
};

const MarketNewsContext = createContext<MarketNewsContextValue | null>(null);

export function useMarketNewsContext() {
  const ctx = useContext(MarketNewsContext);
  if (!ctx) throw new Error('useMarketNewsContext must be used within MarketNewsProvider');
  return ctx;
}

const POPUP_AUTO_DISMISS_MS = 12_000;

export function MarketNewsProvider({ children }: { children: React.ReactNode }) {
  const { news, loading, error, newItems, clearNewItems } = useMarketNews();
  const [popupDismissed, setPopupDismissed] = useState(false);

  const value: MarketNewsContextValue = {
    news,
    loading,
    error,
    newItems,
    clearNewItems,
  };

  useEffect(() => {
    if (newItems.length === 0) setPopupDismissed(false);
  }, [newItems.length]);

  useEffect(() => {
    if (newItems.length === 0) return;
    const t = setTimeout(() => {
      clearNewItems();
      setPopupDismissed(true);
    }, POPUP_AUTO_DISMISS_MS);
    return () => clearTimeout(t);
  }, [newItems, clearNewItems]);

  const handleDismiss = useCallback(() => {
    clearNewItems();
    setPopupDismissed(true);
  }, [clearNewItems]);

  const showPopup = newItems.length > 0 && !popupDismissed;

  return (
    <MarketNewsContext.Provider value={value}>
      {children}
      {showPopup && (
        <div
          className="fixed bottom-4 right-4 z-[100] w-full max-w-sm rounded-lg shadow-lg overflow-hidden"
          style={{
            background: 'var(--tv-bg-surface)',
            border: '1px solid var(--tv-border)',
            boxShadow: '0 8px 32px rgba(0,0,0,0.4)',
          }}
        >
          <div
            className="flex items-center justify-between px-4 py-2.5 border-b"
            style={{ borderColor: 'var(--tv-border)', background: 'var(--tv-bg-elevated)' }}
          >
            <div className="flex items-center gap-2">
              <Newspaper size={14} style={{ color: '#2962ff' }} />
              <span className="text-[12px] font-semibold" style={{ color: 'var(--tv-text-primary)' }}>
                New market news
              </span>
              <span className="text-[10px] px-1.5 py-0.5 rounded" style={{ background: '#2962ff22', color: '#2962ff' }}>
                {newItems.length} new
              </span>
            </div>
            <button
              type="button"
              onClick={handleDismiss}
              className="p-1 rounded hover:bg-[var(--tv-bg-base)]"
              style={{ color: 'var(--tv-text-muted)' }}
              aria-label="Dismiss"
            >
              <X size={14} />
            </button>
          </div>
          <div className="max-h-48 overflow-y-auto">
            {newItems.slice(0, 5).map((item, i) => (
              <a
                key={i}
                href={item.link}
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-start gap-2 px-4 py-2.5 border-b hover:bg-[var(--tv-bg-elevated)] transition-colors"
                style={{ borderColor: 'var(--tv-border)' }}
              >
                <p className="text-[11px] font-medium leading-snug line-clamp-2 flex-1 min-w-0" style={{ color: 'var(--tv-text-primary)' }}>
                  {item.title}
                </p>
                <ExternalLink size={10} className="flex-shrink-0 mt-0.5" style={{ color: 'var(--tv-text-muted)' }} />
              </a>
            ))}
          </div>
          <div className="px-4 py-2 border-t flex justify-end" style={{ borderColor: 'var(--tv-border)' }}>
            <Link
              href="/dashboard/analytics"
              onClick={handleDismiss}
              className="text-[11px] font-semibold"
              style={{ color: '#2962ff' }}
            >
              View all in Analytics →
            </Link>
          </div>
        </div>
      )}
    </MarketNewsContext.Provider>
  );
}
