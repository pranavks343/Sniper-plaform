'use client';

import Link from 'next/link';
import { useEffect, useRef, useState } from 'react';
import gsap from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';
import {
  Activity,
  ArrowRight,
  BarChart2,
  Bell,
  Cpu,
  Shield,
  TrendingUp,
  Zap,
  Globe,
  Lock,
  CheckCircle2,
  Layers,
  Gauge,
} from 'lucide-react';

if (typeof window !== 'undefined') gsap.registerPlugin(ScrollTrigger);

/* ─── Animated candlestick SVG ────────────────────────────────────────────── */
function CandlestickHero() {
  const svgRef = useRef<SVGSVGElement>(null);

  useEffect(() => {
    if (!svgRef.current) return;
    const gridLines = svgRef.current.querySelectorAll('.grid-line');
    const candles  = svgRef.current.querySelectorAll('.candle-body');
    const wicks   = svgRef.current.querySelectorAll('.candle-wick');
    const line     = svgRef.current.querySelector('.price-line');
    const fill     = svgRef.current.querySelector('.price-fill');
    const fillClip = svgRef.current.querySelector('.price-fill-clip');
    const dots     = svgRef.current.querySelectorAll('.signal-dot');
    const sweep    = svgRef.current.querySelector('.chart-sweep');

    const tl = gsap.timeline({ defaults: { ease: 'power2.out' } });

    // Grid lines fade in
    tl.fromTo(gridLines, { opacity: 0 }, { opacity: 1, duration: 0.35, stagger: 0.04 })
      .fromTo(wicks,     { scaleY: 0, transformOrigin: 'center center' }, { scaleY: 1, duration: 0.45, stagger: 0.05 }, '-=0.2')
      .fromTo(candles,   { scaleY: 0, transformOrigin: 'bottom center' }, { scaleY: 1, duration: 0.35, stagger: 0.05 }, '-=0.35')
      .fromTo(line,      { strokeDashoffset: 420 }, { strokeDashoffset: 0, duration: 1, ease: 'power2.inOut' }, '-=0.25')
      .fromTo(fillClip,  { scaleX: 0, transformOrigin: 'left center' },   { scaleX: 1, duration: 0.7, ease: 'power2.inOut' }, '-=0.7')
      .fromTo(fill,      { opacity: 0 }, { opacity: 1, duration: 0.4 }, '-=0.7')
      .fromTo(dots,      { scale: 0, opacity: 0, transformOrigin: 'center center' }, { scale: 1, opacity: 1, duration: 0.3, stagger: 0.08, ease: 'back.out(1.8)' }, '-=0.3');

    // Continuous: strong up-down movement (price line + fill – volatile / “hungry”)
    const drift = gsap.to([fill, line], {
      y: 52,
      duration: 1.4,
      repeat: -1,
      yoyo: true,
      ease: 'sine.inOut',
      delay: 1.8,
    });

    // Continuous: fill opacity pulse
    const pulse = gsap.to(fill, {
      opacity: 0.72,
      duration: 2.2,
      repeat: -1,
      yoyo: true,
      ease: 'sine.inOut',
      delay: 1.5,
    });

    // Continuous: sweep line across chart (live cursor)
    let sweepTween: gsap.core.Tween | null = null;
    if (sweep) {
      gsap.set(sweep, { attr: { x1: 0, x2: 0 } });
      sweepTween = gsap.to(sweep, {
        attr: { x1: 640, x2: 640 },
        duration: 4.5,
        repeat: -1,
        repeatDelay: 2.5,
        ease: 'none',
        delay: 3,
      });
    }

    return () => {
      drift.kill();
      pulse.kill();
      sweepTween?.kill();
    };
  }, []);

  // 18 candles: [x, open%, close%, high%, low%, bull]
  const W = 640, H = 280, pad = 20;
  const cw = 24, gap = 12, total = 18;
  const startX = 24;

  const rawCandles = [
    [0, 52, 48, 55, 44, false],
    [1, 48, 53, 56, 45, true],
    [2, 53, 58, 61, 51, true],
    [3, 58, 55, 62, 52, false],
    [4, 55, 60, 64, 53, true],
    [5, 60, 57, 63, 54, false],
    [6, 57, 62, 65, 55, true],
    [7, 62, 68, 70, 60, true],
    [8, 68, 65, 71, 62, false],
    [9, 65, 70, 72, 63, true],
    [10, 70, 67, 73, 64, false],
    [11, 67, 72, 75, 65, true],
    [12, 72, 76, 78, 70, true],
    [13, 76, 73, 79, 71, false],
    [14, 73, 78, 80, 72, true],
    [15, 78, 82, 84, 76, true],
    [16, 82, 79, 85, 77, false],
    [17, 79, 84, 86, 78, true],
  ];

  const toY = (pct: number) => H - pad - (pct / 100) * (H - 2 * pad);

  const linePoints = rawCandles.map((c, i) => {
    const x = startX + i * (cw + gap) + cw / 2;
    const y = toY(((c[1] as number) + (c[2] as number)) / 2);
    return `${x},${y}`;
  }).join(' ');

  const fillPath = rawCandles.map((c, i) => {
    const x = startX + i * (cw + gap) + cw / 2;
    const y = toY(((c[1] as number) + (c[2] as number)) / 2);
    return `${x},${y}`;
  }).join(' L ');

  const lastX = startX + (rawCandles.length - 1) * (cw + gap) + cw / 2;

  return (
    <svg
      ref={svgRef}
      viewBox={`0 0 ${W} ${H}`}
      className="w-full h-full"
      style={{ maxHeight: 280 }}
      aria-hidden
    >
      <defs>
        <linearGradient id="fillGrad" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor="#2962ff" stopOpacity="0.25" />
          <stop offset="100%" stopColor="#2962ff" stopOpacity="0" />
        </linearGradient>
        <linearGradient id="lineGrad" x1="0" y1="0" x2="1" y2="0">
          <stop offset="0%" stopColor="#2962ff" stopOpacity="0.5" />
          <stop offset="100%" stopColor="#2962ff" stopOpacity="1" />
        </linearGradient>
        <filter id="glow">
          <feGaussianBlur stdDeviation="2" result="blur" />
          <feMerge><feMergeNode in="blur" /><feMergeNode in="SourceGraphic" /></feMerge>
        </filter>
        <clipPath id="fillRevealClip">
          <rect className="price-fill-clip" x={0} y={0} width={W} height={H} />
        </clipPath>
      </defs>

      {/* Horizontal grid lines */}
      {[25, 40, 55, 70, 85].map((pct) => (
        <line
          key={pct}
          className="grid-line"
          x1={0} y1={toY(pct)} x2={W} y2={toY(pct)}
          stroke="currentColor"
          strokeOpacity="0.06"
          strokeWidth="1"
        />
      ))}

      {/* Price fill (revealed left-to-right by clip) */}
      <g clipPath="url(#fillRevealClip)">
        <path
          className="price-fill"
          d={`M ${startX + cw / 2},${H - pad} L ${fillPath} L ${lastX},${H - pad} Z`}
          fill="url(#fillGrad)"
          opacity="0"
        />
      </g>

      {/* Price line */}
      <polyline
        className="price-line"
        points={linePoints}
        fill="none"
        stroke="url(#lineGrad)"
        strokeWidth="2"
        strokeDasharray="400"
        strokeDashoffset="400"
        strokeLinejoin="round"
        filter="url(#glow)"
      />

      {/* Candles */}
      {rawCandles.map((c, i) => {
        const [idx, open, close, high, low, bull] = c as [number, number, number, number, number, boolean];
        const x = startX + i * (cw + gap);
        const cx = x + cw / 2;
        const color = bull ? '#26a69a' : '#ef5350';
        const bodyTop    = toY(Math.max(open, close));
        const bodyBottom = toY(Math.min(open, close));
        const bodyH      = Math.max(bodyBottom - bodyTop, 2);

        return (
          <g key={i}>
            {/* Wick */}
            <line
              className="candle-wick"
              x1={cx} y1={toY(high)} x2={cx} y2={toY(low)}
              stroke={color} strokeWidth="1.5" opacity="0.8"
            />
            {/* Body */}
            <rect
              className="candle-body"
              x={x} y={bodyTop}
              width={cw} height={bodyH}
              rx="2"
              fill={color}
              opacity={bull ? 0.85 : 0.75}
            />
          </g>
        );
      })}

      {/* Signal dots on some candles */}
      {[4, 9, 14, 17].map((i) => {
        const c = rawCandles[i];
        const x = startX + i * (cw + gap) + cw / 2;
        const y = toY(((c[1] as number) + (c[2] as number)) / 2) - 12;
        const bull = c[5] as boolean;
        return (
          <circle
            key={i}
            className="signal-dot"
            cx={x} cy={y} r="4"
            fill={bull ? '#26a69a' : '#ef5350'}
            filter="url(#glow)"
          />
        );
      })}

      {/* Live sweep line (continuously animates across chart) */}
      <line
        className="chart-sweep"
        x1={0} y1={0} x2={0} y2={H}
        stroke="#2962ff"
        strokeWidth="1.5"
        strokeOpacity="0.35"
        strokeDasharray="4 6"
      />
    </svg>
  );
}

