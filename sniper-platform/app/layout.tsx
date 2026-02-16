import type { Metadata } from 'next';

import './globals.css';

export const metadata: Metadata = {
  title: 'Sniper Trading System',
  description: 'Quantum-enhanced algorithmic trading platform'
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="font-body antialiased">{children}</body>
    </html>
  );
}
