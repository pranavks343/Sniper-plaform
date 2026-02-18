export default function AuthLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="auth-bg relative min-h-screen w-full overflow-hidden">
      {/* Base gradient (subtle pulse) */}
      <div
        className="auth-bg-base absolute inset-0"
        style={{
          background:
            'linear-gradient(165deg, #0f1119 0%, #131722 35%, #1a1d2e 70%, #131722 100%)',
        }}
      />
      {/* Glow orbs – floating + pulse */}
      <div
        className="auth-orb auth-orb-1 pointer-events-none absolute -top-[40%] left-1/2 h-[80vw] max-h-[800px] w-[80vw] max-w-[800px] -translate-x-1/2 rounded-full"
        style={{
          background: 'radial-gradient(circle, rgba(41,98,255,0.18) 0%, transparent 65%)',
          filter: 'blur(48px)',
        }}
        aria-hidden
      />
      <div
        className="auth-orb auth-orb-2 pointer-events-none absolute top-[20%] -right-[20%] h-[60vmin] w-[60vmin] rounded-full"
        style={{
          background: 'radial-gradient(circle, rgba(38,166,154,0.12) 0%, transparent 65%)',
          filter: 'blur(40px)',
        }}
        aria-hidden
      />
      <div
        className="auth-orb auth-orb-3 pointer-events-none absolute bottom-[10%] -left-[15%] h-[50vmin] w-[50vmin] rounded-full"
        style={{
          background: 'radial-gradient(circle, rgba(99,102,241,0.1) 0%, transparent 65%)',
          filter: 'blur(36px)',
        }}
        aria-hidden
      />
      {/* Subtle grid overlay */}
      <div
        className="auth-grid pointer-events-none absolute inset-0"
        style={{
          backgroundImage: `
            linear-gradient(rgba(255,255,255,0.08) 1px, transparent 1px),
            linear-gradient(90deg, rgba(255,255,255,0.08) 1px, transparent 1px)
          `,
          backgroundSize: '48px 48px',
        }}
        aria-hidden
      />
      {/* Content on top */}
      <div className="relative z-10">{children}</div>
    </div>
  );
}
