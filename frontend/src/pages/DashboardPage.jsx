import { useMemo } from 'react';
import {
  AreaChart, Area, BarChart, Bar, PieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend,
} from 'recharts';
import {
  ShieldAlert, TrendingUp, PackageSearch, AlertTriangle,
  ArrowUpRight, ArrowDownRight, Activity, Pill,
} from 'lucide-react';
import { useRiskScores, useStockoutRisk, useReorderRecommendations, useConsumptionTrend } from '../hooks/useData';
import { StatCard, RiskBadge, UrgencyBadge, RiskMeter, LoadingState, ChartTooltip, formatINR, formatNumber } from '../components/ui';

const CHART_COLORS = ['#8b5cf6', '#6366f1', '#a78bfa', '#c084fc', '#818cf8', '#4f46e5', '#7c3aed'];

export default function DashboardPage() {
  const { data: riskScores, loading: loadingRisk } = useRiskScores();
  const { data: stockoutRisk, loading: loadingStockout } = useStockoutRisk(30);
  const { data: reorderRecs, loading: loadingReorder } = useReorderRecommendations();
  const { data: trend, loading: loadingTrend } = useConsumptionTrend();

  const loading = loadingRisk || loadingStockout || loadingReorder || loadingTrend;

  /* Derived KPIs */
  const kpis = useMemo(() => {
    if (!riskScores || !stockoutRisk || !reorderRecs) return null;
    const highRisk = riskScores.filter(r => r.risk_tier === 'HIGH').length;
    const criticalStockout = stockoutRisk.filter(s => s.stockout_probability_pct > 60).length;
    const urgentOrders = reorderRecs.filter(r => r.urgency === 'URGENT').length;
    const totalReorderCost = reorderRecs.reduce((s, r) => s + r.estimated_cost_inr, 0);
    const avgRiskScore = riskScores.length
      ? (riskScores.reduce((s, r) => s + r.composite_score, 0) / riskScores.length)
      : 0;
    return { highRisk, criticalStockout, urgentOrders, totalReorderCost, avgRiskScore };
  }, [riskScores, stockoutRisk, reorderRecs]);

  /* Category pie data */
  const categoryPie = useMemo(() => {
    if (!riskScores) return [];
    const cats = {};
    riskScores.forEach(r => {
      cats[r.category] = (cats[r.category] || 0) + 1;
    });
    return Object.entries(cats).map(([name, value]) => ({ name, value }));
  }, [riskScores]);

  /* Risk distribution */
  const riskDistribution = useMemo(() => {
    if (!riskScores) return [];
    const tiers = { HIGH: 0, MED: 0, LOW: 0 };
    riskScores.forEach(r => { tiers[r.risk_tier]++; });
    return [
      { name: 'High Risk', value: tiers.HIGH, color: '#f43f5e' },
      { name: 'Medium Risk', value: tiers.MED, color: '#f59e0b' },
      { name: 'Low Risk', value: tiers.LOW, color: '#10b981' },
    ];
  }, [riskScores]);

  if (loading) {
    return (
      <div className="main-content">
        <LoadingState message="Loading dashboard…" />
      </div>
    );
  }

  return (
    <div className="main-content animate-in">
      {/* Page Header */}
      <div className="page-header">
        <div className="page-header-row">
          <div>
            <h1>Decision Support Dashboard</h1>
            <p>Pharmaceutical supply chain intelligence — real-time risk monitoring & reorder automation</p>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <span style={{ fontSize: 'var(--font-size-xs)', color: 'var(--color-text-tertiary)' }}>
              Last updated: {new Date().toLocaleTimeString()}
            </span>
          </div>
        </div>
      </div>

      {/* KPI Strip */}
      <div className="stat-grid stagger-children">
        <StatCard
          label="High-Risk Medicines"
          value={kpis.highRisk}
          icon={ShieldAlert}
          change={`of ${riskScores.length} total`}
          changeType={kpis.highRisk > 3 ? 'negative' : 'positive'}
          gradient
        />
        <StatCard
          label="Stockout Threats (30d)"
          value={kpis.criticalStockout}
          icon={AlertTriangle}
          change={kpis.criticalStockout > 0 ? 'Immediate action needed' : 'All clear'}
          changeType={kpis.criticalStockout > 0 ? 'negative' : 'positive'}
          gradient
        />
        <StatCard
          label="Urgent Reorders"
          value={kpis.urgentOrders}
          icon={PackageSearch}
          change={`${reorderRecs.length} total pending`}
          changeType={kpis.urgentOrders > 2 ? 'negative' : 'positive'}
          gradient
        />
        <StatCard
          label="Reorder Budget"
          value={formatINR(kpis.totalReorderCost)}
          icon={TrendingUp}
          change={`Avg risk: ${kpis.avgRiskScore.toFixed(1)}`}
          changeType="neutral"
          gradient
        />
      </div>

      {/* Row 1: Consumption Trend + Risk Distribution */}
      <div className="dashboard-grid cols-2-1" style={{ marginBottom: 'var(--space-md)' }}>
        {/* Consumption Trend */}
        <div className="card">
          <div className="card-header">
            <div className="card-title"><Activity size={16} /> Hospital Consumption Trend (30 Days)</div>
          </div>
          <ResponsiveContainer width="100%" height={260}>
            <AreaChart data={trend} margin={{ top: 5, right: 20, bottom: 5, left: 0 }}>
              <defs>
                <linearGradient id="gradAntibiotic" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#8b5cf6" stopOpacity={0.3} />
                  <stop offset="100%" stopColor="#8b5cf6" stopOpacity={0} />
                </linearGradient>
                <linearGradient id="gradCardio" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#6366f1" stopOpacity={0.3} />
                  <stop offset="100%" stopColor="#6366f1" stopOpacity={0} />
                </linearGradient>
                <linearGradient id="gradDiabetic" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#a78bfa" stopOpacity={0.3} />
                  <stop offset="100%" stopColor="#a78bfa" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(139,92,246,0.06)" />
              <XAxis
                dataKey="date"
                tickFormatter={d => d.slice(5)}
                tick={{ fill: '#6b6980', fontSize: 11 }}
                axisLine={{ stroke: 'rgba(139,92,246,0.1)' }}
              />
              <YAxis
                tick={{ fill: '#6b6980', fontSize: 11 }}
                axisLine={{ stroke: 'rgba(139,92,246,0.1)' }}
              />
              <Tooltip content={<ChartTooltip />} />
              <Legend
                wrapperStyle={{ fontSize: 11, color: '#a3a1b2' }}
              />
              <Area type="monotone" dataKey="antibiotic" name="Antibiotic" stroke="#8b5cf6" fill="url(#gradAntibiotic)" strokeWidth={2} />
              <Area type="monotone" dataKey="cardiovascular" name="Cardiovascular" stroke="#6366f1" fill="url(#gradCardio)" strokeWidth={2} />
              <Area type="monotone" dataKey="antidiabetic" name="Antidiabetic" stroke="#a78bfa" fill="url(#gradDiabetic)" strokeWidth={2} />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        {/* Risk Distribution */}
        <div className="card">
          <div className="card-header">
            <div className="card-title"><ShieldAlert size={16} /> Risk Distribution</div>
          </div>
          <ResponsiveContainer width="100%" height={220}>
            <PieChart>
              <Pie
                data={riskDistribution}
                cx="50%"
                cy="50%"
                innerRadius={55}
                outerRadius={80}
                dataKey="value"
                stroke="none"
                paddingAngle={4}
              >
                {riskDistribution.map((entry, i) => (
                  <Cell key={i} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip content={<ChartTooltip />} />
            </PieChart>
          </ResponsiveContainer>
          <div style={{ display: 'flex', justifyContent: 'center', gap: 16, marginTop: 8 }}>
            {riskDistribution.map(d => (
              <div key={d.name} style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: 'var(--font-size-xs)' }}>
                <span style={{ width: 8, height: 8, borderRadius: '50%', background: d.color, display: 'inline-block' }} />
                <span style={{ color: 'var(--color-text-secondary)' }}>{d.name}</span>
                <span className="mono" style={{ fontWeight: 600 }}>{d.value}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Row 2: Top risk table + Category breakdown */}
      <div className="dashboard-grid cols-2" style={{ marginBottom: 'var(--space-md)' }}>
        {/* Top Risk Medicines */}
        <div className="card">
          <div className="card-header">
            <div className="card-title"><ShieldAlert size={16} /> Top Risk Medicines</div>
            <span className="card-subtitle">by composite score</span>
          </div>
          <div className="data-table-wrap" style={{ maxHeight: 320, overflowY: 'auto' }}>
            <table className="data-table" id="top-risk-table">
              <thead>
                <tr>
                  <th>Medicine</th>
                  <th>Category</th>
                  <th>Risk</th>
                  <th>Score</th>
                </tr>
              </thead>
              <tbody>
                {riskScores.slice(0, 8).map(r => (
                  <tr key={r.medicine_id}>
                    <td style={{ color: 'var(--color-text-primary)', fontWeight: 500 }}>{r.medicine_name}</td>
                    <td>{r.category}</td>
                    <td><RiskBadge tier={r.risk_tier} /></td>
                    <td><RiskMeter score={r.composite_score} /></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Category Bar Chart */}
        <div className="card">
          <div className="card-header">
            <div className="card-title"><Pill size={16} /> Medicines by Category</div>
          </div>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={categoryPie} layout="vertical" margin={{ top: 5, right: 30, bottom: 5, left: 80 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(139,92,246,0.06)" horizontal={false} />
              <XAxis type="number" tick={{ fill: '#6b6980', fontSize: 11 }} axisLine={{ stroke: 'rgba(139,92,246,0.1)' }} />
              <YAxis
                type="category"
                dataKey="name"
                tick={{ fill: '#a3a1b2', fontSize: 12 }}
                axisLine={{ stroke: 'rgba(139,92,246,0.1)' }}
                width={80}
              />
              <Tooltip content={<ChartTooltip />} />
              <Bar dataKey="value" name="Count" radius={[0, 6, 6, 0]} maxBarSize={24}>
                {categoryPie.map((_, i) => (
                  <Cell key={i} fill={CHART_COLORS[i % CHART_COLORS.length]} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Row 3: Stockout Threats + Reorder Queue */}
      <div className="dashboard-grid cols-2">
        {/* Stockout Threats */}
        <div className="card">
          <div className="card-header">
            <div className="card-title"><AlertTriangle size={16} /> Stockout Threats</div>
            <span className="card-subtitle">30-day horizon</span>
          </div>
          <div className="data-table-wrap" style={{ maxHeight: 280, overflowY: 'auto' }}>
            <table className="data-table" id="stockout-table">
              <thead>
                <tr>
                  <th>Medicine</th>
                  <th style={{ textAlign: 'right' }}>Stock Days</th>
                  <th style={{ textAlign: 'right' }}>Prob %</th>
                </tr>
              </thead>
              <tbody>
                {stockoutRisk.slice(0, 6).map(s => (
                  <tr key={s.medicine_id}>
                    <td style={{ color: 'var(--color-text-primary)', fontWeight: 500 }}>{s.medicine_name}</td>
                    <td className="mono text-right">{s.stock_days}d</td>
                    <td className="text-right">
                      <span
                        className="mono font-semibold"
                        style={{
                          color: s.stockout_probability_pct > 60
                            ? 'var(--color-risk-high)'
                            : s.stockout_probability_pct > 30
                            ? 'var(--color-risk-med)'
                            : 'var(--color-risk-low)'
                        }}
                      >
                        {s.stockout_probability_pct}%
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Reorder Queue */}
        <div className="card">
          <div className="card-header">
            <div className="card-title"><PackageSearch size={16} /> Reorder Queue</div>
            <span className="card-subtitle">{reorderRecs.length} pending</span>
          </div>
          <div className="data-table-wrap" style={{ maxHeight: 280, overflowY: 'auto' }}>
            <table className="data-table" id="reorder-table">
              <thead>
                <tr>
                  <th>Medicine</th>
                  <th>Urgency</th>
                  <th style={{ textAlign: 'right' }}>Qty</th>
                  <th style={{ textAlign: 'right' }}>Cost</th>
                </tr>
              </thead>
              <tbody>
                {reorderRecs.map(r => (
                  <tr key={r.medicine_id}>
                    <td style={{ color: 'var(--color-text-primary)', fontWeight: 500 }}>{r.medicine_name}</td>
                    <td><UrgencyBadge urgency={r.urgency} /></td>
                    <td className="mono text-right">{formatNumber(r.recommended_qty)}</td>
                    <td className="mono text-right">{formatINR(r.estimated_cost_inr)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}
