import { auth } from '@clerk/nextjs/server';

import { TradingViewPreload } from '@/components/charts/tradingview-preload';
import { Header } from '@/components/layout/header';
import { Sidebar } from '@/components/layout/sidebar';
import { MarketNewsProvider } from '@/components/providers/market-news-provider';

export default async function DashboardLayout({ children }: { children: React.ReactNode }) {
  await auth.protect();

  return (
    <MarketNewsProvider>
      <div className="flex min-h-screen" style={{ background: 'var(--tv-bg-base)' }}>
        <TradingViewPreload />
        <Sidebar />
        <div className="flex min-w-0 flex-1 flex-col">
          <Header />
          <main
            className="flex-1 overflow-auto p-4 md:p-5"
            style={{ background: 'var(--tv-bg-base)' }}
          >
            {children}
          </main>
        </div>
      </div>
    </MarketNewsProvider>
  );
}
