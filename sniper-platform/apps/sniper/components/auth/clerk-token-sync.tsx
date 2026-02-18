'use client';

import { useAuth } from '@clerk/nextjs';
import { useEffect, useRef } from 'react';

const TOKEN_KEY = 'token';
const REFRESH_MS = 55_000; // Refresh before expiry (Clerk tokens often 1 min)

/**
 * When the user is signed in with Clerk, sync the Clerk session token to
 * localStorage so the API client (Bearer token) is sent to the backend.
 * The backend accepts this as a valid Clerk JWT when CLERK_JWKS_URL is set.
 */
export function ClerkTokenSync() {
  const { isSignedIn, getToken } = useAuth();
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);

  useEffect(() => {
    if (!isSignedIn) {
      if (typeof window !== 'undefined') {
        window.localStorage.removeItem(TOKEN_KEY);
      }
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
      return;
    }

    const setToken = async () => {
      try {
        const token = await getToken();
        if (token && typeof window !== 'undefined') {
          window.localStorage.setItem(TOKEN_KEY, token);
        }
      } catch {
        // Ignore; getToken can fail if session is invalid
      }
    };

    void setToken();
    intervalRef.current = setInterval(setToken, REFRESH_MS);

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
    };
  }, [isSignedIn, getToken]);

  return null;
}
