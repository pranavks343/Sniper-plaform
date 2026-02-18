import type { ReactNode } from 'react';
import { cn } from '@/lib/utils';

type Tone = 'default' | 'success' | 'danger' | 'warning' | 'blue' | 'muted';

interface BadgeProps {
  children: ReactNode;
  tone?: Tone;
  className?: string;
  dot?: boolean;
}

const toneStyles: Record<Tone, string> = {
  default: 'border-[var(--tv-border-lg,#363a45)] bg-[var(--tv-bg-elevated,#2a2e39)] text-[var(--tv-text-secondary,#787b86)]',
  success: 'border-[rgba(38,166,154,0.4)] bg-[rgba(38,166,154,0.12)] text-[#26a69a]',
  danger:  'border-[rgba(239,83,80,0.4)]  bg-[rgba(239,83,80,0.12)]  text-[#ef5350]',
  warning: 'border-[rgba(247,166,0,0.4)]  bg-[rgba(247,166,0,0.10)]  text-[#f7a600]',
  blue:    'border-[rgba(41,98,255,0.3)]   bg-[rgba(41,98,255,0.12)]  text-[#2962ff]',
  muted:   'border-transparent bg-[var(--tv-bg-elevated,#2a2e39)] text-[var(--tv-text-muted,#50535e)]',
};

const dotColors: Record<Tone, string> = {
  default: 'bg-[var(--tv-text-muted,#50535e)]',
  success: 'bg-[#26a69a]',
  danger:  'bg-[#ef5350]',
  warning: 'bg-[#f7a600]',
  blue:    'bg-[#2962ff]',
  muted:   'bg-[var(--tv-text-muted,#50535e)]',
};

export function Badge({ children, tone = 'default', className, dot }: BadgeProps) {
  return (
    <span
      className={cn(
        'inline-flex items-center gap-1.5 rounded border px-2 py-0.5 text-[11px] font-semibold uppercase tracking-[0.04em] whitespace-nowrap',
        toneStyles[tone],
        className
      )}
    >
      {dot && <span className={cn('h-1.5 w-1.5 rounded-full flex-shrink-0', dotColors[tone])} />}
      {children}
    </span>
  );
}
