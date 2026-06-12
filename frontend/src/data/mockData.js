/* 
  Mock data for MedChain Dashboard — realistic pharmaceutical supply chain data
  These are used as fallback when the backend API is unavailable.
*/

export const MOCK_MEDICINES = [
  { id: 1, name: 'Amoxicillin 500mg', generic_name: 'Amoxicillin', category: 'Antibiotic', is_who_essential: true, shelf_life_days: 730, unit: 'caps', current_stock_units: 12000, unit_cost_inr: 3.5, supplier_count: 2, china_api_pct: 72, lead_time_days: 21 },
  { id: 2, name: 'Metformin 500mg', generic_name: 'Metformin HCl', category: 'Antidiabetic', is_who_essential: true, shelf_life_days: 1095, unit: 'tabs', current_stock_units: 45000, unit_cost_inr: 1.2, supplier_count: 5, china_api_pct: 85, lead_time_days: 14 },
  { id: 3, name: 'Atorvastatin 10mg', generic_name: 'Atorvastatin Calcium', category: 'Cardiovascular', is_who_essential: true, shelf_life_days: 730, unit: 'tabs', current_stock_units: 8500, unit_cost_inr: 5.8, supplier_count: 3, china_api_pct: 68, lead_time_days: 18 },
  { id: 4, name: 'Pantoprazole 40mg', generic_name: 'Pantoprazole Sodium', category: 'Gastrointestinal', is_who_essential: false, shelf_life_days: 730, unit: 'tabs', current_stock_units: 22000, unit_cost_inr: 4.2, supplier_count: 4, china_api_pct: 45, lead_time_days: 12 },
  { id: 5, name: 'Ceftriaxone 1g', generic_name: 'Ceftriaxone Sodium', category: 'Antibiotic', is_who_essential: true, shelf_life_days: 365, unit: 'vials', current_stock_units: 3200, unit_cost_inr: 42.0, supplier_count: 1, china_api_pct: 91, lead_time_days: 28 },
  { id: 6, name: 'Amlodipine 5mg', generic_name: 'Amlodipine Besylate', category: 'Cardiovascular', is_who_essential: true, shelf_life_days: 1095, unit: 'tabs', current_stock_units: 35000, unit_cost_inr: 2.1, supplier_count: 6, china_api_pct: 78, lead_time_days: 10 },
  { id: 7, name: 'ORS Sachets', generic_name: 'Oral Rehydration Salts', category: 'Rehydration', is_who_essential: true, shelf_life_days: 365, unit: 'sachets', current_stock_units: 5000, unit_cost_inr: 8.5, supplier_count: 2, china_api_pct: 15, lead_time_days: 7 },
  { id: 8, name: 'Ciprofloxacin 500mg', generic_name: 'Ciprofloxacin HCl', category: 'Antibiotic', is_who_essential: true, shelf_life_days: 730, unit: 'tabs', current_stock_units: 9800, unit_cost_inr: 6.3, supplier_count: 3, china_api_pct: 82, lead_time_days: 16 },
  { id: 9, name: 'Insulin Glargine', generic_name: 'Insulin Glargine', category: 'Antidiabetic', is_who_essential: true, shelf_life_days: 180, unit: 'vials', current_stock_units: 450, unit_cost_inr: 385.0, supplier_count: 2, china_api_pct: 30, lead_time_days: 35 },
  { id: 10, name: 'Paracetamol 500mg', generic_name: 'Acetaminophen', category: 'Analgesic', is_who_essential: true, shelf_life_days: 1095, unit: 'tabs', current_stock_units: 120000, unit_cost_inr: 0.5, supplier_count: 8, china_api_pct: 55, lead_time_days: 7 },
  { id: 11, name: 'Azithromycin 250mg', generic_name: 'Azithromycin', category: 'Antibiotic', is_who_essential: true, shelf_life_days: 730, unit: 'tabs', current_stock_units: 6200, unit_cost_inr: 12.5, supplier_count: 2, china_api_pct: 88, lead_time_days: 21 },
  { id: 12, name: 'Phenytoin 100mg', generic_name: 'Phenytoin Sodium', category: 'Anticonvulsant', is_who_essential: true, shelf_life_days: 365, unit: 'tabs', current_stock_units: 2800, unit_cost_inr: 3.8, supplier_count: 1, china_api_pct: 65, lead_time_days: 25 },
];

