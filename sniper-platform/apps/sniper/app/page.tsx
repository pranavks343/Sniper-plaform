import type { Metadata } from 'next';
import { redirect } from 'next/navigation';
import LandingPageClient from './landing-page-client';

export const metadata: Metadata = {
  title: 'Home Page'
};

const isClerkConfigured = !!process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY;

export default async function RootPage() {
  if (isClerkConfigured) {
    const { auth } = await import('@clerk/nextjs/server');
    const { userId } = await auth();
    if (userId) {
      redirect('/dashboard');
    }
  }
  return <LandingPageClient />;
}
