'use client';

import { useUiStore } from '@/store/ui-store';

import { Button } from '../ui/button';

export function Header() {
  const darkMode = useUiStore((state) => state.darkMode);
  const toggleDarkMode = useUiStore((state) => state.toggleDarkMode);

  return (
    <header className="sticky top-0 z-20 flex h-16 items-center justify-between border-b border-slate-300/40 bg-white/70 px-4 backdrop-blur dark:border-slate-700/60 dark:bg-slate-950/70">
      <div>
        <p className="text-xs uppercase tracking-[0.25em] text-slate-500">Live Monitoring</p>
        <p className="font-heading text-lg">Institutional Control Surface</p>
      </div>
      <Button className="bg-slate-800 text-white dark:bg-slate-100 dark:text-slate-900" onClick={toggleDarkMode}>
        {darkMode ? 'Light' : 'Dark'} Mode
      </Button>
    </header>
  );
}
