import { useMemo } from 'react';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Cell,
  ResponsiveContainer,
} from 'recharts';
import { PackageSearch, AlertTriangle, Clock } from 'lucide-react';
import { useReorderRecommendations } from '../hooks/useData';
import { StatCard, UrgencyBadge, LoadingState, ChartTooltip, formatINR, formatNumber } from '../components/ui';

export default function ReorderPage() {
  const { data: recs, loading } = useReorderRecommendations();

  const stats = useMemo(() => {
    if (!recs) return null;
    const urgent = recs.filter(r => r.urgency === 'URGENT');
    const warning = recs.filter(r => r.urgency === 'WARNING');
    const totalCost = recs.reduce((s, r) => s + r.estimated_cost_inr, 0);
    const totalQty = recs.reduce((s, r) => s + r.recommended_qty, 0);
    return { urgent: urgent.length, warning: warning.length, totalCost, totalQty };
  }, [recs]);

  const costChart = useMemo(() => {
    if (!recs) return [];
    return recs.map(r => ({
      name: r.medicine_name.length > 14 ? r.medicine_name.slice(0, 12) + '…' : r.medicine_name,
      cost: r.estimated_cost_inr,
      urgency: r.urgency,
    }));
  }, [recs]);

  if (loading) return <div className="main-content"><LoadingState /></div>;

  return (
    <div className="main-content animate-in">
      <div className="page-header">
        <h1>Reorder Engine</h1>
        <p>Safety stock + EOQ-based automated reorder recommendations (95% service level)</p>
      </div>

      {/* KPIs */}
      <div className="stat-grid stagger-children">
        <StatCard
          label="Urgent Orders"
          value={stats.urgent}
          icon={AlertTriangle}
          change="≤ 30 days of stock"
          changeType="negative"
          gradient
        />
        <StatCard
          label="Warning Orders"
          value={stats.warning}
          icon={Clock}
          change="31–60 days of stock"
          changeType="negative"
          gradient
        />
        <StatCard
          label="Total Order Qty"
          value={formatNumber(stats.totalQty)}
          icon={PackageSearch}
          change={`${recs.length} medicines`}
          gradient
        />
        <StatCard
          label="Estimated Budget"
          value={formatINR(stats.totalCost)}
          icon={PackageSearch}
          change="procurement budget needed"
          gradient
        />
      </div>

      {/* Cost bar chart */}
      <div className="card" style={{ marginBottom: 'var(--space-md)' }}>
        <div className="card-header">
          <div className="card-title"><PackageSearch size={16} /> Estimated Reorder Cost per Medicine</div>
        </div>
        <ResponsiveContainer width="100%" height={280}>
          <BarChart data={costChart} margin={{ top: 10, right: 30, bottom: 50, left: 10 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(139,92,246,0.06)" />
            <XAxis
              dataKey="name"
              tick={{ fill: '#a3a1b2', fontSize: 11 }}
              angle={-35}
              textAnchor="end"
              interval={0}
              axisLine={{ stroke: 'rgba(139,92,246,0.1)' }}
            />
            <YAxis
              tickFormatter={v => formatINR(v)}
              tick={{ fill: '#6b6980', fontSize: 11 }}
              axisLine={{ stroke: 'rgba(139,92,246,0.1)' }}
            />
            <Tooltip content={<ChartTooltip formatter={v => formatINR(v)} />} />
            <Bar dataKey="cost" name="Est. Cost" radius={[6, 6, 0, 0]} maxBarSize={40}>
              {costChart.map((entry, i) => (
                <Cell key={i} fill={entry.urgency === 'URGENT' ? '#f43f5e' : '#f59e0b'} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Recommendations table */}
      <div className="card">
        <div className="card-header">
          <div className="card-title">Reorder Recommendations</div>
          <span className="card-subtitle">{recs.length} items</span>
        </div>
        <div className="data-table-wrap">
          <table className="data-table" id="reorder-recommendations-table">
            <thead>
              <tr>
                <th>Medicine</th>
                <th>Urgency</th>
                <th style={{ textAlign: 'right' }}>Current Stock</th>
                <th style={{ textAlign: 'right' }}>Days Left</th>
                <th style={{ textAlign: 'right' }}>Safety Stock</th>
                <th style={{ textAlign: 'right' }}>Reorder Pt</th>
                <th style={{ textAlign: 'right' }}>Order Qty</th>
                <th style={{ textAlign: 'right' }}>Est. Cost</th>
                <th style={{ textAlign: 'right' }}>Daily Demand</th>
                <th style={{ textAlign: 'right' }}>Lead Time</th>
              </tr>
            </thead>
            <tbody>
              {recs.map(r => (
                <tr key={r.medicine_id}>
                  <td style={{ color: 'var(--color-text-primary)', fontWeight: 500 }}>{r.medicine_name}</td>
                  <td><UrgencyBadge urgency={r.urgency} /></td>
                  <td className="mono text-right">{formatNumber(r.current_stock)}</td>
                  <td className="mono text-right" style={{
                    color: r.days_of_stock <= 30 ? 'var(--color-risk-high)' : 'var(--color-risk-med)'
                  }}>{r.days_of_stock}d</td>
                  <td className="mono text-right">{formatNumber(r.safety_stock)}</td>
                  <td className="mono text-right">{formatNumber(r.reorder_point)}</td>
                  <td className="mono text-right font-semibold text-accent">{formatNumber(r.recommended_qty)}</td>
                  <td className="mono text-right">{formatINR(r.estimated_cost_inr)}</td>
                  <td className="mono text-right">{r.avg_daily_demand}</td>
                  <td className="mono text-right">{r.lead_time_days}d</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
