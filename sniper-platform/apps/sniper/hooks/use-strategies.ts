'use client';

import { useEffect } from 'react';

import { useStrategyStore } from '@/store/strategy-store';

export function useStrategies() {
  const store = useStrategyStore();
  const fetchStrategies = useStrategyStore((state) => state.fetchStrategies);

  useEffect(() => {
    void fetchStrategies();
  }, [fetchStrategies]);

  return store;
}
