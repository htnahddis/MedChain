import { useState, useEffect, useCallback } from 'react';
import * as api from '../services/api';
import {
  MOCK_MEDICINES,
  MOCK_RISK_SCORES,
  MOCK_STOCKOUT_RISK,
  MOCK_REORDER,
  MOCK_CONSUMPTION_TREND,
  generateMockForecast,
} from '../data/mockData';

/**
 * Generic hook for fetching API data with mock fallback.
 * Tries the live backend first; falls back to mock data on failure.
 */
function useApiData(apiFn, mockData, deps = []) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isLive, setIsLive] = useState(false);

  const refetch = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await apiFn();
      setData(result);
      setIsLive(true);
    } catch {
      // Fallback to mock data
      setData(mockData);
      setIsLive(false);
    } finally {
      setLoading(false);
    }
  }, deps);

  useEffect(() => { refetch(); }, [refetch]);

  return { data, loading, error, isLive, refetch };
}

export function useMedicines() {
  return useApiData(() => api.getMedicines(), MOCK_MEDICINES);
}

export function useRiskScores() {
  return useApiData(() => api.getRiskScores(), MOCK_RISK_SCORES);
}

export function useStockoutRisk(horizon = 30) {
  return useApiData(
    () => api.getStockoutRisk(horizon),
    MOCK_STOCKOUT_RISK,
    [horizon]
  );
}

export function useReorderRecommendations() {
  return useApiData(() => api.getReorderRecommendations(), MOCK_REORDER);
}

export function useConsumptionTrend() {
  return useApiData(async () => MOCK_CONSUMPTION_TREND, MOCK_CONSUMPTION_TREND);
}

export function useForecast(medicineId, horizon = 90) {
  return useApiData(
    () => api.getForecast(medicineId, horizon),
    generateMockForecast(medicineId, horizon),
    [medicineId, horizon]
  );
}
