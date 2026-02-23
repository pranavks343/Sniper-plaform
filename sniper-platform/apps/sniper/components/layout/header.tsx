'use client';

import {
  Bell,
  ChevronDown,
  LogOut,
  Moon,
  PanelLeftClose,
  PanelLeftOpen,
  Search,
  Settings,
  Sun,
  User,
} from 'lucide-react';
import { useEffect, useRef, useState } from 'react';
import { useClerk, useUser } from '@clerk/nextjs';
import Link from 'next/link';
import gsap from 'gsap';

import { useUiStore } from '@/store/ui-store';
import { useLiveIndices } from '@/hooks/use-live-indices';

function TickerCell({
  symbol,
  price,
  change,
  pct,
  loading,
}: {
  symbol: string;
  price: number;
  change: number;
  pct: number;
  loading?: boolean;
}) {
  const bull = change >= 0;
  const showSkeleton = loading && price === 0;
  return (
    <div className="ticker-item">
      <span className="ticker-symbol">{symbol}</span>
      {showSkeleton ? (
        <>
          <span className="ticker-price" style={{ color: 'var(--tv-text-muted)' }}>—</span>
          <span className="ticker-change" style={{ color: 'var(--tv-text-muted)' }}>loading…</span>
        </>
      ) : (
        <>
          <span className={`ticker-price ${bull ? 'bull-glow' : 'bear-glow'}`}>
            {price.toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
          </span>
          <span className={`ticker-change ${bull ? 'bull-glow' : 'bear-glow'}`}>
            {bull ? '+' : ''}{change.toFixed(2)} ({bull ? '+' : ''}{pct.toFixed(2)}%)
          </span>
        </>
      )}
    </div>
  );
}

/* ─── Profile dropdown ───────────────────────────────────────────────────── */
function ProfileDropdown() {
  const { user } = useUser();
  const { signOut } = useClerk();
  const { darkMode, toggleDarkMode, initTheme } = useUiStore();
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  // Init theme from localStorage on first render
  useEffect(() => {
    initTheme();
  }, [initTheme]);

  // Close on outside click
  useEffect(() => {
    function handleClick(e: MouseEvent) {
      if (ref.current && !ref.current.contains(e.target as Node)) {
        setOpen(false);
      }
    }
    document.addEventListener('mousedown', handleClick);
    return () => document.removeEventListener('mousedown', handleClick);
  }, []);

  const initials = user
    ? (user.firstName?.[0] ?? '') + (user.lastName?.[0] ?? '')
    : 'T';
  const displayName = user?.fullName ?? user?.username ?? 'Trader';
  const email = user?.primaryEmailAddress?.emailAddress ?? '';

  return (
    <div ref={ref} className="relative">
      {/* Trigger */}
      <button
        type="button"
        onClick={() => setOpen((o) => !o)}
        className="flex items-center gap-1.5 rounded px-2 py-1 text-[12px] font-medium transition"
        style={{
          background: open ? 'var(--tv-bg-overlay)' : 'var(--tv-bg-elevated)',
          border: `1px solid ${open ? 'var(--tv-border-light)' : 'var(--tv-border-light)'}`,
          color: 'var(--tv-text-primary)',
        }}
        aria-label="Profile menu"
      >
        <span
          className="flex h-6 w-6 items-center justify-center rounded-full text-[11px] font-bold flex-shrink-0"
          style={{ background: 'var(--tv-blue)', color: '#fff' }}
        >
          {initials || 'T'}
        </span>
        <span className="hidden xl:inline max-w-[80px] truncate">{displayName}</span>
        <ChevronDown
          size={11}
          style={{
            color: 'var(--tv-text-muted)',
            transform: open ? 'rotate(180deg)' : 'rotate(0deg)',
            transition: 'transform 0.15s ease',
          }}
        />
      </button>

      {/* Dropdown panel */}
      {open && (
        <div
          className="absolute right-0 top-full mt-1.5 w-56 rounded-md overflow-hidden z-50 animate-fadein"
          style={{
            background: 'var(--tv-bg-surface)',
            border: '1px solid var(--tv-border-light)',
            boxShadow: '0 8px 32px rgba(0,0,0,0.35)',
          }}
        >
          {/* User info */}
          <div
            className="px-4 py-3 border-b"
            style={{ borderColor: 'var(--tv-border)' }}
          >
            <div className="flex items-center gap-3">
              <span
                className="flex h-9 w-9 items-center justify-center rounded-full text-[14px] font-bold flex-shrink-0"
                style={{ background: 'var(--tv-blue)', color: '#fff' }}
              >
                {initials || 'T'}
              </span>
              <div className="min-w-0">
                <p
                  className="text-[13px] font-semibold truncate"
                  style={{ color: 'var(--tv-text-primary)' }}
                >
                  {displayName}
                </p>
                {email && (
                  <p
                    className="text-[11px] truncate"
                    style={{ color: 'var(--tv-text-muted)' }}
                  >
                    {email}
                  </p>
                )}
              </div>
            </div>
          </div>

          {/* Menu items */}
          <div className="py-1">
            <Link
              href="/dashboard/profile"
              onClick={() => setOpen(false)}
              className="flex items-center gap-2.5 px-4 py-2.5 text-[13px] transition w-full"
              style={{ color: 'var(--tv-text-primary)' }}
              onMouseEnter={(e) => (e.currentTarget.style.background = 'var(--tv-bg-elevated)')}
              onMouseLeave={(e) => (e.currentTarget.style.background = 'transparent')}
            >
              <User size={14} style={{ color: 'var(--tv-text-secondary)' }} />
              View Profile
            </Link>

            <Link
              href="/dashboard/settings"
              onClick={() => setOpen(false)}
              className="flex items-center gap-2.5 px-4 py-2.5 text-[13px] transition w-full"
              style={{ color: 'var(--tv-text-primary)' }}
              onMouseEnter={(e) => (e.currentTarget.style.background = 'var(--tv-bg-elevated)')}
              onMouseLeave={(e) => (e.currentTarget.style.background = 'transparent')}
            >
              <Settings size={14} style={{ color: 'var(--tv-text-secondary)' }} />
              Settings
            </Link>

            {/* Theme toggle */}
            <button
              type="button"
              onClick={() => { toggleDarkMode(); }}
              className="flex items-center justify-between gap-2.5 px-4 py-2.5 text-[13px] transition w-full text-left"
              style={{ color: 'var(--tv-text-primary)' }}
              onMouseEnter={(e) => (e.currentTarget.style.background = 'var(--tv-bg-elevated)')}
              onMouseLeave={(e) => (e.currentTarget.style.background = 'transparent')}
            >
              <span className="flex items-center gap-2.5">
                {darkMode
                  ? <Sun size={14} style={{ color: 'var(--tv-text-secondary)' }} />
                  : <Moon size={14} style={{ color: 'var(--tv-text-secondary)' }} />
                }
                {darkMode ? 'Light Mode' : 'Dark Mode'}
              </span>
              {/* Toggle pill */}
              <span
                className="relative inline-flex h-4.5 w-8 items-center rounded-full flex-shrink-0"
                style={{
                  width: 30,
                  height: 18,
                  background: darkMode ? 'var(--tv-blue)' : 'var(--tv-bg-overlay)',
                  border: '1px solid var(--tv-border-light)',
                  display: 'flex',
                  alignItems: 'center',
                  padding: '0 2px',
                  transition: 'background 0.2s',
                }}
              >
                <span
                  style={{
                    width: 12,
                    height: 12,
                    borderRadius: '50%',
                    background: '#fff',
                    transform: darkMode ? 'translateX(12px)' : 'translateX(0)',
                    transition: 'transform 0.2s',
                    flexShrink: 0,
                  }}
                />
              </span>
            </button>
          </div>

          {/* Divider + Sign out */}
          <div
            className="border-t py-1"
            style={{ borderColor: 'var(--tv-border)' }}
          >
            <button
              type="button"
              onClick={() => signOut({ redirectUrl: '/' })}
              className="flex items-center gap-2.5 px-4 py-2.5 text-[13px] transition w-full text-left"
              style={{ color: '#ef5350' }}
              onMouseEnter={(e) => (e.currentTarget.style.background = 'rgba(239,83,80,0.08)')}
              onMouseLeave={(e) => (e.currentTarget.style.background = 'transparent')}
            >
              <LogOut size={14} />
              Sign Out
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

/* ─── Header ─────────────────────────────────────────────────────────────── */
export function Header() {
  const [clock, setClock] = useState('');
  const [sessionOpen, setSessionOpen] = useState(false);
  const { darkMode, sidebarOpen, toggleDarkMode, toggleSidebar } = useUiStore();
  const { tickers: liveTickers, loading: tickersLoading } = useLiveIndices();
  const headerRef = useRef<HTMLElement>(null);

  // Clock + NSE session status (IST: 9:15–15:30, Mon–Fri)
  useEffect(() => {
    const refresh = () => {
      const now = new Date();
      setClock(
        new Intl.DateTimeFormat('en-IN', {
          hour: '2-digit',
          minute: '2-digit',
          second: '2-digit',
          timeZone: 'Asia/Kolkata',
          hour12: false,
        }).format(now)
      );
      const ist = new Intl.DateTimeFormat('en-IN', {
        timeZone: 'Asia/Kolkata',
        hour: 'numeric',
        minute: 'numeric',
        weekday: 'short',
        hour12: false,
      }).formatToParts(now);
      const hour = parseInt(ist.find((p) => p.type === 'hour')?.value ?? '0', 10);
      const minute = parseInt(ist.find((p) => p.type === 'minute')?.value ?? '0', 10);
      const weekday = ist.find((p) => p.type === 'weekday')?.value ?? '';
      const isWeekday = !['Sat', 'Sun'].includes(weekday);
      const minutesSinceMidnight = hour * 60 + minute;
      const openAt = 9 * 60 + 15;
      const closeAt = 15 * 60 + 30;
      setSessionOpen(isWeekday && minutesSinceMidnight >= openAt && minutesSinceMidnight < closeAt);
    };
    refresh();
    const t = window.setInterval(refresh, 1000);
    return () => window.clearInterval(t);
  }, []);

  // GSAP ticker entrance
  useEffect(() => {
    if (!headerRef.current) return;
    const ctx = gsap.context(() => {
      gsap.fromTo(
        '.ticker-item',
        { opacity: 0, y: -8 },
        { opacity: 1, y: 0, duration: 0.4, stagger: 0.08, ease: 'power2.out', delay: 0.2 }
      );
      gsap.fromTo(
        '.header-control',
        { opacity: 0, x: 12 },
        { opacity: 1, x: 0, duration: 0.4, stagger: 0.05, ease: 'power2.out', delay: 0.4 }
      );
    }, headerRef);
    return () => ctx.revert();
  }, []);

  return (
    <header ref={headerRef} className="tv-topbar">
      {/* Left: brand + market status + tickers */}
      <div className="flex flex-1 items-stretch overflow-x-auto">
        <div
          className="flex items-center gap-2 border-r px-4"
          style={{ borderColor: 'var(--tv-border)', minWidth: 'max-content' }}
        >
          <span className="text-sm font-bold tracking-tight" style={{ color: 'var(--tv-text-primary)' }}>
            SNIPER
          </span>
          <span
            className="rounded px-1.5 py-0.5 text-[10px] font-semibold"
            style={{ background: 'var(--tv-blue-light)', color: 'var(--tv-blue)', border: '1px solid rgba(41,98,255,0.3)' }}
          >
            PRO
          </span>
        </div>

        <div
          className="flex items-center gap-2 border-r px-3"
          style={{ borderColor: 'var(--tv-border)', minWidth: 'max-content' }}
        >
          <span
            className="session-pill"
            style={sessionOpen ? undefined : { opacity: 0.85 }}
            title={sessionOpen ? 'NSE market open (9:15–15:30 IST)' : 'NSE market closed'}
          >
            <span
              className="live-dot"
              style={{ background: sessionOpen ? '#26a69a' : 'var(--tv-text-muted)' }}
            />
            {sessionOpen ? 'NSE Open' : 'Closed'}
          </span>
        </div>

        <div className="flex items-stretch overflow-x-auto">
          {liveTickers.map((t) => (
            <TickerCell key={t.symbol} {...t} loading={tickersLoading} />
          ))}
        </div>
      </div>

      {/* Right controls */}
      <div
        className="flex items-center gap-1 border-l px-3"
        style={{ borderColor: 'var(--tv-border)' }}
      >
        {/* Clock */}
        <div
          className="header-control flex items-center gap-1.5 rounded px-2 py-1 text-[12px] font-mono"
          style={{
            color: 'var(--tv-text-secondary)',
            background: 'var(--tv-bg-elevated)',
            border: '1px solid var(--tv-border-light)',
          }}
        >
          <span style={{ color: 'var(--tv-text-muted)', fontSize: 10 }}>IST</span>
          <span style={{ color: 'var(--tv-text-primary)', fontWeight: 600 }}>{clock || '--:--:--'}</span>
        </div>

        {/* Latency chip */}
        <div
          className="header-control hidden xl:flex items-center gap-1.5 rounded px-2 py-1 text-[11px] font-medium"
          style={{ color: 'var(--tv-text-muted)', background: 'var(--tv-bg-elevated)', border: '1px solid var(--tv-border)' }}
        >
          <span className="h-1.5 w-1.5 rounded-full" style={{ background: 'var(--tv-bull)' }} />
          21ms
        </div>

        {/* Quick theme toggle (sun/moon icon) — separate from dropdown */}
        <button
          type="button"
          aria-label={sidebarOpen ? 'Collapse sidebar' : 'Expand sidebar'}
          onClick={toggleSidebar}
          className="header-control tv-btn tv-btn-icon hidden lg:inline-flex"
          title={sidebarOpen ? 'Collapse Sidebar' : 'Expand Sidebar'}
        >
          {sidebarOpen ? <PanelLeftClose size={14} /> : <PanelLeftOpen size={14} />}
        </button>

        <button
          type="button"
          aria-label="Toggle theme"
          onClick={toggleDarkMode}
          className="header-control tv-btn tv-btn-icon"
          title={darkMode ? 'Switch to Light Mode' : 'Switch to Dark Mode'}
        >
          {darkMode
            ? <Sun size={14} />
            : <Moon size={14} />
          }
        </button>

        {/* Search */}
        <button type="button" aria-label="Search" className="header-control tv-btn tv-btn-icon">
          <Search size={14} />
        </button>

        {/* Notifications */}
        <button type="button" aria-label="Notifications" className="header-control tv-btn tv-btn-icon">
          <Bell size={14} />
        </button>

        {/* Profile dropdown */}
        <div className="header-control">
          <ProfileDropdown />
        </div>
      </div>
    </header>
  );
}
