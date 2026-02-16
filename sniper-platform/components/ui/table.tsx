import type { ReactNode } from 'react';

export function Table({ children }: { children: ReactNode }) {
  return <table className="w-full text-left text-sm">{children}</table>;
}
