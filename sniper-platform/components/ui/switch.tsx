'use client';

import type { ChangeEventHandler } from 'react';

export function Switch({ checked, onChange }: { checked: boolean; onChange?: ChangeEventHandler<HTMLInputElement> }) {
  return (
    <label className="inline-flex cursor-pointer items-center gap-2">
      <input type="checkbox" className="sr-only" checked={checked} onChange={onChange} />
      <span className={`h-6 w-11 rounded-full ${checked ? 'bg-brand' : 'bg-slate-400'} relative transition`}>
        <span className={`absolute left-0.5 top-0.5 h-5 w-5 rounded-full bg-white transition ${checked ? 'translate-x-5' : 'translate-x-0'}`} />
      </span>
    </label>
  );
}
