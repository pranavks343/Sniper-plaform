'use client';

import Link from 'next/link';

import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';

export default function LoginPage() {
  return (
    <main className="mx-auto flex min-h-screen max-w-md items-center px-4">
      <div className="card-shell w-full space-y-4">
        <h1 className="font-heading text-3xl">Login</h1>
        <Input placeholder="Email" type="email" />
        <Input placeholder="Password" type="password" />
        <Button className="w-full">Sign In</Button>
        <p className="text-sm text-slate-600 dark:text-slate-300">
          No account?{' '}
          <Link href="/register" className="text-brand underline">
            Register
          </Link>
        </p>
      </div>
    </main>
  );
}