/* ─── Animated order-book SVG ─────────────────────────────────────────────── */
function OrderBookSVG() {
  const ref = useRef<SVGSVGElement>(null);

  useEffect(() => {
    if (!ref.current) return;
    const bidBars = ref.current.querySelectorAll('.ob-bar-bid');
    const askBars = ref.current.querySelectorAll('.ob-bar-ask');

    // Initial reveal (bids from left, asks from right)
    gsap.fromTo(bidBars, { scaleX: 0 }, { scaleX: 1, duration: 0.6, stagger: 0.04, ease: 'power2.out', delay: 0.5, transformOrigin: 'left center' });
    gsap.fromTo(askBars, { scaleX: 0 }, { scaleX: 1, duration: 0.6, stagger: 0.04, ease: 'power2.out', delay: 0.5, transformOrigin: 'right center' });

    // Continuous “depth” pulse
    const tlBid = gsap.to(bidBars, {
      scaleX: 1.08,
      duration: 2,
      repeat: -1,
      yoyo: true,
      ease: 'sine.inOut',
      stagger: { each: 0.08, from: 'start' },
      transformOrigin: 'left center',
      delay: 1.2,
    });
    const tlAsk = gsap.to(askBars, {
      scaleX: 1.08,
      duration: 2.2,
      repeat: -1,
      yoyo: true,
      ease: 'sine.inOut',
      stagger: { each: 0.08, from: 'end' },
      transformOrigin: 'right center',
      delay: 1.4,
    });

    return () => {
      tlBid.kill();
      tlAsk.kill();
    };
  }, []);

  const bids = [85, 72, 60, 48, 36, 28, 20];
  const asks = [90, 78, 64, 52, 40, 30, 22];

  return (
    <svg ref={ref} viewBox="0 0 200 160" className="w-full h-full" aria-hidden>
      {bids.map((w, i) => (
        <rect key={`b${i}`} className="ob-bar ob-bar-bid" x="0" y={i * 22 + 2} width={w} height="16" rx="2" fill="#26a69a" opacity={0.7 - i * 0.07} />
      ))}
      {asks.map((w, i) => (
        <rect key={`a${i}`} className="ob-bar ob-bar-ask" x={200 - w} y={i * 22 + 2} width={w} height="16" rx="2" fill="#ef5350" opacity={0.7 - i * 0.07} />
      ))}
    </svg>
  );
}

