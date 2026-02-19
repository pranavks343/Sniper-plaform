import { SignIn } from '@clerk/nextjs';
import { redirect } from 'next/navigation';

const isClerkConfigured =
  !!process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY &&
  !process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY.startsWith('pk_test_');

export default async function LoginPage() {
  if (isClerkConfigured) {
    const { auth } = await import('@clerk/nextjs/server');
    const { userId } = await auth();
    if (userId) redirect('/dashboard');
  }

  if (!isClerkConfigured) {
    return (
      <main className="mx-auto flex min-h-screen max-w-md items-center justify-center px-4 py-8">
        <div className="rounded-xl p-8 text-center" style={{ background: 'var(--tv-bg-surface)', border: '1px solid var(--tv-border)' }}>
          <h2 className="text-lg font-bold mb-3" style={{ color: 'var(--tv-text-primary)' }}>Sign In Unavailable</h2>
          <p className="text-sm mb-4" style={{ color: 'var(--tv-text-secondary)' }}>
            Authentication is not configured for this deployment. Please set production Clerk API keys.
          </p>
          <a href="/" className="tv-btn tv-btn-primary px-6 py-2 text-sm">Back to Home</a>
        </div>
      </main>
    );
  }

  return (
    <main className="mx-auto flex min-h-screen max-w-md items-center justify-center px-4 py-8">
      <SignIn routing="path" path="/login" signUpUrl="/register" fallbackRedirectUrl="/dashboard" />
    </main>
  );
}
