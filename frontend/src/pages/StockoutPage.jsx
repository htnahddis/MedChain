import { useState, useMemo } from 'react';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Cell,
  ResponsiveContainer, ScatterChart, Scatter, ZAxis,
} from 'recharts';
import { Activity, AlertTriangle } from 'lucide-react';
import { useStockoutRisk } from '../hooks/useData';
import { LoadingState, ChartTooltip, formatNumber } from '../components/ui';

export default function StockoutPage() {
  const [horizon, setHorizon] = useState(30);
  const { data: stockoutRisk, loading } = useStockoutRisk(horizon);

  const barData = useMemo(() => {
    if (!stockoutRisk) return [];
    return stockoutRisk.map(s => ({
      name: s.medicine_name.length > 14 ? s.medicine_name.slice(0, 12) + '…' : s.medicine_name,
      probability: s.stockout_probability_pct,
      stockDays: s.stock_days,
      full_name: s.medicine_name,
    }));
  }, [stockoutRisk]);

  const scatterData = useMemo(() => {
    if (!stockoutRisk) return [];
    return stockoutRisk.map(s => ({
      x: s.stock_days,
      y: s.stockout_probability_pct,
      z: s.avg_daily_demand,
      name: s.medicine_name,
    }));
  }, [stockoutRisk]);

  if (loading) return <div className="main-content"><LoadingState /></div>;

  return (
    <div className="main-content animate-in">
      <div className="page-header">
        <div className="page-header-row">
          <div>
            <h1>Stockout Monitor</h1>
            <p>Probability-based stockout risk assessment across all medicines</p>
          </div>
          <select
            className="select-field"
            value={horizon}
            onChange={e => setHorizon(Number(e.target.value))}
            id="stockout-horizon-select"
          >
            <option value={30}>30-Day Horizon</option>
            <option value={60}>60-Day Horizon</option>
            <option value={90}>90-Day Horizon</option>
          </select>
        </div>
      </div>

      {/* Probability bar chart */}
      <div className="card" style={{ marginBottom: 'var(--space-md)' }}>
        <div className="card-header">
          <div className="card-title"><AlertTriangle size={16} /> Stockout Probability — {horizon}-Day</div>
        </div>
        <ResponsiveContainer width="100%" height={320}>
          <BarChart data={barData} margin={{ top: 10, right: 30, bottom: 60, left: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(139,92,246,0.06)" />
            <XAxis
              dataKey="name"
              tick={{ fill: '#a3a1b2', fontSize: 11 }}
              angle={-40}
              textAnchor="end"
              interval={0}
              axisLine={{ stroke: 'rgba(139,92,246,0.1)' }}
            />
            <YAxis
              domain={[0, 100]}
              tickFormatter={v => `${v}%`}
              tick={{ fill: '#6b6980', fontSize: 11 }}
              axisLine={{ stroke: 'rgba(139,92,246,0.1)' }}
            />
            <Tooltip content={<ChartTooltip formatter={v => `${v}%`} />} />
            <Bar dataKey="probability" name="Stockout Prob" radius={[6, 6, 0, 0]} maxBarSize={36}>
              {barData.map((entry, i) => (
                <Cell
                  key={i}
                  fill={entry.probability > 60 ? '#f43f5e' : entry.probability > 30 ? '#f59e0b' : '#10b981'}
                />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Scatter: Stock Days vs Probability */}
      <div className="dashboard-grid cols-2">
        <div className="card">
          <div className="card-header">
            <div className="card-title"><Activity size={16} /> Stock Days vs Probability</div>
            <span className="card-subtitle">Bubble size = daily demand</span>
          </div>
          <ResponsiveContainer width="100%" height={320}>
            <ScatterChart margin={{ top: 10, right: 20, bottom: 10, left: 10 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(139,92,246,0.06)" />
              <XAxis
                dataKey="x"
                name="Stock Days"
                tick={{ fill: '#6b6980', fontSize: 11 }}
                axisLine={{ stroke: 'rgba(139,92,246,0.1)' }}
                label={{ value: 'Stock Days', position: 'insideBottom', offset: -5, fill: '#6b6980', fontSize: 11 }}
              />
              <YAxis
                dataKey="y"
                name="Stockout %"
                tick={{ fill: '#6b6980', fontSize: 11 }}
                axisLine={{ stroke: 'rgba(139,92,246,0.1)' }}
                label={{ value: 'Stockout %', angle: -90, position: 'insideLeft', fill: '#6b6980', fontSize: 11 }}
              />
              <ZAxis dataKey="z" range={[40, 300]} />
              <Tooltip content={({ active, payload }) => {
                if (!active || !payload?.length) return null;
                const d = payload[0].payload;
                return (
                  <div className="chart-tooltip">
                    <div className="label">{d.name}</div>
                    <div className="value">Stock: {d.x} days</div>
                    <div className="value">Prob: {d.y}%</div>
                    <div className="value">Demand: {d.z}/day</div>
                  </div>
                );
              }} />
              <Scatter data={scatterData} fill="#8b5cf6" fillOpacity={0.6} stroke="#8b5cf6" strokeWidth={1} />
            </ScatterChart>
          </ResponsiveContainer>
        </div>

        {/* Detail table */}
        <div className="card">
          <div className="card-header">
            <div className="card-title">Detailed Analysis</div>
          </div>
          <div className="data-table-wrap" style={{ maxHeight: 340, overflowY: 'auto' }}>
            <table className="data-table" id="stockout-detail-table">
              <thead>
                <tr>
                  <th>Medicine</th>
                  <th>Category</th>
                  <th style={{ textAlign: 'right' }}>Stock</th>
                  <th style={{ textAlign: 'right' }}>Days</th>
                  <th style={{ textAlign: 'right' }}>Daily</th>
                  <th style={{ textAlign: 'right' }}>Prob</th>
                </tr>
              </thead>
              <tbody>
                {stockoutRisk.map(s => (
                  <tr key={s.medicine_id}>
                    <td style={{ color: 'var(--color-text-primary)', fontWeight: 500 }}>{s.medicine_name}</td>
                    <td>{s.category}</td>
                    <td className="mono text-right">{formatNumber(s.current_stock)}</td>
                    <td className="mono text-right">{s.stock_days}d</td>
                    <td className="mono text-right">{s.avg_daily_demand}</td>
                    <td className="text-right">
                      <span className="mono font-semibold" style={{
                        color: s.stockout_probability_pct > 60 ? 'var(--color-risk-high)' : s.stockout_probability_pct > 30 ? 'var(--color-risk-med)' : 'var(--color-risk-low)'
                      }}>
                        {s.stockout_probability_pct}%
                      </span>
                    </td>
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
