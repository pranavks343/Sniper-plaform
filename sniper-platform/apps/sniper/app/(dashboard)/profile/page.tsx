'use client';

import { useClerk, useUser } from '@clerk/nextjs';
import { useEffect, useRef } from 'react';
import gsap from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';
import {
  Activity,
  BarChart2,
  Calendar,
  Edit3,
  Key,
  LogOut,
  Mail,
  Moon,
  Shield,
  Sun,
  TrendingUp,
  User,
  Zap,
} from 'lucide-react';
import { Badge } from '@/lib/ui';
import { useUiStore } from '@/store/ui-store';

if (typeof window !== 'undefined') gsap.registerPlugin(ScrollTrigger);

/* ─── Stat mini-card ─────────────────────────────────────────────────────── */
function ProfileStat({
  label,
  value,
  icon: Icon,
  accent,
}: {
  label: string;
  value: string;
  icon: React.ElementType;
  accent?: string;
}) {
  return (
    <div
      className="metric-card"
      style={{ flex: '1 1 120px', minWidth: 120 }}
    >
      <div className="flex items-center gap-2 mb-1">
        <Icon size={13} style={{ color: accent ?? 'var(--tv-text-muted)' }} />
        <span className="panel-caption">{label}</span>
      </div>
      <span
        className="text-[18px] font-bold font-mono"
        style={{ color: accent ?? 'var(--tv-text-primary)', letterSpacing: '-0.02em' }}
      >
        {value}
      </span>
    </div>
  );
}

/* ─── Section card ───────────────────────────────────────────────────────── */
function Section({
  title,
  icon: Icon,
  children,
}: {
  title: string;
  icon: React.ElementType;
  children: React.ReactNode;
}) {
  return (
    <div
      className="profile-section rounded-md overflow-hidden"
      style={{ background: 'var(--tv-bg-surface)', border: '1px solid var(--tv-border)', opacity: 0 }}
    >
      <div
        className="flex items-center gap-2 px-5 py-3 border-b"
        style={{ borderColor: 'var(--tv-border)' }}
      >
        <Icon size={14} style={{ color: 'var(--tv-text-secondary)' }} />
        <span className="panel-title">{title}</span>
      </div>
      <div className="p-5">{children}</div>
    </div>
  );
}

/* ─── Info row ───────────────────────────────────────────────────────────── */
function InfoRow({ label, value }: { label: string; value: string }) {
  return (
    <div
      className="flex items-center justify-between py-3 border-b"
      style={{ borderColor: 'var(--tv-border)' }}
    >
      <span className="text-[12px]" style={{ color: 'var(--tv-text-secondary)' }}>
        {label}
      </span>
      <span
        className="text-[13px] font-medium"
        style={{ color: 'var(--tv-text-primary)' }}
      >
        {value}
      </span>
    </div>
  );
}

