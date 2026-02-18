'use client';

import { cn } from './utils';

export function Switch({
  checked,
  onCheckedChange,
  onChange,
  disabled,
  className,
}: {
  checked: boolean;
  onCheckedChange?: (checked: boolean) => void;
  onChange?: () => void;
  disabled?: boolean;
  className?: string;
}) {
  const handleClick = () => {
    if (disabled) return;
    const next = !checked;
    onCheckedChange?.(next);
    onChange?.();
  };
  return (
    <button
      type="button"
      role="switch"
      aria-checked={checked}
      disabled={disabled}
      className={cn(
        'relative inline-flex h-6 w-11 flex-shrink-0 rounded-full border transition-colors',
        checked ? 'border-[#26a69a] bg-[#26a69a]' : 'border-[var(--tv-border)] bg-[var(--tv-bg-elevated)]',
        className
      )}
      onClick={handleClick}
    >
      <span
        className={cn(
          'pointer-events-none inline-block h-5 w-5 rounded-full bg-white shadow transition-transform',
          checked ? 'translate-x-5' : 'translate-x-0.5'
        )}
        style={{ marginTop: 2 }}
      />
    </button>
  );
}
