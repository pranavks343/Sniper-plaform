// ─── Components ────────────────────────────────────────────────────────────
export { Badge } from './components/badge';
export { Button } from './components/button';
export { Card, CardHeader, CardBody } from './components/card';
export { Input } from './components/input';
export { Select } from './components/select';
export { Switch } from './components/switch';
export { Table } from './components/table';

// ─── Hooks ──────────────────────────────────────────────────────────────────
export { useFadeUp, useScrollReveal, useCountUp } from './hooks/use-gsap';

// ─── Lib ────────────────────────────────────────────────────────────────────
export { cn, formatINR } from './lib/utils';
export { calculateEma, calculateVwap, toLineSeries, clamp } from './lib/chart-math';
