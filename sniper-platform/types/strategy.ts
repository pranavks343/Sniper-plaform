export type Regime = 'TRENDING' | 'MEAN_REVERTING' | 'VOLATILE';

export type Strategy = {
  id: string;
  user_id: string;
  name: string;
  type: string;
  parameters: Record<string, unknown>;
  status: 'active' | 'inactive';
  regime_filters: Regime[];
  created_at: string;
};