/* ---------- Risk scores (pre-computed) ---------- */
function computeRisk(med) {
  const supplierMapping = { 1: 100, 2: 75, 3: 55, 4: 45, 5: 30, 6: 20, 7: 15 };
  const supplierScore = supplierMapping[med.supplier_count] ?? Math.max(5, 100 - med.supplier_count * 12);
  const apiScore = med.china_api_pct >= 70 ? Math.min(100, med.china_api_pct * 1.25) : med.china_api_pct;
  const shelfScore = med.shelf_life_days < 30 ? 90 : med.shelf_life_days < 90 ? 60 : med.shelf_life_days < 365 ? 30 : 10;
  const criticalCats = new Set(['Antibiotic', 'Antidiabetic', 'Cardiovascular', 'Rehydration', 'Anticonvulsant', 'Anticoagulant']);
  let critScore = med.is_who_essential ? 80 : 40;
  if (criticalCats.has(med.category)) critScore = Math.min(100, critScore * 1.15);

  const composite = supplierScore * 0.30 + apiScore * 0.30 + shelfScore * 0.15 + critScore * 0.25;
  const tier = composite >= 65 ? 'HIGH' : composite >= 35 ? 'MED' : 'LOW';
  
  const avgDaily = med.current_stock_units / (med.shelf_life_days * 0.15 + 30);
  const stockDays = avgDaily > 0 ? med.current_stock_units / avgDaily : 999;

  return {
    medicine_id: med.id,
    medicine_name: med.name,
    category: med.category,
    composite_score: Math.round(composite * 100) / 100,
    risk_tier: tier,
    supplier_score: Math.round(supplierScore * 100) / 100,
    api_dependency_score: Math.round(apiScore * 100) / 100,
    shelf_life_score: shelfScore,
    criticality_score: Math.round(critScore * 100) / 100,
    supplier_count: med.supplier_count,
    china_api_pct: med.china_api_pct,
    is_who_essential: med.is_who_essential,
    stock_days: Math.round(stockDays * 10) / 10,
  };
}

export const MOCK_RISK_SCORES = MOCK_MEDICINES
  .map(computeRisk)
  .sort((a, b) => b.composite_score - a.composite_score);

/* ---------- Stockout risk ---------- */
export const MOCK_STOCKOUT_RISK = [
  { medicine_id: 5, medicine_name: 'Ceftriaxone 1g', category: 'Antibiotic', avg_daily_demand: 85.2, current_stock: 3200, stock_days: 37.6, stockout_probability_pct: 82.4, horizon_days: 30 },
  { medicine_id: 9, medicine_name: 'Insulin Glargine', category: 'Antidiabetic', avg_daily_demand: 12.5, current_stock: 450, stock_days: 36.0, stockout_probability_pct: 78.1, horizon_days: 30 },
  { medicine_id: 12, medicine_name: 'Phenytoin 100mg', category: 'Anticonvulsant', avg_daily_demand: 45.8, current_stock: 2800, stock_days: 61.1, stockout_probability_pct: 54.2, horizon_days: 30 },
  { medicine_id: 7, medicine_name: 'ORS Sachets', category: 'Rehydration', avg_daily_demand: 92.3, current_stock: 5000, stock_days: 54.2, stockout_probability_pct: 45.8, horizon_days: 30 },
  { medicine_id: 1, medicine_name: 'Amoxicillin 500mg', category: 'Antibiotic', avg_daily_demand: 156.7, current_stock: 12000, stock_days: 76.6, stockout_probability_pct: 33.1, horizon_days: 30 },
  { medicine_id: 11, medicine_name: 'Azithromycin 250mg', category: 'Antibiotic', avg_daily_demand: 68.4, current_stock: 6200, stock_days: 90.6, stockout_probability_pct: 18.5, horizon_days: 30 },
  { medicine_id: 8, medicine_name: 'Ciprofloxacin 500mg', category: 'Antibiotic', avg_daily_demand: 72.1, current_stock: 9800, stock_days: 135.9, stockout_probability_pct: 8.2, horizon_days: 30 },
  { medicine_id: 3, medicine_name: 'Atorvastatin 10mg', category: 'Cardiovascular', avg_daily_demand: 95.0, current_stock: 8500, stock_days: 89.5, stockout_probability_pct: 12.3, horizon_days: 30 },
  { medicine_id: 4, medicine_name: 'Pantoprazole 40mg', category: 'Gastrointestinal', avg_daily_demand: 110.5, current_stock: 22000, stock_days: 199.1, stockout_probability_pct: 4.1, horizon_days: 30 },
  { medicine_id: 2, medicine_name: 'Metformin 500mg', category: 'Antidiabetic', avg_daily_demand: 220.3, current_stock: 45000, stock_days: 204.3, stockout_probability_pct: 3.5, horizon_days: 30 },
  { medicine_id: 6, medicine_name: 'Amlodipine 5mg', category: 'Cardiovascular', avg_daily_demand: 180.0, current_stock: 35000, stock_days: 194.4, stockout_probability_pct: 2.8, horizon_days: 30 },
  { medicine_id: 10, medicine_name: 'Paracetamol 500mg', category: 'Analgesic', avg_daily_demand: 450.0, current_stock: 120000, stock_days: 266.7, stockout_probability_pct: 0.6, horizon_days: 30 },
];

