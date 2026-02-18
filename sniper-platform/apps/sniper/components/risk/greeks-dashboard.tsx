function GreekGauge({
  label,
  value,
  limit,
  symbol,
}: {
  label: string;
  value: number;
  limit: number;
  symbol?: string;
}) {
  const usage = Math.min(100, Math.abs((value / limit) * 100));
  const fillColor =
    usage > 90 ? '#ef5350' :
    usage > 70 ? '#f7a600' :
    '#26a69a';

  return (
    <div
      className="rounded-md p-4"
      style={{ background: 'var(--tv-bg-surface)', border: '1px solid var(--tv-border)' }}
    >
      <div className="flex items-start justify-between mb-3">
        <div>
          <p className="panel-caption mb-1">{label}</p>
          <p
            className="text-[22px] font-bold font-mono"
            style={{ color: fillColor, letterSpacing: '-0.02em' }}
          >
            {symbol}{value.toFixed(label === 'Gamma' ? 3 : 1)}
          </p>
        </div>
        <div
          className="flex h-8 w-8 items-center justify-center rounded text-[11px] font-bold"
          style={{
            background: `${fillColor}18`,
            color: fillColor,
            border: `1px solid ${fillColor}40`,
          }}
        >
          {usage.toFixed(0)}%
        </div>
      </div>

      {/* Track */}
      <div className="risk-bar-track">
        <div
          className="risk-bar-fill"
          style={{ width: `${usage}%`, background: fillColor }}
        />
      </div>

      <div className="flex items-center justify-between mt-2">
        <span className="panel-caption">Used</span>
        <span className="text-[11px] font-mono" style={{ color: 'var(--tv-text-muted)' }}>
          {value.toFixed(label === 'Gamma' ? 3 : 1)} / {limit}
        </span>
      </div>
    </div>
  );
}

export function GreeksDashboard({
  greeks,
}: {
  greeks: { delta: number; gamma: number; theta: number; vega: number };
}) {
  return (
    <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-4">
      <GreekGauge label="Delta" value={greeks.delta} limit={500} />
      <GreekGauge label="Gamma" value={greeks.gamma} limit={50} />
      <GreekGauge label="Theta" value={greeks.theta} limit={10000} symbol="-" />
      <GreekGauge label="Vega"  value={greeks.vega}  limit={10000} />
    </div>
  );
}
