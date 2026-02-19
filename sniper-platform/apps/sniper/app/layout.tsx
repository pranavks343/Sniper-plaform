import type { Metadata } from 'next';
import { ClerkProvider } from '@clerk/nextjs';

import { ClerkTokenSync } from '@/components/auth/clerk-token-sync';
import './globals.css';

export const metadata: Metadata = {
  title: 'Sniper — Professional Trading Terminal',
  description: 'Quantum-enhanced algorithmic trading platform'
};

const themeScript = `
(function(){
  try {
    var t = localStorage.getItem('sniper-theme');
    var dark = t !== null ? t === 'dark' : true;
    document.documentElement.classList.add(dark ? 'dark' : 'light');
  } catch(e){}
})();
`;

const isClerkConfigured = !!process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY;

export default function RootLayout({ children }: { children: React.ReactNode }) {
  const shell = (
    <html lang="en" suppressHydrationWarning>
      <head>
        <script dangerouslySetInnerHTML={{ __html: themeScript }} />
      </head>
      <body
        className="antialiased"
        style={{ background: 'var(--tv-bg-base)', color: 'var(--tv-text-primary)' }}
        suppressHydrationWarning
      >
        {isClerkConfigured && <ClerkTokenSync />}
        {children}
      </body>
    </html>
  );

  if (isClerkConfigured) {
    return <ClerkProvider>{shell}</ClerkProvider>;
  }

  return shell;
}
