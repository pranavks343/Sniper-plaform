'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import {
  BarChart3,
  BookOpen,
  Bot,
  BrainCircuit,
  CandlestickChart,
  FlaskConical,
  LayoutDashboard,
  PanelLeftClose,
  PanelLeftOpen,
  UserCircle,
  Zap,
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { useUiStore } from '@/store/ui-store';
import { useCopilotStore } from '@/store/copilot-store';

/* ─── Nav structure ───────────────────────────────────────────────────────── */
type NavSection = 'algo' | 'monitor' | 'account';

type NavItem = {
  href: string;
  label: string;
  icon: React.ElementType;
  section: NavSection;
};

const navItems: NavItem[] = [
  /* ── Algo Workflow ── */
  { href: '/dashboard',                label: 'Strategy Dashboard', icon: LayoutDashboard, section: 'algo'    },
  { href: '/dashboard/strategies',     label: 'Strategy Library',   icon: BrainCircuit,    section: 'algo'    },
  { href: '/dashboard/strategies/new', label: 'Strategy Builder',   icon: FlaskConical,    section: 'algo'    },
  { href: '/dashboard/backtesting',    label: 'Backtesting',        icon: BookOpen,        section: 'algo'    },
  /* ── Monitor ── */
  { href: '/dashboard/live-trading',   label: 'Live Monitor',       icon: CandlestickChart,section: 'monitor' },
  { href: '/dashboard/analytics',      label: 'Analytics',          icon: BarChart3,       section: 'monitor' },
  /* ── Account ── */
  { href: '/dashboard/profile',        label: 'Profile',            icon: UserCircle,      section: 'account' },
];

const SECTION_LABELS: Record<NavSection, string> = {
  algo:    'Algo Workflow',
  monitor: 'Monitor',
  account: 'Account',
};

function isItemActive(pathname: string | null, href: string): boolean {
  if (!pathname) return false;
  if (href === '/dashboard') return pathname === '/dashboard';
  return pathname === href || pathname.startsWith(`${href}/`);
}

/* ─── Component ───────────────────────────────────────────────────────────── */
export function Sidebar() {
  const pathname = usePathname();
  const { sidebarOpen, toggleSidebar } = useUiStore();
  const { toggleCopilot, copilotOpen } = useCopilotStore();

  const sections = (['algo', 'monitor', 'account'] as const).map((s) => ({
    id: s,
    label: SECTION_LABELS[s],
    items: navItems.filter((n) => n.section === s),
  }));

  return (
    <aside className={cn('tv-sidebar hidden lg:flex', sidebarOpen ? 'is-open' : 'is-collapsed')}>

      {/* Logo + collapse toggle */}
      <div className={cn('mb-2 flex w-full', sidebarOpen ? 'items-center gap-2 px-2' : 'flex-col items-center gap-2')}>
        <div
          className="flex h-10 w-10 items-center justify-center rounded-lg flex-shrink-0"
          style={{ background: 'var(--tv-blue)' }}
        >
          <Zap size={19} className="text-white" fill="white" />
        </div>
        {sidebarOpen && (
          <div className="min-w-0 flex-1">
            <p className="truncate text-[13px] font-semibold tracking-tight" style={{ color: 'var(--tv-text-primary)' }}>
              Sniper
            </p>
            <p className="text-[10px] uppercase tracking-[0.12em]" style={{ color: 'var(--tv-text-muted)' }}>
              Algo Platform
            </p>
          </div>
        )}
        <button
          type="button"
          onClick={toggleSidebar}
          className="tv-sidebar-item tv-sidebar-toggle"
          aria-label={sidebarOpen ? 'Collapse sidebar' : 'Expand sidebar'}
          title={sidebarOpen ? 'Collapse sidebar' : 'Expand sidebar'}
        >
          {sidebarOpen ? <PanelLeftClose size={18} /> : <PanelLeftOpen size={18} />}
          {!sidebarOpen && <span className="tv-sidebar-tooltip">Expand Sidebar</span>}
        </button>
      </div>

      <div className={cn('tv-divider my-1', sidebarOpen ? 'w-full' : 'w-8')} />

      {/* Grouped nav */}
      <nav className={cn('flex flex-1 flex-col gap-0.5 py-2 overflow-y-auto', sidebarOpen ? 'items-stretch px-2' : 'items-center')}>
        {sections.map((section, si) => (
          <div key={section.id}>
            {si > 0 && (
              <div className={cn('mt-3 mb-1')}>
                <div className="tv-divider w-full" />
                {sidebarOpen && (
                  <p className="mt-2 px-2 text-[10px] uppercase tracking-[0.16em]" style={{ color: 'var(--tv-text-muted)' }}>
                    {section.label}
                  </p>
                )}
              </div>
            )}
            {si === 0 && sidebarOpen && (
              <p className="px-2 pb-1 pt-0.5 text-[10px] uppercase tracking-[0.16em]" style={{ color: 'var(--tv-text-muted)' }}>
                {section.label}
              </p>
            )}
            {section.items.map((item) => {
              const active = isItemActive(pathname, item.href);
              const Icon   = item.icon;
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={cn('tv-sidebar-item', active && 'active')}
                  aria-label={item.label}
                >
                  <Icon size={18} strokeWidth={active ? 2.25 : 1.9} />
                  <span className="tv-sidebar-label">{item.label}</span>
                  {!sidebarOpen && <span className="tv-sidebar-tooltip">{item.label}</span>}
                </Link>
              );
            })}
          </div>
        ))}
      </nav>

      {/* AI Copilot + Algo engine status */}
      <div className={cn('mb-2 flex flex-col gap-2', sidebarOpen ? 'items-stretch px-2' : 'items-center')}>
        <div className={cn('tv-divider', sidebarOpen ? 'w-full' : 'w-8')} />
        {/* AI Copilot toggle button */}
        <button
          type="button"
          onClick={toggleCopilot}
          className={cn('tv-sidebar-item', copilotOpen && 'active')}
          aria-label="AI Trading Copilot"
          title="AI Trading Copilot"
          style={copilotOpen ? { borderColor: 'rgba(38,166,154,0.4)', background: 'rgba(38,166,154,0.12)' } : undefined}
        >
          <Bot size={18} strokeWidth={copilotOpen ? 2.25 : 1.9} style={{ color: copilotOpen ? '#26a69a' : undefined }} />
          <span className="tv-sidebar-label" style={{ color: copilotOpen ? '#26a69a' : undefined }}>AI Copilot</span>
          {!sidebarOpen && <span className="tv-sidebar-tooltip">AI Trading Copilot</span>}
        </button>
        {/* Algo engine status */}
        <div
          className="tv-sidebar-item"
          style={{ cursor: 'default', borderColor: 'rgba(38,166,154,0.25)', background: 'rgba(38,166,154,0.08)' }}
        >
          <span className="live-dot" />
          <span className="tv-sidebar-label">Algo Engine: Armed</span>
          {!sidebarOpen && <span className="tv-sidebar-tooltip">Algo Engine: Armed</span>}
        </div>
      </div>
    </aside>
  );
}
