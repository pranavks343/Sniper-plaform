import type { ReactNode } from 'react';

import { cn } from '@/lib/utils';

export function Badge({ children, tone = 'default' }: { children: ReactNode; tone?: 'default' | 'success' | 'danger' | 'warning' }) {
  const tones = {
    default: 'bg-slate-200 text-slate-900 dark:bg-slate-700 dark:text-slate-100',
    success: 'bg-green-100 text-green-800 dark:bg-green-900/50 dark:text-green-200',
    danger: 'bg-red-100 text-red-800 dark:bg-red-900/50 dark:text-red-200',
    warning: 'bg-amber-100 text-amber-800 dark:bg-amber-900/50 dark:text-amber-200'
  };
  return <span className={cn('inline-flex rounded-full px-2.5 py-1 text-xs font-semibold', tones[tone])}>{children}</span>;
}
