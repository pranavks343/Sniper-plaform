'use client';

import { cn } from './utils';

type Tone = 'success' | 'danger' | 'blue' | 'muted' | 'warning';

export function Badge({
  children,
  tone = 'muted',
  dot,
  className,
}: {
  children: React.ReactNode;
  tone?: Tone;
  dot?: boolean;
  className?: string;
}) {
  const toneClass: Record<Tone, string> = {
    success: 'bg-[rgba(38,166,154,0.12)] text-[#26a69a] border border-[rgba(38,166,154,0.3)]',
    danger: 'bg-[rgba(239,83,80,0.12)] text-[#ef5350] border border-[rgba(239,83,80,0.3)]',
    blue: 'bg-[rgba(41,98,255,0.12)] text-[#2962ff] border border-[rgba(41,98,255,0.3)]',
    warning: 'bg-[rgba(247,166,0,0.12)] text-[#f7a600] border border-[rgba(247,166,0,0.3)]',
    muted: 'bg-[var(--tv-bg-elevated)] text-[var(--tv-text-muted)] border border-[var(--tv-border)]',
  };
  return (
    <span
      className={cn(
        'inline-flex items-center gap-1.5 rounded px-2 py-0.5 text-[11px] font-medium',
        toneClass[tone],
        className
      )}
    >
      {dot ? (
        <span
          className="h-1.5 w-1.5 rounded-full flex-shrink-0"
          style={{
            background: tone === 'success' ? '#26a69a' : tone === 'danger' ? '#ef5350' : tone === 'blue' ? '#2962ff' : 'var(--tv-text-muted)',
          }}
        />
      ) : null}
      {children}
    </span>
  );
}
