'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';

import { cn } from '@/lib/utils';

const nav = [
  { href: '/dashboard', label: 'Dashboard' },
  { href: '/dashboard/live-trading', label: 'Live Trading' },
  { href: '/dashboard/paper-trading', label: 'Paper Trading' },
  { href: '/dashboard/backtesting', label: 'Backtesting' },
  { href: '/dashboard/strategies', label: 'Strategies' },
  { href: '/dashboard/risk', label: 'Risk' },
  { href: '/dashboard/quantum', label: 'Quantum' },
  { href: '/dashboard/analytics', label: 'Analytics' }
] as const;

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="hidden w-64 shrink-0 border-r border-slate-300/40 bg-white/70 p-4 backdrop-blur lg:block dark:border-slate-700/60 dark:bg-slate-950/70">
      <h2 className="font-heading text-xl">Sniper</h2>
      <nav className="mt-6 flex flex-col gap-2">
        {nav.map((item) => {
          const active = pathname === item.href || pathname?.startsWith(`${item.href}/`);
          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                'rounded-lg px-3 py-2 text-sm transition',
                active ? 'bg-brand text-white' : 'text-slate-700 hover:bg-slate-200 dark:text-slate-300 dark:hover:bg-slate-800'
              )}
            >
              {item.label}
            </Link>
          );
        })}
      </nav>
    </aside>
  );
}
