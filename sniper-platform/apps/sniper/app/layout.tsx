import type { Metadata } from 'next';

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

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <head>
        <script dangerouslySetInnerHTML={{ __html: themeScript }} />
      </head>
      <body
        className="antialiased"
        style={{ background: 'var(--tv-bg-base)', color: 'var(--tv-text-primary)' }}
        suppressHydrationWarning
      >
        {children}
      </body>
    </html>
  );
}
