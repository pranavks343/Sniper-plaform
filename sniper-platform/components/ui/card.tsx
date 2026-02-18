import type { HTMLAttributes, ReactNode } from 'react';
import { cn } from '@/lib/utils';

interface CardProps extends HTMLAttributes<HTMLDivElement> {
  children: ReactNode;
  noPad?: boolean;
}

export function Card({ children, className, noPad, ...props }: CardProps) {
  return (
    <div
      className={cn('card-shell', noPad && '!p-0 overflow-hidden', className)}
      {...props}
    >
      {children}
    </div>
  );
}

export function CardHeader({ children, className, ...props }: HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      className={cn('flex items-center justify-between px-4 py-3 border-b', className)}
      style={{ borderColor: 'var(--tv-border)' }}
      {...props}
    >
      {children}
    </div>
  );
}

export function CardBody({ children, className, ...props }: HTMLAttributes<HTMLDivElement>) {
  return (
    <div className={cn('p-4', className)} {...props}>
      {children}
    </div>
  );
}
