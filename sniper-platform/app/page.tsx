import Link from 'next/link';

export default function LandingPage() {
  return (
    <main className="mx-auto flex min-h-screen max-w-6xl flex-col justify-center gap-8 px-4 py-10 md:px-8">
      <div className="card-shell">
        <p className="text-sm uppercase tracking-[0.3em] text-brand">Institutional Alpha Stack</p>
        <h1 className="mt-3 font-heading text-4xl font-semibold md:text-6xl">Sniper Trading System</h1>
        <p className="mt-4 max-w-2xl text-slate-700 dark:text-slate-300">
          Strategy engine, tactical execution, and real-time risk guardian with optional IBM Quantum optimization.
        </p>
        <div className="mt-8 flex gap-3">
          <Link href="/login" className="rounded-xl bg-brand px-5 py-3 text-white">
            Login
          </Link>
          <Link href="/register" className="rounded-xl border border-slate-400 px-5 py-3 dark:border-slate-600">
            Register
          </Link>
        </div>
      </div>
    </main>
  );
}