/* ─── Animated risk gauge SVG ─────────────────────────────────────────────── */
function RiskGaugeSVG() {
  const ref = useRef<SVGCircleElement>(null);

  useEffect(() => {
    if (!ref.current) return;
    const circ = 2 * Math.PI * 54;
    const at72 = circ * 0.28;  // 72% filled
    const at78 = circ * 0.22;  // 78% filled

    // Initial fill to 72%
    gsap.fromTo(ref.current,
      { strokeDashoffset: circ },
      { strokeDashoffset: at72, duration: 1.4, ease: 'power3.out', delay: 0.3 }
    );

    // Continuous gentle oscillation (72% ↔ 78%)
    const loop = gsap.to(ref.current, {
      strokeDashoffset: at78,
      duration: 2.5,
      repeat: -1,
      yoyo: true,
      ease: 'sine.inOut',
      delay: 2,
    });

    return () => { loop.kill(); };
  }, []);

  const circ = 2 * Math.PI * 54;

  return (
    <svg viewBox="0 0 140 140" className="w-full h-full" aria-hidden>
      <defs>
        <linearGradient id="gaugeGrad" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0%" stopColor="#26a69a" />
          <stop offset="100%" stopColor="#2962ff" />
        </linearGradient>
      </defs>
      <circle cx="70" cy="70" r="54" fill="none" stroke="currentColor" strokeOpacity="0.08" strokeWidth="12" />
      <circle
        ref={ref}
        cx="70" cy="70" r="54"
        fill="none"
        stroke="url(#gaugeGrad)"
        strokeWidth="12"
        strokeLinecap="round"
        strokeDasharray={circ}
        strokeDashoffset={circ}
        transform="rotate(-90 70 70)"
      />
      <text x="70" y="65" textAnchor="middle" fill="#d1d4dc" fontSize="22" fontWeight="700" fontFamily="Inter,sans-serif">72%</text>
      <text x="70" y="83" textAnchor="middle" fill="#787b86" fontSize="10" fontFamily="Inter,sans-serif">SAFE ZONE</text>
    </svg>
  );
}

