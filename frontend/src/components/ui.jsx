export function StatCard({ label, value, icon: Icon, change, changeType, gradient }) {
  return (
    <div className="stat-card">
      <div className="stat-card-label">
        {Icon && <Icon size={14} />}
        {label}
      </div>
      <div className={`stat-card-value ${gradient ? 'gradient' : ''}`}>
        {value}
      </div>
      {change !== undefined && (
        <div className={`stat-card-change ${changeType || ''}`}>
          {change}
        </div>
      )}
      {Icon && (
        <div className="stat-card-icon">
          <Icon size={24} />
        </div>
      )}
    </div>
  );
}

export function RiskBadge({ tier }) {
  const cls = tier === 'HIGH' ? 'badge-high' : tier === 'MED' ? 'badge-med' : 'badge-low';
  return <span className={`badge ${cls}`}>{tier}</span>;
}

export function UrgencyBadge({ urgency }) {
  const cls = urgency === 'URGENT' ? 'badge-urgent' : urgency === 'WARNING' ? 'badge-warning' : 'badge-info';
  return <span className={`badge ${cls}`}>{urgency}</span>;
}

export function RiskMeter({ score, max = 100 }) {
  const pct = Math.min(100, (score / max) * 100);
  const color = pct >= 65 ? 'high' : pct >= 35 ? 'med' : 'low';
  return (
    <div className="risk-meter">
      <div className="risk-meter-bar">
        <div
          className={`risk-meter-fill progress-bar-fill ${color}`}
          style={{ width: `${pct}%` }}
        />
      </div>
      <span className="risk-meter-value" style={{ color: `var(--color-risk-${color})` }}>
        {score.toFixed(1)}
      </span>
    </div>
  );
}

export function LoadingState({ message = 'Loading data…' }) {
  return (
    <div className="loading-container">
      <div className="spinner" />
      <span>{message}</span>
    </div>
  );
}

export function SkeletonCard() {
  return (
    <div className="card" style={{ minHeight: 200 }}>
      <div className="skeleton" style={{ height: 16, width: '40%', marginBottom: 16 }} />
      <div className="skeleton" style={{ height: 32, width: '60%', marginBottom: 12 }} />
      <div className="skeleton" style={{ height: 12, width: '80%', marginBottom: 8 }} />
      <div className="skeleton" style={{ height: 12, width: '55%' }} />
    </div>
  );
}

export function ChartTooltip({ active, payload, label, formatter }) {
  if (!active || !payload?.length) return null;
  return (
    <div className="chart-tooltip">
      <div className="label">{label}</div>
      {payload.map((entry, i) => (
        <div key={i} className="value" style={{ color: entry.color }}>
          {entry.name}: {formatter ? formatter(entry.value) : entry.value.toLocaleString()}
        </div>
      ))}
    </div>
  );
}

export function formatINR(value) {
  if (value >= 100000) return `₹${(value / 100000).toFixed(1)}L`;
  if (value >= 1000) return `₹${(value / 1000).toFixed(1)}K`;
  return `₹${value.toFixed(0)}`;
}

export function formatNumber(value) {
  if (value >= 100000) return `${(value / 1000).toFixed(0)}K`;
  return value.toLocaleString('en-IN');
}
