'use client';

import type { SelectHTMLAttributes, ReactNode } from 'react';
import { cn } from './utils';

export function Select({
  children,
  className,
  ...props
}: SelectHTMLAttributes<HTMLSelectElement> & { children?: ReactNode }) {
  return (
    <select
      className={cn(
        'w-full rounded border px-3 py-2 text-sm',
        'border-[var(--tv-border)] bg-[var(--tv-bg-elevated)]',
        'focus:outline-none focus:ring-2 focus:ring-[var(--tv-blue)]',
        className
      )}
      {...props}
    >
      {children}
    </select>
  );
}
