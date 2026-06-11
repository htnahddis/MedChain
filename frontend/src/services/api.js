/* API service for MedChain backend */

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

async function fetchJSON(url, options = {}) {
  const res = await fetch(`${API_BASE}${url}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  });
  if (!res.ok) {
    throw new Error(`API Error ${res.status}: ${res.statusText}`);
  }
  return res.json();
}

/* ---- Medicines ---- */
export const getMedicines = () => fetchJSON('/api/medicines/');
export const getMedicine = (id) => fetchJSON(`/api/medicines/${id}`);
export const getRiskScores = () => fetchJSON('/api/medicines/risk-scores/all');

/* ---- Forecast ---- */
export const getForecast = (medicineId, horizon = 90) =>
  fetchJSON(`/api/forecast/${medicineId}?horizon_days=${horizon}`);
export const getStockoutRisk = (horizon = 30) =>
  fetchJSON(`/api/forecast/stockout-risk/all?horizon=${horizon}`);

/* ---- Reorder ---- */
export const getReorderRecommendations = () =>
  fetchJSON('/api/reorder/recommendations');

/* ---- AI Insights ---- */
export const getAIInsight = (question, dashboardContext) =>
  fetchJSON('/ai-insights/', {
    method: 'POST',
    body: JSON.stringify({
      question,
      dashboard_context: dashboardContext,
    }),
  });
