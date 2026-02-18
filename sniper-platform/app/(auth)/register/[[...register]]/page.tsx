import { SignUp } from '@clerk/nextjs';
import { auth } from '@clerk/nextjs/server';
import { redirect } from 'next/navigation';

export default async function RegisterPage() {
  const { userId } = await auth();
  if (userId) redirect('/dashboard');
  return (
    <main className="mx-auto flex min-h-screen max-w-md items-center justify-center px-4 py-8">
      <SignUp routing="path" path="/register" signInUrl="/login" fallbackRedirectUrl="/dashboard" />
    </main>
  );
}
