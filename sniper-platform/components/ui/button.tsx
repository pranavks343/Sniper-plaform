import type { ButtonHTMLAttributes, ReactNode } from 'react';
import { cn } from '@/lib/utils';

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  children: ReactNode;
  variant?: 'primary' | 'ghost' | 'danger' | 'bull' | 'bear' | 'icon';
  size?: 'sm' | 'md' | 'lg';
}

export function Button({ className, children, variant = 'primary', size = 'md', ...props }: ButtonProps) {
  const base = 'tv-btn';

  const variants: Record<string, string> = {
    primary: 'tv-btn-primary',
    ghost:   'tv-btn-ghost',
    icon:    'tv-btn-icon',
    danger:  'border border-[rgba(239,83,80,0.4)] bg-[rgba(239,83,80,0.12)] text-[#ef5350] hover:bg-[rgba(239,83,80,0.22)] hover:border-[rgba(239,83,80,0.6)]',
    bull:    'border border-[rgba(38,166,154,0.4)] bg-[rgba(38,166,154,0.12)] text-[#26a69a] hover:bg-[rgba(38,166,154,0.22)]',
    bear:    'border border-[rgba(239,83,80,0.4)] bg-[rgba(239,83,80,0.12)] text-[#ef5350] hover:bg-[rgba(239,83,80,0.22)]',
  };

  const sizes: Record<string, string> = {
    sm: 'px-2.5 py-1 text-[11px]',
    md: 'px-3.5 py-[7px] text-[13px]',
    lg: 'px-5 py-2.5 text-[14px]',
  };

  return (
    <button
      className={cn(base, variants[variant], size !== 'md' && sizes[size], className)}
      {...props}
    >
      {children}
    </button>
  );
}