/* ─── Feature card ────────────────────────────────────────────────────────── */
function FeatureCard({
  icon: Icon,
  title,
  body,
  visual,
  accent,
}: {
  icon: React.ElementType;
  title: string;
  body: string;
  visual: React.ReactNode;
  accent: string;
}) {
  return (
    <div
      className="feature-card rounded-xl overflow-hidden"
      style={{
        background: 'var(--tv-bg-surface)',
        border: '1px solid var(--tv-border)',
      }}
    >
      {/* Visual area */}
      <div
        className="h-44 flex items-center justify-center p-6"
        style={{
          background: 'var(--tv-bg-base)',
          borderBottom: '1px solid var(--tv-border)',
        }}
      >
        {visual}
      </div>

      {/* Content */}
      <div className="p-5">
        <div className="flex items-center gap-2 mb-2">
          <span
            className="flex h-7 w-7 items-center justify-center rounded"
            style={{ background: `${accent}18`, color: accent }}
          >
            <Icon size={14} />
          </span>
          <h3 className="text-[14px] font-semibold" style={{ color: 'var(--tv-text-primary)' }}>
            {title}
          </h3>
        </div>
        <p className="text-[12px] leading-relaxed" style={{ color: 'var(--tv-text-secondary)' }}>
          {body}
        </p>
      </div>
    </div>
  );
}

