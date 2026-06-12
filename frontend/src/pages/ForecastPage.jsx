import { useState, useMemo } from 'react';
import {
  LineChart, Line, AreaChart, Area,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend,
  ResponsiveContainer,
} from 'recharts';
import { TrendingUp, Calendar } from 'lucide-react';
import { useMedicines, useForecast } from '../hooks/useData';
import { LoadingState, ChartTooltip } from '../components/ui';

export default function ForecastPage() {
  const { data: medicines, loading: loadingMeds } = useMedicines();
  const [selectedId, setSelectedId] = useState(1);
  const [horizon, setHorizon] = useState(90);

  const { data: forecast, loading: loadingForecast } = useForecast(selectedId, horizon);

  /* Moving average (7-day) */
  const chartData = useMemo(() => {
    if (!forecast?.forecasts) return [];
    return forecast.forecasts.map((pt, i, arr) => {
      const windowStart = Math.max(0, i - 6);
      const window = arr.slice(windowStart, i + 1);
      const ma = Math.round(window.reduce((s, p) => s + p.predicted_units, 0) / window.length);
      return { ...pt, ma7: ma };
    });
  }, [forecast]);

  /* Summary stats */
  const stats = useMemo(() => {
    if (!forecast?.forecasts?.length) return null;
    const vals = forecast.forecasts.map(f => f.predicted_units);
    const total = vals.reduce((a, b) => a + b, 0);
    const peak = Math.max(...vals);
    const min = Math.min(...vals);
    const avg = Math.round(total / vals.length);
    return { total, peak, min, avg, mape: forecast.model_mape };
  }, [forecast]);

  if (loadingMeds) return <div className="main-content"><LoadingState /></div>;

  return (
    <div className="main-content animate-in">
      <div className="page-header">
        <h1>Demand Forecast</h1>
        <p>Prophet + ARIMA ensemble forecast with monsoon seasonality adjustment</p>
      </div>

      {/* Controls */}
      <div className="card" style={{ marginBottom: 'var(--space-md)' }}>
        <div style={{ display: 'flex', gap: 'var(--space-md)', flexWrap: 'wrap', alignItems: 'center' }}>
          <div>
            <label style={{ fontSize: 'var(--font-size-xs)', color: 'var(--color-text-tertiary)', display: 'block', marginBottom: 4, textTransform: 'uppercase', letterSpacing: '0.08em', fontWeight: 600 }}>
              Medicine
            </label>
            <select
              className="select-field"
              value={selectedId}
              onChange={e => setSelectedId(Number(e.target.value))}
              id="forecast-medicine-select"
            >
              {medicines.map(m => (
                <option key={m.id} value={m.id}>{m.name}</option>
              ))}
            </select>
          </div>
          <div>
            <label style={{ fontSize: 'var(--font-size-xs)', color: 'var(--color-text-tertiary)', display: 'block', marginBottom: 4, textTransform: 'uppercase', letterSpacing: '0.08em', fontWeight: 600 }}>
              Horizon
            </label>
            <select
              className="select-field"
              value={horizon}
              onChange={e => setHorizon(Number(e.target.value))}
              id="forecast-horizon-select"
            >
              <option value={30}>30 Days</option>
              <option value={60}>60 Days</option>
              <option value={90}>90 Days</option>
              <option value={180}>180 Days</option>
            </select>
          </div>
          {stats && (
            <div style={{ display: 'flex', gap: 'var(--space-xl)', marginLeft: 'auto', flexWrap: 'wrap' }}>
              <div>
                <div style={{ fontSize: 'var(--font-size-xs)', color: 'var(--color-text-tertiary)', textTransform: 'uppercase', letterSpacing: '0.08em', fontWeight: 600 }}>Avg Daily</div>
                <div className="mono" style={{ fontSize: 'var(--font-size-xl)', fontWeight: 700, color: 'var(--color-text-primary)' }}>{stats.avg}</div>
              </div>
              <div>
                <div style={{ fontSize: 'var(--font-size-xs)', color: 'var(--color-text-tertiary)', textTransform: 'uppercase', letterSpacing: '0.08em', fontWeight: 600 }}>Peak</div>
                <div className="mono" style={{ fontSize: 'var(--font-size-xl)', fontWeight: 700, color: 'var(--color-risk-high)' }}>{stats.peak}</div>
              </div>
              <div>
                <div style={{ fontSize: 'var(--font-size-xs)', color: 'var(--color-text-tertiary)', textTransform: 'uppercase', letterSpacing: '0.08em', fontWeight: 600 }}>MAPE</div>
                <div className="mono" style={{ fontSize: 'var(--font-size-xl)', fontWeight: 700, color: 'var(--color-accent-primary)' }}>{stats.mape}%</div>
              </div>
              <div>
                <div style={{ fontSize: 'var(--font-size-xs)', color: 'var(--color-text-tertiary)', textTransform: 'uppercase', letterSpacing: '0.08em', fontWeight: 600 }}>Total</div>
                <div className="mono" style={{ fontSize: 'var(--font-size-xl)', fontWeight: 700, color: 'var(--color-text-primary)' }}>{stats.total.toLocaleString()}</div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Forecast chart */}
      <div className="card" style={{ marginBottom: 'var(--space-md)' }}>
        <div className="card-header">
          <div className="card-title"><TrendingUp size={16} /> {forecast?.medicine_name} — {horizon}-Day Forecast</div>
        </div>
        {loadingForecast ? (
          <LoadingState message="Generating forecast…" />
        ) : (
          <ResponsiveContainer width="100%" height={380}>
            <AreaChart data={chartData} margin={{ top: 10, right: 30, bottom: 5, left: 0 }}>
              <defs>
                <linearGradient id="forecastGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#8b5cf6" stopOpacity={0.25} />
                  <stop offset="100%" stopColor="#8b5cf6" stopOpacity={0} />
                </linearGradient>
                <linearGradient id="ciGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#6366f1" stopOpacity={0.1} />
                  <stop offset="100%" stopColor="#6366f1" stopOpacity={0.02} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(139,92,246,0.06)" />
              <XAxis
                dataKey="forecast_date"
                tickFormatter={d => d.slice(5)}
                tick={{ fill: '#6b6980', fontSize: 11 }}
                axisLine={{ stroke: 'rgba(139,92,246,0.1)' }}
                interval={Math.floor(chartData.length / 8)}
              />
              <YAxis
                tick={{ fill: '#6b6980', fontSize: 11 }}
                axisLine={{ stroke: 'rgba(139,92,246,0.1)' }}
              />
              <Tooltip content={<ChartTooltip />} />
              <Legend wrapperStyle={{ fontSize: 11, color: '#a3a1b2' }} />
              <Area type="monotone" dataKey="upper_ci" name="Upper CI" stroke="none" fill="url(#ciGrad)" />
              <Area type="monotone" dataKey="lower_ci" name="Lower CI" stroke="none" fill="url(#ciGrad)" />
              <Area type="monotone" dataKey="predicted_units" name="Predicted" stroke="#8b5cf6" fill="url(#forecastGrad)" strokeWidth={2} dot={false} />
              <Line type="monotone" dataKey="ma7" name="7d Moving Avg" stroke="#c084fc" strokeWidth={2} dot={false} strokeDasharray="5 5" />
            </AreaChart>
          </ResponsiveContainer>
        )}
      </div>

      {/* Data table */}
      <div className="card">
        <div className="card-header">
          <div className="card-title"><Calendar size={16} /> Forecast Data Points</div>
          <span className="card-subtitle">{chartData.length} days</span>
        </div>
        <div className="data-table-wrap" style={{ maxHeight: 320, overflowY: 'auto' }}>
          <table className="data-table" id="forecast-data-table">
            <thead>
              <tr>
                <th>Date</th>
                <th style={{ textAlign: 'right' }}>Predicted</th>
                <th style={{ textAlign: 'right' }}>Lower CI</th>
                <th style={{ textAlign: 'right' }}>Upper CI</th>
                <th style={{ textAlign: 'right' }}>7d MA</th>
              </tr>
            </thead>
            <tbody>
              {chartData.slice(0, 30).map((pt, i) => (
                <tr key={i}>
                  <td style={{ color: 'var(--color-text-primary)' }}>{pt.forecast_date}</td>
                  <td className="mono text-right">{pt.predicted_units}</td>
                  <td className="mono text-right text-secondary">{pt.lower_ci}</td>
                  <td className="mono text-right text-secondary">{pt.upper_ci}</td>
                  <td className="mono text-right text-accent">{pt.ma7}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
