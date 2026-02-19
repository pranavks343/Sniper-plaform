import type { Metadata } from 'next';
import { auth } from '@clerk/nextjs/server';
import { redirect } from 'next/navigation';
import LandingPageClient from './landing-page-client';

export const metadata: Metadata = {
  title: 'Home Page'
};

export default async function RootPage() {
  const { userId } = await auth();
  if (userId) {
    redirect('/dashboard');
  }
  return <LandingPageClient />;
}
