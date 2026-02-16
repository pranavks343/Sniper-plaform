import type { SelectHTMLAttributes } from 'react';

import { cn } from '@/lib/utils';

export function Select(props: SelectHTMLAttributes<HTMLSelectElement>) {
  return <select {...props} className={cn('w-full rounded-xl border border-slate-300 bg-white/70 px-3 py-2 text-sm dark:border-slate-700 dark:bg-slate-800/80', props.className)} />;
}
