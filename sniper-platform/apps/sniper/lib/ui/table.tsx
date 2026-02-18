'use client';

import type { ReactNode } from 'react';
import { cn } from './utils';

export function Table({
  children,
  className,
}: { children: ReactNode; className?: string }) {
  return (
    <div className={cn('overflow-x-auto', className)}>
      <table className="w-full text-sm">{children}</table>
    </div>
  );
}
