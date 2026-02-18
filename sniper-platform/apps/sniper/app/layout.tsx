import type { Metadata } from 'next';
import { ClerkProvider } from '@clerk/nextjs';

import { ClerkTokenSync } from '@/components/auth/clerk-token-sync';
import './globals.css';

export const metadata: Metadata = {
  title: 'Sniper — Professional Trading Terminal',
  description: 'Quantum-enhanced algorithmic trading platform'
};

// Injected before React hydrates — reads localStorage and sets class on <html>
// to avoid flash of wrong theme.
const themeScript = `
(function(){
  try {
    var t = localStorage.getItem('sniper-theme');
    var dark = t !== null ? t === 'dark' : true;
    document.documentElement.classList.add(dark ? 'dark' : 'light');
  } catch(e){}
})();
`;

// #region agent log
console.log('[DEBUG][H1] RootLayout server render reached', {env:process.env.NODE_ENV, port:process.env.PORT});
// #endregion

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <ClerkProvider>
      {/* suppressHydrationWarning because we mutate className client-side */}
      <html lang="en" suppressHydrationWarning>
        <head>
          {/* Run synchronously before page renders to prevent theme flash */}
          <script dangerouslySetInnerHTML={{ __html: themeScript }} />
        </head>
        <body
          className="antialiased"
          style={{ background: 'var(--tv-bg-base)', color: 'var(--tv-text-primary)' }}
          suppressHydrationWarning
        >
          <ClerkTokenSync />
          {children}
        </body>
      </html>
    </ClerkProvider>
  );
}
