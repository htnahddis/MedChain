import { useState, useMemo } from 'react';
import {
  RadarChart, Radar, PolarGrid, PolarAngleAxis, PolarRadiusAxis,
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Cell,
  ResponsiveContainer,
} from 'recharts';
import { ShieldAlert, Filter } from 'lucide-react';
import { useRiskScores } from '../hooks/useData';
import { RiskBadge, RiskMeter, LoadingState, ChartTooltip } from '../components/ui';

export default function RiskPage() {
  const { data: riskScores, loading } = useRiskScores();
  const [filterTier, setFilterTier] = useState('ALL');
  const [selectedMed, setSelectedMed] = useState(null);

  const filtered = useMemo(() => {
    if (!riskScores) return [];
    if (filterTier === 'ALL') return riskScores;
    return riskScores.filter(r => r.risk_tier === filterTier);
  }, [riskScores, filterTier]);

  const radarData = useMemo(() => {
    if (!selectedMed) return [];
    return [
      { factor: 'Supplier', score: selectedMed.supplier_score, fullMark: 100 },
      { factor: 'API Dep.', score: selectedMed.api_dependency_score, fullMark: 100 },
      { factor: 'Shelf Life', score: selectedMed.shelf_life_score, fullMark: 100 },
      { factor: 'Criticality', score: selectedMed.criticality_score, fullMark: 100 },
    ];
  }, [selectedMed]);

  /* Risk bar chart (all medicines) */
  const barData = useMemo(() => {
    if (!riskScores) return [];
    return riskScores.slice(0, 12).map(r => ({
      name: r.medicine_name.length > 16 ? r.medicine_name.slice(0, 14) + '…' : r.medicine_name,
      score: r.composite_score,
      tier: r.risk_tier,
    }));
  }, [riskScores]);

  if (loading) return <div className="main-content"><LoadingState /></div>;

  return (
    <div className="main-content animate-in">
      <div className="page-header">
        <h1>Risk Assessment</h1>
        <p>Composite supply chain disruption risk scoring for all medicines</p>
      </div>

      {/* Risk bar chart */}
      <div className="card" style={{ marginBottom: 'var(--space-md)' }}>
        <div className="card-header">
          <div className="card-title"><ShieldAlert size={16} /> Composite Risk Scores — All Medicines</div>
        </div>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={barData} margin={{ top: 5, right: 20, bottom: 50, left: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(139,92,246,0.06)" />
            <XAxis
              dataKey="name"
              tick={{ fill: '#a3a1b2', fontSize: 11 }}
              angle={-35}
              textAnchor="end"
              axisLine={{ stroke: 'rgba(139,92,246,0.1)' }}
              interval={0}
            />
            <YAxis
              domain={[0, 100]}
              tick={{ fill: '#6b6980', fontSize: 11 }}
              axisLine={{ stroke: 'rgba(139,92,246,0.1)' }}
            />
            <Tooltip content={<ChartTooltip />} />
            <Bar dataKey="score" name="Risk Score" radius={[6, 6, 0, 0]} maxBarSize={36}>
              {barData.map((entry, i) => (
                <Cell
                  key={i}
                  fill={entry.tier === 'HIGH' ? '#f43f5e' : entry.tier === 'MED' ? '#f59e0b' : '#10b981'}
                />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

      <div className="dashboard-grid cols-2-1">
        {/* Risk Table */}
        <div className="card">
          <div className="card-header">
            <div className="card-title"><Filter size={16} /> Risk Register</div>
            <select
              className="select-field"
              value={filterTier}
              onChange={e => setFilterTier(e.target.value)}
              id="risk-tier-filter"
            >
              <option value="ALL">All Tiers</option>
              <option value="HIGH">High Risk</option>
              <option value="MED">Medium Risk</option>
              <option value="LOW">Low Risk</option>
            </select>
          </div>
          <div className="data-table-wrap" style={{ maxHeight: 480, overflowY: 'auto' }}>
            <table className="data-table" id="risk-register-table">
              <thead>
                <tr>
                  <th>Medicine</th>
                  <th>Category</th>
                  <th>Tier</th>
                  <th>Score</th>
                  <th>Suppliers</th>
                  <th>China API</th>
                  <th>WHO</th>
                </tr>
              </thead>
              <tbody>
                {filtered.map(r => (
                  <tr
                    key={r.medicine_id}
                    style={{ cursor: 'pointer', background: selectedMed?.medicine_id === r.medicine_id ? 'rgba(139,92,246,0.06)' : undefined }}
                    onClick={() => setSelectedMed(r)}
                  >
                    <td style={{ color: 'var(--color-text-primary)', fontWeight: 500 }}>{r.medicine_name}</td>
                    <td>{r.category}</td>
                    <td><RiskBadge tier={r.risk_tier} /></td>
                    <td><RiskMeter score={r.composite_score} /></td>
                    <td className="mono text-center">{r.supplier_count}</td>
                    <td className="mono text-right">{r.china_api_pct}%</td>
                    <td className="text-center">{r.is_who_essential ? '✓' : '—'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Radar Breakdown */}
        <div className="card">
          <div className="card-header">
            <div className="card-title">Factor Breakdown</div>
          </div>
          {selectedMed ? (
            <>
              <div style={{ textAlign: 'center', marginBottom: 12 }}>
                <span style={{ fontWeight: 600, fontSize: 'var(--font-size-lg)' }}>{selectedMed.medicine_name}</span>
                <div style={{ marginTop: 4 }}><RiskBadge tier={selectedMed.risk_tier} /></div>
              </div>
              <ResponsiveContainer width="100%" height={260}>
                <RadarChart data={radarData} cx="50%" cy="50%" outerRadius="70%">
                  <PolarGrid stroke="rgba(139,92,246,0.15)" />
                  <PolarAngleAxis dataKey="factor" tick={{ fill: '#a3a1b2', fontSize: 12 }} />
                  <PolarRadiusAxis domain={[0, 100]} tick={false} axisLine={false} />
                  <Radar
                    dataKey="score"
                    stroke="#8b5cf6"
                    fill="#8b5cf6"
                    fillOpacity={0.2}
                    strokeWidth={2}
                  />
                </RadarChart>
              </ResponsiveContainer>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 8, padding: '0 8px' }}>
                {radarData.map(d => (
                  <div key={d.factor} style={{ display: 'flex', justifyContent: 'space-between', fontSize: 'var(--font-size-sm)', color: 'var(--color-text-secondary)' }}>
                    <span>{d.factor}</span>
                    <span className="mono font-semibold" style={{ color: d.score >= 65 ? 'var(--color-risk-high)' : d.score >= 35 ? 'var(--color-risk-med)' : 'var(--color-risk-low)' }}>
                      {d.score}
                    </span>
                  </div>
                ))}
              </div>
            </>
          ) : (
            <div className="empty-state" style={{ minHeight: 300 }}>
              <ShieldAlert size={48} />
              <p>Select a medicine from the table to view its risk factor breakdown</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
