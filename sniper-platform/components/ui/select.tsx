import type { SelectHTMLAttributes, ReactNode } from 'react';
import { cn } from '@/lib/utils';

interface SelectProps extends SelectHTMLAttributes<HTMLSelectElement> {
  children: ReactNode;
}

export function Select({ className, children, ...props }: SelectProps) {
  return (
    <select className={cn('tv-select', className)} {...props}>
      {children}
    </select>
  );
}
