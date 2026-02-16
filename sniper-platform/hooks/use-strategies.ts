'use client';

import { useEffect } from 'react';

import { useStrategyStore } from '@/store/strategy-store';

export function useStrategies() {
  const store = useStrategyStore();

  useEffect(() => {
    void store.fetchStrategies();
  }, [store]);

  return store;
}