/* ---------- Reorder recommendations ---------- */
export const MOCK_REORDER = [
  { medicine_id: 5, medicine_name: 'Ceftriaxone 1g', urgency: 'URGENT', horizon_days: 30, current_stock: 3200, days_of_stock: 37.6, safety_stock: 680, reorder_point: 3062, recommended_qty: 4500, estimated_cost_inr: 189000, avg_daily_demand: 85.2, lead_time_days: 28, suggested_supplier: null },
  { medicine_id: 9, medicine_name: 'Insulin Glargine', urgency: 'URGENT', horizon_days: 30, current_stock: 450, days_of_stock: 36.0, safety_stock: 95, reorder_point: 533, recommended_qty: 800, estimated_cost_inr: 308000, avg_daily_demand: 12.5, lead_time_days: 35, suggested_supplier: null },
  { medicine_id: 12, medicine_name: 'Phenytoin 100mg', urgency: 'WARNING', horizon_days: 60, current_stock: 2800, days_of_stock: 61.1, safety_stock: 420, reorder_point: 1565, recommended_qty: 5200, estimated_cost_inr: 19760, avg_daily_demand: 45.8, lead_time_days: 25, suggested_supplier: null },
  { medicine_id: 7, medicine_name: 'ORS Sachets', urgency: 'WARNING', horizon_days: 60, current_stock: 5000, days_of_stock: 54.2, safety_stock: 350, reorder_point: 996, recommended_qty: 8000, estimated_cost_inr: 68000, avg_daily_demand: 92.3, lead_time_days: 7, suggested_supplier: null },
  { medicine_id: 1, medicine_name: 'Amoxicillin 500mg', urgency: 'WARNING', horizon_days: 60, current_stock: 12000, days_of_stock: 76.6, safety_stock: 1250, reorder_point: 4541, recommended_qty: 18000, estimated_cost_inr: 63000, avg_daily_demand: 156.7, lead_time_days: 21, suggested_supplier: null },
];

/* ---------- Consumption trend (30 days for spark charts) ---------- */
export const MOCK_CONSUMPTION_TREND = Array.from({ length: 30 }, (_, i) => {
  const d = new Date();
  d.setDate(d.getDate() - (29 - i));
  return {
    date: d.toISOString().slice(0, 10),
    total_units: Math.round(1800 + Math.sin(i / 5) * 300 + Math.random() * 200),
    antibiotic: Math.round(420 + Math.sin(i / 4) * 80 + Math.random() * 50),
    cardiovascular: Math.round(350 + Math.cos(i / 6) * 50 + Math.random() * 40),
    antidiabetic: Math.round(280 + Math.sin(i / 3) * 40 + Math.random() * 30),
    other: Math.round(750 + Math.cos(i / 5) * 130 + Math.random() * 80),
  };
});

/* ---------- Category distribution ---------- */
export const MOCK_CATEGORY_DIST = [
  { category: 'Antibiotic', count: 4, total_stock: 31200, risk_avg: 72.3 },
  { category: 'Cardiovascular', count: 2, total_stock: 43500, risk_avg: 51.8 },
  { category: 'Antidiabetic', count: 2, total_stock: 45450, risk_avg: 58.4 },
  { category: 'Gastrointestinal', count: 1, total_stock: 22000, risk_avg: 32.1 },
  { category: 'Rehydration', count: 1, total_stock: 5000, risk_avg: 55.2 },
  { category: 'Analgesic', count: 1, total_stock: 120000, risk_avg: 18.6 },
  { category: 'Anticonvulsant', count: 1, total_stock: 2800, risk_avg: 68.9 },
];

/* ---------- Forecast data (for a single medicine) ---------- */
export function generateMockForecast(medicineId, horizonDays = 90) {
  const med = MOCK_MEDICINES.find(m => m.id === medicineId) || MOCK_MEDICINES[0];
  const baseDaily = med.current_stock_units / 150;
  const points = [];
  for (let i = 0; i < horizonDays; i++) {
    const d = new Date();
    d.setDate(d.getDate() + i);
    const seasonal = Math.sin((d.getMonth() + i / 30) * Math.PI / 6) * baseDaily * 0.15;
    const trend = baseDaily * (1 + i * 0.001);
    const predicted = Math.round(trend + seasonal + (Math.random() - 0.5) * baseDaily * 0.2);
    points.push({
      forecast_date: d.toISOString().slice(0, 10),
      predicted_units: Math.max(1, predicted),
      upper_ci: Math.round(predicted * 1.2),
      lower_ci: Math.round(predicted * 0.8),
    });
  }
  return {
    medicine_id: medicineId,
    medicine_name: med.name,
    category: med.category,
    horizon_days: horizonDays,
    model_mape: Math.round((8 + Math.random() * 7) * 100) / 100,
    forecasts: points,
  };
}
