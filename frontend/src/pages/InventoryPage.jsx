import { useMemo, useState } from 'react';
import { Pill, Search, ChevronDown, ChevronUp } from 'lucide-react';
import { useMedicines, useRiskScores } from '../hooks/useData';
import { RiskBadge, LoadingState, formatNumber, formatINR } from '../components/ui';

export default function InventoryPage() {
  const { data: medicines, loading: loadingMeds } = useMedicines();
  const { data: riskScores, loading: loadingRisk } = useRiskScores();
  const [search, setSearch] = useState('');
  const [sortCol, setSortCol] = useState('name');
  const [sortDir, setSortDir] = useState('asc');

  const riskMap = useMemo(() => {
    if (!riskScores) return {};
    const map = {};
    riskScores.forEach(r => { map[r.medicine_id] = r; });
    return map;
  }, [riskScores]);

  const enriched = useMemo(() => {
    if (!medicines) return [];
    return medicines
      .map(m => ({
        ...m,
        risk: riskMap[m.id] || null,
      }))
      .filter(m =>
        m.name.toLowerCase().includes(search.toLowerCase()) ||
        m.category.toLowerCase().includes(search.toLowerCase()) ||
        (m.generic_name || '').toLowerCase().includes(search.toLowerCase())
      );
  }, [medicines, riskMap, search]);

  const sorted = useMemo(() => {
    return [...enriched].sort((a, b) => {
      let va, vb;
      switch (sortCol) {
        case 'name': va = a.name; vb = b.name; break;
        case 'category': va = a.category; vb = b.category; break;
        case 'stock': va = a.current_stock_units; vb = b.current_stock_units; break;
        case 'cost': va = a.unit_cost_inr; vb = b.unit_cost_inr; break;
        case 'risk': va = a.risk?.composite_score || 0; vb = b.risk?.composite_score || 0; break;
        case 'suppliers': va = a.supplier_count; vb = b.supplier_count; break;
        default: va = a.name; vb = b.name;
      }
      if (typeof va === 'string') {
        return sortDir === 'asc' ? va.localeCompare(vb) : vb.localeCompare(va);
      }
      return sortDir === 'asc' ? va - vb : vb - va;
    });
  }, [enriched, sortCol, sortDir]);

  const handleSort = (col) => {
    if (sortCol === col) {
      setSortDir(d => d === 'asc' ? 'desc' : 'asc');
    } else {
      setSortCol(col);
      setSortDir('asc');
    }
  };

  const SortIcon = ({ col }) => {
    if (sortCol !== col) return null;
    return sortDir === 'asc' ? <ChevronUp size={12} /> : <ChevronDown size={12} />;
  };

  if (loadingMeds || loadingRisk) return <div className="main-content"><LoadingState /></div>;

  return (
    <div className="main-content animate-in">
      <div className="page-header">
        <div className="page-header-row">
          <div>
            <h1>Inventory</h1>
            <p>Complete medicine inventory with risk overlays</p>
          </div>
          <div style={{ position: 'relative' }}>
            <Search size={14} style={{ position: 'absolute', left: 12, top: '50%', transform: 'translateY(-50%)', color: 'var(--color-text-tertiary)' }} />
            <input
              type="text"
              className="ai-panel-input"
              style={{ paddingLeft: 32, width: 260 }}
              placeholder="Search medicines…"
              value={search}
              onChange={e => setSearch(e.target.value)}
              id="inventory-search"
            />
          </div>
        </div>
      </div>

      <div className="card">
        <div className="card-header">
          <div className="card-title"><Pill size={16} /> {sorted.length} Medicines</div>
        </div>
        <div className="data-table-wrap">
          <table className="data-table" id="inventory-table">
            <thead>
              <tr>
                <th style={{ cursor: 'pointer' }} onClick={() => handleSort('name')}>
                  Name <SortIcon col="name" />
                </th>
                <th style={{ cursor: 'pointer' }} onClick={() => handleSort('category')}>
                  Category <SortIcon col="category" />
                </th>
                <th>WHO</th>
                <th style={{ cursor: 'pointer', textAlign: 'right' }} onClick={() => handleSort('stock')}>
                  Stock <SortIcon col="stock" />
                </th>
                <th>Unit</th>
                <th style={{ cursor: 'pointer', textAlign: 'right' }} onClick={() => handleSort('cost')}>
                  Unit Cost <SortIcon col="cost" />
                </th>
                <th style={{ cursor: 'pointer', textAlign: 'right' }} onClick={() => handleSort('suppliers')}>
                  Suppliers <SortIcon col="suppliers" />
                </th>
                <th style={{ textAlign: 'right' }}>China API</th>
                <th style={{ textAlign: 'right' }}>Lead Time</th>
                <th style={{ cursor: 'pointer' }} onClick={() => handleSort('risk')}>
                  Risk <SortIcon col="risk" />
                </th>
              </tr>
            </thead>
            <tbody>
              {sorted.map(m => (
                <tr key={m.id}>
                  <td style={{ color: 'var(--color-text-primary)', fontWeight: 500 }}>{m.name}</td>
                  <td>{m.category}</td>
                  <td className="text-center">{m.is_who_essential ? '✓' : '—'}</td>
                  <td className="mono text-right">{formatNumber(m.current_stock_units)}</td>
                  <td className="text-center" style={{ fontSize: 'var(--font-size-xs)', color: 'var(--color-text-tertiary)' }}>{m.unit}</td>
                  <td className="mono text-right">₹{m.unit_cost_inr}</td>
                  <td className="mono text-center">{m.supplier_count}</td>
                  <td className="mono text-right">{m.china_api_pct}%</td>
                  <td className="mono text-right">{m.lead_time_days}d</td>
                  <td>{m.risk ? <RiskBadge tier={m.risk.risk_tier} /> : '—'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