/* ─── Page ───────────────────────────────────────────────────────────────── */
export default function ProfilePage() {
  const { user } = useUser();
  const { signOut } = useClerk();
  const { darkMode, toggleDarkMode } = useUiStore();
  const pageRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!pageRef.current) return;
    const ctx = gsap.context(() => {
      const tl = gsap.timeline({ defaults: { ease: 'power3.out' } });
      tl.fromTo('.profile-header', { opacity: 0, y: -14 }, { opacity: 1, y: 0, duration: 0.45 })
        .fromTo('.profile-hero',   { opacity: 0, y: 20, scale: 0.98 }, { opacity: 1, y: 0, scale: 1, duration: 0.5 }, '-=0.2')
        .fromTo('.profile-stat',   { opacity: 0, y: 16 }, { opacity: 1, y: 0, duration: 0.4, stagger: 0.07 }, '-=0.15')
        .fromTo('.profile-section',{ opacity: 0, y: 24 }, { opacity: 1, y: 0, duration: 0.45, stagger: 0.09 }, '-=0.1');
    }, pageRef);
    return () => ctx.revert();
  }, []);

  const displayName = user?.fullName ?? user?.username ?? 'Trader';
  const initials    = user
    ? (user.firstName?.[0] ?? '') + (user.lastName?.[0] ?? '')
    : 'T';
  const email       = user?.primaryEmailAddress?.emailAddress ?? '—';
  const createdAt   = user?.createdAt
    ? new Date(user.createdAt).toLocaleDateString('en-IN', { year: 'numeric', month: 'long', day: 'numeric' })
    : '—';
  const lastActive  = user?.updatedAt
    ? new Date(user.updatedAt).toLocaleDateString('en-IN', { year: 'numeric', month: 'short', day: 'numeric' })
    : '—';

  return (
    <div ref={pageRef} className="max-w-3xl mx-auto space-y-5">

      {/* ── Page header ── */}
      <div className="profile-header flex flex-wrap items-center justify-between gap-3" style={{ opacity: 0 }}>
        <div>
          <p className="panel-caption mb-1">Account</p>
          <h1 className="text-[17px] font-semibold tracking-tight" style={{ color: 'var(--tv-text-primary)' }}>
            Profile
          </h1>
        </div>
        <Badge tone="blue" dot>Pro Account</Badge>
      </div>

      {/* ── Avatar + name hero ── */}
      <div
        className="profile-hero rounded-md p-6 flex flex-wrap items-center gap-5"
        style={{ background: 'var(--tv-bg-surface)', border: '1px solid var(--tv-border)', opacity: 0 }}
      >
        {/* Avatar */}
        <div className="relative flex-shrink-0">
          {user?.imageUrl ? (
            // eslint-disable-next-line @next/next/no-img-element
            <img
              src={user.imageUrl}
              alt={displayName}
              className="h-20 w-20 rounded-full object-cover"
              style={{ border: '3px solid var(--tv-border-light)' }}
            />
          ) : (
            <span
              className="flex h-20 w-20 items-center justify-center rounded-full text-[28px] font-bold"
              style={{ background: 'var(--tv-blue)', color: '#fff' }}
            >
              {initials || 'T'}
            </span>
          )}
          {/* Online dot */}
          <span
            className="absolute bottom-1 right-1 h-4 w-4 rounded-full"
            style={{
              background: 'var(--tv-bull)',
              border: '2px solid var(--tv-bg-surface)',
            }}
          />
        </div>

        {/* Name + meta */}
        <div className="flex-1 min-w-0">
          <h2
            className="text-[22px] font-bold tracking-tight"
            style={{ color: 'var(--tv-text-primary)', letterSpacing: '-0.02em' }}
          >
            {displayName}
          </h2>
          <p className="text-[13px] mt-0.5" style={{ color: 'var(--tv-text-secondary)' }}>
            {email}
          </p>
          <div className="flex flex-wrap gap-2 mt-3">
            <Badge tone="success" dot>Active Session</Badge>
            <Badge tone="blue">Institutional Sim</Badge>
            <Badge>NSE Access</Badge>
          </div>
        </div>

        {/* Edit button */}
        <button
          className="tv-btn tv-btn-ghost flex items-center gap-1.5 flex-shrink-0"
          onClick={() => user?.update({})}
        >
          <Edit3 size={13} />
          Edit Profile
        </button>
      </div>

      {/* ── Stats row ── */}
      <div className="flex flex-wrap gap-3">
        <div className="profile-stat" style={{ opacity: 0, flex: '1 1 120px' }}><ProfileStat label="Total Trades"  value="428"   icon={BarChart2}  accent="var(--tv-blue)" /></div>
        <div className="profile-stat" style={{ opacity: 0, flex: '1 1 120px' }}><ProfileStat label="Win Rate"      value="68.4%" icon={TrendingUp} accent="var(--tv-bull)" /></div>
        <div className="profile-stat" style={{ opacity: 0, flex: '1 1 120px' }}><ProfileStat label="Best Day P&L"  value="₹42K"  icon={Activity}   accent="var(--tv-bull)" /></div>
        <div className="profile-stat" style={{ opacity: 0, flex: '1 1 120px' }}><ProfileStat label="Strategies"    value="7"     icon={Zap}        accent="var(--tv-blue)" /></div>
      </div>

      {/* ── Account details ── */}
      <Section title="Account Details" icon={User}>
        <div className="-mt-2">
          <InfoRow label="Full Name"     value={displayName} />
          <InfoRow label="Email"         value={email} />
          <InfoRow label="Account Type"  value="Pro — Institutional Sim" />
          <InfoRow label="Member Since"  value={createdAt} />
          <InfoRow label="Last Active"   value={lastActive} />
          <div className="flex items-center justify-between pt-3">
            <span className="text-[12px]" style={{ color: 'var(--tv-text-secondary)' }}>
              User ID
            </span>
            <span
              className="text-[11px] font-mono rounded px-2 py-1"
              style={{
                background: 'var(--tv-bg-elevated)',
                color: 'var(--tv-text-muted)',
                border: '1px solid var(--tv-border)',
              }}
            >
              {user?.id?.slice(0, 24) ?? '—'}…
            </span>
          </div>
        </div>
      </Section>

      {/* ── Preferences ── */}
      <Section title="Preferences" icon={Shield}>
        {/* Theme toggle */}
        <div
          className="flex items-center justify-between py-3 border-b"
          style={{ borderColor: 'var(--tv-border)' }}
        >
          <div className="flex items-center gap-2">
            {darkMode
              ? <Moon size={14} style={{ color: 'var(--tv-text-secondary)' }} />
              : <Sun  size={14} style={{ color: 'var(--tv-text-secondary)' }} />
            }
            <span className="text-[13px]" style={{ color: 'var(--tv-text-primary)' }}>
              {darkMode ? 'Dark Mode' : 'Light Mode'}
            </span>
          </div>
          <button
            type="button"
            onClick={toggleDarkMode}
            aria-label="Toggle theme"
            style={{
              width: 42,
              height: 24,
              borderRadius: 12,
              background: darkMode ? 'var(--tv-blue)' : 'var(--tv-bg-overlay)',
              border: '1px solid var(--tv-border-light)',
              display: 'flex',
              alignItems: 'center',
              padding: '0 3px',
              cursor: 'pointer',
              transition: 'background 0.2s',
            }}
          >
            <span
              style={{
                width: 16,
                height: 16,
                borderRadius: '50%',
                background: '#fff',
                transform: darkMode ? 'translateX(18px)' : 'translateX(0)',
                transition: 'transform 0.2s',
                flexShrink: 0,
                boxShadow: '0 1px 4px rgba(0,0,0,0.3)',
              }}
            />
          </button>
        </div>

        {/* Notification preference rows */}
        {[
          { label: 'Order notifications',   defaultOn: true },
          { label: 'Risk alert emails',      defaultOn: true },
          { label: 'Strategy reports',       defaultOn: false },
        ].map(({ label, defaultOn }) => (
          <div
            key={label}
            className="flex items-center justify-between py-3 border-b last:border-0"
            style={{ borderColor: 'var(--tv-border)' }}
          >
            <span className="text-[13px]" style={{ color: 'var(--tv-text-primary)' }}>
              {label}
            </span>
            <Badge tone={defaultOn ? 'success' : 'muted'}>{defaultOn ? 'On' : 'Off'}</Badge>
          </div>
        ))}
      </Section>

      {/* ── Security ── */}
      <Section title="Security" icon={Key}>
        <div className="-mt-2">
          <InfoRow label="Password"      value="••••••••••••" />
          <InfoRow label="2FA"           value="Enabled via Authenticator" />
          <InfoRow label="Active Sessions" value="1 (this device)" />
          <div className="pt-3">
            <button className="tv-btn tv-btn-ghost text-[12px]">
              Manage Sessions
            </button>
          </div>
        </div>
      </Section>

      {/* ── Danger zone ── */}
      <div
        className="profile-section rounded-md p-5 flex flex-wrap items-center justify-between gap-4"
        style={{
          background: 'rgba(239,83,80,0.05)',
          border: '1px solid rgba(239,83,80,0.25)',
          opacity: 0,
        }}
      >
        <div>
          <p className="text-[13px] font-semibold" style={{ color: '#ef5350' }}>
            Sign Out
          </p>
          <p className="text-[12px] mt-0.5" style={{ color: 'var(--tv-text-muted)' }}>
            End your current session on all devices.
          </p>
        </div>
        <button
          type="button"
          onClick={() => signOut({ redirectUrl: '/' })}
          className="tv-btn flex items-center gap-2"
          style={{
            background: 'rgba(239,83,80,0.12)',
            border: '1px solid rgba(239,83,80,0.4)',
            color: '#ef5350',
          }}
        >
          <LogOut size={14} />
          Sign Out
        </button>
      </div>

    </div>
  );
}
