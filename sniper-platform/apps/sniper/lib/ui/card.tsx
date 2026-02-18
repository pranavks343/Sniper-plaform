'use client';

import type { ReactNode } from 'react';
import { cn } from './utils';

export function Card({
  children,
  className,
}: { children: ReactNode; className?: string }) {
  return (
    <div
      className={cn(
        'rounded-lg border p-4',
        'border-[var(--tv-border)] bg-[var(--tv-bg-surface)]',
        className
      )}
    >
      {children}
    </div>
  );
}

export function CardHeader({ children, className }: { children: ReactNode; className?: string }) {
  return <div className={cn('mb-3 text-sm font-semibold', className)}>{children}</div>;
}

export function CardBody({ children, className }: { children: ReactNode; className?: string }) {
  return <div className={cn('text-sm', className)}>{children}</div>;
}
