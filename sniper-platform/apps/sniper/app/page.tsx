import type { Metadata } from 'next';
import LandingPageClient from './landing-page-client';

export const metadata: Metadata = {
  title: 'Home Page'
};

export default function RootPage() {
  return <LandingPageClient />;
}
