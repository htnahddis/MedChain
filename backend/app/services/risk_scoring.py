
import numpy as np
import pandas as pd
from typing import Dict, List
from app.config import settings


class RiskScorer:
    """
    Composite risk index for medicine supply chain disruption.
    
    Formula:
        Composite Score = (supplier_score × 0.30)
                        + (api_dependency_score × 0.30)
                        + (shelf_life_score × 0.15)
                        + (criticality_score × 0.25)
    
    Score range: 0-100 (higher = more risk)
    Tiers: HIGH ≥ 65 | MEDIUM 35-64 | LOW < 35
    """

    TIER_HIGH = 65
    TIER_MED = 35

    def score_supplier_concentration(self, supplier_count: int) -> float:
        """
        Fewer suppliers = higher risk.
        1 supplier → 100 risk | 2 → 75 | 3-4 → 50 | 5+ → 25 | 8+ → 10
        """
        mapping = {1: 100, 2: 75, 3: 55, 4: 45, 5: 30, 6: 20, 7: 15}
        return float(mapping.get(supplier_count, max(5, 100 - (supplier_count * 12))))

    def score_api_dependency(self, china_api_pct: float) -> float:
        """
        Linear mapping: 100% China API → 100 risk | 0% → 0 risk.
        Applies a steep multiplier above 70% (geopolitical risk threshold).
        """
        if china_api_pct >= 70:
            return min(100.0, china_api_pct * 1.25)
        return china_api_pct

    def score_shelf_life(self, shelf_life_days: int) -> float:
        """
        Short shelf life medicines require more frequent ordering → higher operational risk.
        < 30 days → 90 risk | 30-90 → 60 | 90-365 → 30 | > 365 → 10
        """
        if shelf_life_days < 30:
            return 90.0
        elif shelf_life_days < 90:
            return 60.0
        elif shelf_life_days < 365:
            return 30.0
        return 10.0

    def score_criticality(self, is_who_essential: bool, category: str) -> float:
        """
        WHO essential list medicines get higher criticality weight.
        Life-saving categories (antibiotics, antidiabetics, cardiovascular) amplified.
        """
        base = 80.0 if is_who_essential else 40.0
        critical_categories = {'Antibiotic', 'Antidiabetic', 'Cardiovascular', 
                               'Rehydration', 'Anticonvulsant', 'Anticoagulant'}
        if category in critical_categories:
            base = min(100.0, base * 1.15)
        return base

    def compute_composite(self, medicine_data: Dict) -> Dict:
        """
        Full risk scoring pipeline for a single medicine.
        Returns composite score, tier, and component breakdown.
        """
        s_supplier  = self.score_supplier_concentration(medicine_data['supplier_count'])
        s_api       = self.score_api_dependency(medicine_data['china_api_pct'])
        s_shelf     = self.score_shelf_life(medicine_data['shelf_life_days'])
        s_critical  = self.score_criticality(
            medicine_data['is_who_essential'], 
            medicine_data['category']
        )

        w = settings
        composite = (
            s_supplier  * w.WEIGHT_SUPPLIER_COUNT +
            s_api       * w.WEIGHT_API_DEPENDENCY +
            s_shelf     * w.WEIGHT_SHELF_LIFE +
            s_critical  * w.WEIGHT_WHO_CRITICALITY
        )

        tier = 'HIGH' if composite >= self.TIER_HIGH else \
               'MED'  if composite >= self.TIER_MED  else 'LOW'

        return {
            'composite_score':    round(composite, 2),
            'risk_tier':          tier,
            'supplier_score':     round(s_supplier, 2),
            'api_dependency_score': round(s_api, 2),
            'shelf_life_score':   round(s_shelf, 2),
            'criticality_score':  round(s_critical, 2),
        }

    def score_all(self, medicines: List[Dict]) -> pd.DataFrame:
        """Batch-scores all medicines and returns a sorted DataFrame."""
        results = [{'name': m['name'], **self.compute_composite(m)} for m in medicines]
        df = pd.DataFrame(results).sort_values('composite_score', ascending=False)
        return df