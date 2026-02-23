'use client';

import { useState } from 'react';
import { ChevronDown, ChevronRight, ExternalLink, Newspaper } from 'lucide-react';
import { useMarketNewsContext } from '@/components/providers/market-news-provider';
import { cn } from '@/lib/ui';

export function SidebarMarketNews({ sidebarOpen }: { sidebarOpen: boolean }) {
  const { news, loading } = useMarketNewsContext();
  const [expanded, setExpanded] = useState(false);

  if (!sidebarOpen) {
    return (
      <button
        type="button"
        className="tv-sidebar-item w-full"
        onClick={() => setExpanded((e) => !e)}
        aria-label="Market News"
        title="Market News"
      >
        <Newspaper size={18} style={{ color: '#f7a600' }} />
        <span className="tv-sidebar-tooltip">Market News</span>
      </button>
    );
  }

  return (
    <div className="flex flex-col gap-0">
      <button
        type="button"
        onClick={() => setExpanded((e) => !e)}
        className="tv-sidebar-item w-full justify-between"
        aria-expanded={expanded}
      >
        <div className="flex items-center gap-2 min-w-0">
          <Newspaper size={18} style={{ color: '#f7a600' }} />
          <span className="tv-sidebar-label truncate">Market News</span>
        </div>
        {expanded ? <ChevronDown size={14} style={{ color: 'var(--tv-text-muted)' }} /> : <ChevronRight size={14} style={{ color: 'var(--tv-text-muted)' }} />}
      </button>
      {expanded && (
        <div
          className={cn('overflow-hidden border-l-2 ml-2 pl-2 mt-0.5')}
          style={{ borderColor: 'var(--tv-border)', maxHeight: 320 }}
        >
          <div className="overflow-y-auto py-1 space-y-0" style={{ maxHeight: 300 }}>
            {loading ? (
              <p className="px-2 py-4 text-[11px]" style={{ color: 'var(--tv-text-muted)' }}>Loading…</p>
            ) : news.length === 0 ? (
              <p className="px-2 py-4 text-[11px]" style={{ color: 'var(--tv-text-muted)' }}>No headlines yet</p>
            ) : (
              news.slice(0, 15).map((item, i) => (
                <a
                  key={i}
                  href={item.link}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-start gap-1.5 py-2 px-2 rounded hover:bg-[var(--tv-bg-elevated)] transition-colors group"
                >
                  <p className="text-[11px] leading-snug line-clamp-2 flex-1 min-w-0" style={{ color: 'var(--tv-text-primary)' }}>
                    {item.title}
                  </p>
                  <ExternalLink size={10} className="flex-shrink-0 mt-0.5 opacity-0 group-hover:opacity-100" style={{ color: 'var(--tv-text-muted)' }} />
                </a>
              ))
            )}
          </div>
          {!loading && news.length > 0 && (
            <p className="px-2 pt-1 pb-2 text-[9px] uppercase tracking-wider" style={{ color: 'var(--tv-text-muted)' }}>
              Indian Market · NSE · BSE · RBI
            </p>
          )}
        </div>
      )}
    </div>
  );
}
