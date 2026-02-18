/** Merge class names; falsy values are omitted */
export function cn(...args: (string | undefined | false | null)[]): string {
  return args.filter(Boolean).join(' ');
}

/** Format number as Indian Rupee (e.g. ₹1,23,456.78) */
export function formatINR(value: number): string {
  if (!Number.isFinite(value)) return '—';
  const abs = Math.abs(value);
  const [int, dec] = abs.toFixed(2).split('.');
  const withCommas = int.replace(/\B(?=(\d{3})+(?!\d))/g, ',');
  const sign = value < 0 ? '−' : '';
  return `${sign}₹${withCommas}.${dec}`;
}