/* ─── Page ────────────────────────────────────────────────────────────────── */
export default function LandingPageClient() {
  const heroRef       = useRef<HTMLDivElement>(null);
  const featsRef      = useRef<HTMLDivElement>(null);
  const valueStripRef = useRef<HTMLDivElement>(null);
  const ctaBannerRef  = useRef<HTMLDivElement>(null);
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  // Hero entrance
  useEffect(() => {
    if (!heroRef.current || !mounted) return;
    const ctx = gsap.context(() => {
      const tl = gsap.timeline({ defaults: { ease: 'power3.out' } });
      tl.fromTo('.hero-badge',  { opacity: 0, y: -12 }, { opacity: 1, y: 0, duration: 0.5 })
        .fromTo('.hero-h1',     { opacity: 0, y: 32 },  { opacity: 1, y: 0, duration: 0.7 }, '-=0.2')
        .fromTo('.hero-sub',    { opacity: 0, y: 20 },  { opacity: 1, y: 0, duration: 0.6 }, '-=0.4')
        .fromTo('.hero-cta',    { opacity: 0, y: 16 },  { opacity: 1, y: 0, duration: 0.5 }, '-=0.3')
        .fromTo('.hero-trust',  { opacity: 0, y: 10 },  { opacity: 1, y: 0, duration: 0.45 }, '-=0.2')
        .fromTo('.hero-chart',  { opacity: 0, scale: 0.95 }, { opacity: 1, scale: 1, duration: 0.8, ease: 'back.out(1.2)' }, '-=0.5')
        .fromTo('.hero-ticker', { opacity: 0, x: 20 },  { opacity: 1, x: 0, duration: 0.5, stagger: 0.08 }, '-=0.4');
      // Floating background blobs
      gsap.to('.hero-blob', {
        y: '+=25',
        duration: 4,
        repeat: -1,
        yoyo: true,
        ease: 'sine.inOut',
        stagger: { each: 1.2, from: 'random' },
      });
    }, heroRef);
    return () => ctx.revert();
  }, [mounted]);

  // Features scroll reveal (heading + cards)
  useEffect(() => {
    if (!featsRef.current) return;
    const ctx = gsap.context(() => {
      gsap.fromTo('.feat-heading',
        { opacity: 0, y: 28 },
        { opacity: 1, y: 0, duration: 0.6, ease: 'power3.out', scrollTrigger: { trigger: featsRef.current, start: 'top 82%', once: true } }
      );
      gsap.fromTo('.feature-card',
        { opacity: 0, y: 48 },
        {
          opacity: 1, y: 0, duration: 0.7, stagger: 0.12, ease: 'power3.out',
          scrollTrigger: { trigger: '.feature-card', start: 'top 88%', once: true },
        }
      );
    }, featsRef);
    return () => ctx.revert();
  }, []);

  // CTA banner scroll reveal
  useEffect(() => {
    if (!ctaBannerRef.current) return;
    const ctx = gsap.context(() => {
      gsap.fromTo(ctaBannerRef.current,
        { opacity: 0, y: 40 },
        { opacity: 1, y: 0, duration: 0.7, ease: 'power3.out', scrollTrigger: { trigger: ctaBannerRef.current, start: 'top 88%', once: true } }
      );
    });
    return () => ctx.revert();
  }, []);

  // Value strip section fade-in
  useEffect(() => {
    if (!valueStripRef.current) return;
    const ctx = gsap.context(() => {
      gsap.fromTo(valueStripRef.current,
        { opacity: 0 },
        { opacity: 1, duration: 0.6, ease: 'power2.out', scrollTrigger: { trigger: valueStripRef.current, start: 'top 85%', once: true } }
      );
    });
    return () => ctx.revert();
  }, []);

  return (
    <main
      className="min-h-screen flex flex-col overflow-x-hidden"
      style={{ background: 'var(--tv-bg-base)', color: 'var(--tv-text-primary)' }}
    >
      {/* ── Navbar ── */}
      <header
        className="sticky top-0 z-50 flex items-center justify-between px-6 md:px-10 py-3 border-b backdrop-blur-md"
        style={{
          borderColor: 'rgba(99, 102, 241, 0.2)',
          background: 'linear-gradient(180deg, rgba(30, 33, 52, 0.97) 0%, rgba(24, 27, 42, 0.95) 100%)',
          boxShadow: '0 1px 0 0 rgba(99, 102, 241, 0.12)',
        }}
      >
        <div className="flex items-center gap-2">
          <div className="flex h-8 w-8 items-center justify-center rounded" style={{ background: 'var(--tv-blue)' }}>
            <Zap size={16} className="text-white" fill="white" />
          </div>
          <span className="text-[15px] font-bold tracking-tight text-white">SNIPER</span>
          <span className="rounded px-1.5 py-0.5 text-[10px] font-bold" style={{ background: 'var(--tv-blue-light)', color: 'var(--tv-blue)', border: '1px solid rgba(41,98,255,0.3)' }}>PRO</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="hidden sm:flex items-center gap-1.5 text-[11px]" style={{ color: 'var(--tv-bull)' }}>
            <span className="live-dot" />NSE Live
          </span>
          <Link href="/login">
            <button className="tv-btn tv-btn-ghost text-[13px] py-1.5 px-3">Sign In</button>
          </Link>
          <Link href="/register">
            <button className="tv-btn tv-btn-primary text-[13px] py-1.5 px-4 flex items-center gap-1.5">
              Get Started <ArrowRight size={13} />
            </button>
          </Link>
        </div>
      </header>

      {/* ── Hero ── */}
      <div ref={heroRef} className="relative flex flex-col items-center pt-24 pb-16 px-4 text-center overflow-hidden">

        {/* Background glow blobs (floating) */}
        <div className="pointer-events-none absolute inset-0 overflow-hidden" aria-hidden>
          <div
            className="hero-blob absolute rounded-full"
            style={{
              width: 600, height: 600,
              top: -200, left: '50%', transform: 'translateX(-50%)',
              background: 'radial-gradient(circle, rgba(41,98,255,0.14) 0%, transparent 70%)',
              filter: 'blur(40px)',
            }}
          />
          <div
            className="hero-blob absolute rounded-full"
            style={{
              width: 300, height: 300,
              top: 100, right: '15%',
              background: 'radial-gradient(circle, rgba(38,166,154,0.10) 0%, transparent 70%)',
              filter: 'blur(30px)',
            }}
          />
          <div
            className="hero-blob absolute rounded-full"
            style={{
              width: 250, height: 250,
              top: 60, left: '12%',
              background: 'radial-gradient(circle, rgba(239,83,80,0.08) 0%, transparent 70%)',
              filter: 'blur(25px)',
            }}
          />
        </div>

        {/* Badge */}
        <div
          className="hero-badge mb-5 inline-flex items-center gap-2 rounded-full px-4 py-1.5 text-[12px] font-semibold"
          style={{ background: 'var(--tv-blue-light)', color: 'var(--tv-blue)', border: '1px solid rgba(41,98,255,0.3)' }}
        >
          <Activity size={12} />
          Institutional-Grade · Sub-25ms Execution · IBM Quantum Enhanced
        </div>

        {/* H1 */}
        <h1
          className="hero-h1 font-black leading-[1.08] tracking-tight"
          style={{ fontSize: 'clamp(36px, 6vw, 68px)', color: 'var(--tv-text-primary)', maxWidth: 780, letterSpacing: '-0.03em' }}
        >
          Trade with clarity<br />
          and{' '}
          <span
            style={{
              background: 'linear-gradient(135deg, #2962ff 0%, #26a69a 100%)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              backgroundClip: 'text',
            }}
          >
            control
          </span>
        </h1>

        <p
          className="hero-sub mt-6 text-[15px] leading-relaxed"
          style={{ color: 'var(--tv-text-secondary)', maxWidth: 520 }}
        >
          Strategy engine, real-time risk management, and IBM Quantum-enhanced
          execution — all in one professional trading terminal.
        </p>

        {/* CTAs */}
        <div className="hero-cta mt-8 flex items-center gap-3">
          <Link href="/register">
            <button
              className="tv-btn tv-btn-primary px-7 py-3 text-[14px] font-semibold flex items-center gap-2"
              style={{ boxShadow: '0 4px 24px rgba(41,98,255,0.4)', borderRadius: 8 }}
            >
              Start Trading Free <ArrowRight size={15} />
            </button>
          </Link>
          <Link href="/login">
            <button className="tv-btn tv-btn-ghost px-6 py-3 text-[14px]" style={{ borderRadius: 8 }}>
              Sign In
            </button>
          </Link>
        </div>

        {/* Trust badges */}
        <div className="hero-trust mt-6 flex flex-wrap items-center justify-center gap-4 text-[11px]" style={{ color: 'var(--tv-text-muted)' }}>
          {[
            { icon: Lock,   label: 'Bank-grade security' },
            { icon: Globe,  label: 'NSE & BSE connected' },
            { icon: Shield, label: 'SEBI compliant' },
          ].map(({ icon: I, label }) => (
            <span key={label} className="flex items-center gap-1.5">
              <I size={11} />
              {label}
            </span>
          ))}
        </div>

        {/* Hero chart visual */}
        <div
          className="hero-chart mt-12 w-full max-w-3xl rounded-xl overflow-hidden relative"
          style={{
            background: 'var(--tv-bg-surface)',
            border: '1px solid var(--tv-border)',
            boxShadow: '0 24px 80px rgba(0,0,0,0.45)',
          }}
        >
          {/* Mock topbar */}
          <div
            className="flex items-center justify-between px-4 py-2.5 border-b"
            style={{ borderColor: 'var(--tv-border)' }}
          >
            <div className="flex items-center gap-3">
              <span className="text-[13px] font-bold" style={{ color: 'var(--tv-text-primary)' }}>NIFTY 50</span>
              <span className="text-[13px] font-mono font-semibold" style={{ color: 'var(--tv-bull)' }}>24,891.65</span>
              <span className="text-[11px]" style={{ color: 'var(--tv-bull)' }}>+47.20 (+0.19%)</span>
            </div>
            <div className="flex items-center gap-2">
              {['1m', '5m', '15m', '1h', 'D'].map((tf) => (
                <span
                  key={tf}
                  className="rounded px-1.5 py-0.5 text-[10px] font-semibold cursor-pointer"
                  style={{
                    background: tf === '5m' ? 'var(--tv-blue-light)' : 'transparent',
                    color: tf === '5m' ? 'var(--tv-blue)' : 'var(--tv-text-muted)',
                  }}
                >
                  {tf}
                </span>
              ))}
            </div>
          </div>

          {/* Candlestick chart */}
          <div className="px-4 py-3" style={{ background: 'var(--tv-bg-base)' }}>
            <CandlestickHero />
          </div>

          {/* Mini ticker bar */}
          <div
            className="flex overflow-x-auto border-t"
            style={{ borderColor: 'var(--tv-border)' }}
          >
            {[
              { sym: 'BANKNIFTY', price: '53,241', chg: '+0.23%', bull: true },
              { sym: 'SENSEX',    price: '81,765', chg: '-0.04%', bull: false },
              { sym: 'USDINR',    price: '83.92',  chg: '+0.10%', bull: true },
              { sym: 'CRUDEOIL',  price: '6,842',  chg: '+0.55%', bull: true },
            ].map((t) => (
              <div
                key={t.sym}
                className="hero-ticker flex flex-col px-4 py-2 border-r flex-shrink-0"
                style={{ borderColor: 'var(--tv-border)' }}
              >
                <span className="text-[10px] font-semibold" style={{ color: 'var(--tv-text-muted)' }}>{t.sym}</span>
                <span className="text-[12px] font-mono font-bold" style={{ color: 'var(--tv-text-primary)' }}>{t.price}</span>
                <span className="text-[10px] font-medium" style={{ color: t.bull ? 'var(--tv-bull)' : 'var(--tv-bear)' }}>{t.chg}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* ── Marquee strip ── */}
      <div ref={valueStripRef} className="border-y py-8 overflow-hidden" style={{ borderColor: 'var(--tv-border)' }}>
        {/* Row 1 – scrolls left */}
        <div className="marquee-row mb-4" style={{ '--marquee-dir': '-50%' } as React.CSSProperties}>
          <div className="marquee-track animate-marquee flex gap-6 w-max">
            {[
              { icon: Zap,          label: 'Sub-25ms execution',         color: 'var(--tv-blue)' },
              { icon: Shield,       label: 'Bank-grade security',         color: '#26a69a' },
              { icon: TrendingUp,   label: 'Institutional-grade signals', color: 'var(--tv-blue)' },
              { icon: CheckCircle2, label: 'SEBI compliant',              color: '#26a69a' },
              { icon: Globe,        label: 'NSE & BSE connected',         color: 'var(--tv-blue)' },
              { icon: Cpu,          label: 'Quantum-enhanced AI',         color: '#26a69a' },
              { icon: Lock,         label: 'End-to-end encrypted',        color: 'var(--tv-blue)' },
              { icon: Activity,     label: '99.9% uptime SLA',            color: '#26a69a' },
              /* duplicate for seamless loop */
              { icon: Zap,          label: 'Sub-25ms execution',         color: 'var(--tv-blue)' },
              { icon: Shield,       label: 'Bank-grade security',         color: '#26a69a' },
              { icon: TrendingUp,   label: 'Institutional-grade signals', color: 'var(--tv-blue)' },
              { icon: CheckCircle2, label: 'SEBI compliant',              color: '#26a69a' },
              { icon: Globe,        label: 'NSE & BSE connected',         color: 'var(--tv-blue)' },
              { icon: Cpu,          label: 'Quantum-enhanced AI',         color: '#26a69a' },
              { icon: Lock,         label: 'End-to-end encrypted',        color: 'var(--tv-blue)' },
              { icon: Activity,     label: '99.9% uptime SLA',            color: '#26a69a' },
            ].map(({ icon: Icon, label, color }, i) => (
              <span
                key={i}
                className="inline-flex items-center gap-2 rounded-full px-4 py-2 text-[13px] font-medium flex-shrink-0"
                style={{ color: 'var(--tv-text-secondary)', background: 'rgba(255,255,255,0.04)', border: '1px solid rgba(255,255,255,0.06)' }}
              >
                <Icon size={13} style={{ color }} />
                {label}
              </span>
            ))}
          </div>
        </div>
        {/* Row 2 – scrolls right */}
        <div className="marquee-row" style={{ '--marquee-dir': '0%' } as React.CSSProperties}>
          <div className="marquee-track animate-marquee-reverse flex gap-6 w-max">
            {[
              { icon: Gauge,        label: 'Real-time risk engine',       color: '#ef5350' },
              { icon: Layers,       label: 'Multi-strategy support',      color: 'var(--tv-blue)' },
              { icon: BarChart2,    label: 'Advanced charting suite',     color: '#26a69a' },
              { icon: TrendingUp,   label: 'Auto order slicing',          color: '#ef5350' },
              { icon: Zap,          label: 'Zerodha & Upstox APIs',       color: 'var(--tv-blue)' },
              { icon: CheckCircle2, label: 'Paper trading mode',          color: '#26a69a' },
              { icon: Shield,       label: 'Portfolio stress tests',       color: '#ef5350' },
              { icon: Activity,     label: 'Live Greeks monitoring',       color: 'var(--tv-blue)' },
              /* duplicate */
              { icon: Gauge,        label: 'Real-time risk engine',       color: '#ef5350' },
              { icon: Layers,       label: 'Multi-strategy support',      color: 'var(--tv-blue)' },
              { icon: BarChart2,    label: 'Advanced charting suite',     color: '#26a69a' },
              { icon: TrendingUp,   label: 'Auto order slicing',          color: '#ef5350' },
              { icon: Zap,          label: 'Zerodha & Upstox APIs',       color: 'var(--tv-blue)' },
              { icon: CheckCircle2, label: 'Paper trading mode',          color: '#26a69a' },
              { icon: Shield,       label: 'Portfolio stress tests',       color: '#ef5350' },
              { icon: Activity,     label: 'Live Greeks monitoring',       color: 'var(--tv-blue)' },
            ].map(({ icon: Icon, label, color }, i) => (
              <span
                key={i}
                className="inline-flex items-center gap-2 rounded-full px-4 py-2 text-[13px] font-medium flex-shrink-0"
                style={{ color: 'var(--tv-text-secondary)', background: 'rgba(255,255,255,0.04)', border: '1px solid rgba(255,255,255,0.06)' }}
              >
                <Icon size={13} style={{ color }} />
                {label}
              </span>
            ))}
          </div>
        </div>
      </div>

      {/* ── Feature cards ── */}
      <div ref={featsRef} className="px-4 py-20">
        <div className="mx-auto max-w-5xl">
          <div className="feat-heading text-center mb-12">
            <p className="panel-caption mb-2">Why Sniper</p>
            <h2
              className="text-[32px] font-black tracking-tight"
              style={{ color: 'var(--tv-text-primary)', letterSpacing: '-0.025em' }}
            >
              Everything a professional trader needs
            </h2>
          </div>

          <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
            <FeatureCard
              icon={BarChart2}
              title="Advanced Charts"
              body="Candlestick charts with EMA, VWAP, Bollinger Bands and custom strategy overlays."
              accent="var(--tv-blue)"
              visual={<CandlestickHero />}
            />
            <FeatureCard
              icon={Shield}
              title="Risk Engine"
              body="Real-time Greeks monitoring with automated circuit breakers and portfolio stress testing."
              accent="#26a69a"
              visual={<RiskGaugeSVG />}
            />
            <FeatureCard
              icon={TrendingUp}
              title="Smart Execution"
              body="Sub-25ms order routing via Zerodha with Upstox failover. Smart order slicing built in."
              accent="#ef5350"
              visual={<OrderBookSVG />}
            />
            <FeatureCard
              icon={Bell}
              title="Alerts & Notifications"
              body="Price and condition alerts with push and email. Never miss a level or breakout."
              accent="var(--tv-blue)"
              visual={
                <svg viewBox="0 0 160 120" className="w-full h-full" aria-hidden>
                  {/* Bell: top arc + sides + clapper */}
                  <path
                    d="M55 42 Q80 28 105 42 L100 82 Q80 92 60 82 Z"
                    fill="none"
                    stroke="#2962ff"
                    strokeWidth="2.5"
                    strokeLinejoin="round"
                    opacity="0.9"
                  />
                  <circle cx="80" cy="94" r="4" fill="#2962ff" />
                  {/* Notification stack */}
                  <rect x="50" y="36" width="60" height="7" rx="3" fill="#2962ff" opacity="0.4" />
                  <rect x="54" y="48" width="52" height="6" rx="2" fill="#2962ff" opacity="0.25" />
                  <rect x="58" y="58" width="44" height="5" rx="2" fill="#2962ff" opacity="0.15" />
                  <circle cx="112" cy="40" r="9" fill="#ef5350" />
                  <circle cx="112" cy="40" r="4" fill="#fff" />
                </svg>
              }
            />
          </div>
        </div>
      </div>

      {/* ── CTA banner ── */}
      <div
        ref={ctaBannerRef}
        className="mx-4 mb-16 rounded-2xl px-8 py-12 text-center relative overflow-hidden"
        style={{
          background: 'linear-gradient(135deg, var(--tv-bg-surface) 0%, var(--tv-bg-elevated) 100%)',
          border: '1px solid var(--tv-border-light)',
        }}
      >
        <div
          className="pointer-events-none absolute inset-0 rounded-2xl"
          style={{ background: 'radial-gradient(ellipse at 50% 0%, rgba(41,98,255,0.18) 0%, transparent 60%)' }}
          aria-hidden
        />
        <h2
          className="text-[28px] font-black tracking-tight mb-3 relative"
          style={{ color: 'var(--tv-text-primary)', letterSpacing: '-0.025em' }}
        >
          Ready to trade at institutional speed?
        </h2>
        <p className="text-[14px] mb-7 relative" style={{ color: 'var(--tv-text-secondary)' }}>
          Join thousands of traders using Sniper to execute with precision.
        </p>
        <Link href="/register">
          <button
            className="tv-btn tv-btn-primary px-8 py-3.5 text-[14px] font-semibold relative"
            style={{ boxShadow: '0 4px 24px rgba(41,98,255,0.4)', borderRadius: 8 }}
          >
            Start for Free → No credit card required
          </button>
        </Link>
      </div>

      {/* ── Footer ── */}
      <footer
        className="border-t px-8 py-6 flex items-center justify-between text-[11px]"
        style={{ borderColor: 'var(--tv-border)', color: 'var(--tv-text-muted)' }}
      >
        <span>© 2025 Sniper Pro. All rights reserved.</span>
        <span className="flex items-center gap-1.5">
          <span className="live-dot" />
          All systems operational
        </span>
      </footer>
    </main>
  );
}
