'use client';

import { useMemo } from 'react';

export function EquityCurveChart({ values }: { values: number[] }) {
  const path = useMemo(() => {
    if (values.length === 0) {
      return '';
    }
    const min = Math.min(...values);
    const max = Math.max(...values);
    return values
      .map((value, index) => {
        const x = (index / (values.length - 1 || 1)) * 100;
        const y = 100 - ((value - min) / (max - min || 1)) * 100;
        return `${x},${y}`;
      })
      .join(' ');
  }, [values]);

  return (
    <svg viewBox="0 0 100 100" className="h-52 w-full rounded-xl bg-slate-100/80 p-2 dark:bg-slate-800/70">
      <polyline fill="none" stroke="#3b82f6" strokeWidth="2" points={path} />
    </svg>
  );
}
