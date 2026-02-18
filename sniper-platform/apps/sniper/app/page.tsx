import { auth } from '@clerk/nextjs/server';
import { redirect } from 'next/navigation';
import LandingPageClient from './landing-page-client';

export default async function RootPage() {
  const { userId } = await auth();
  if (userId) {
    redirect('/dashboard');
  }
  return <LandingPageClient />;
}
