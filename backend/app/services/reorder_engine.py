import numpy as np
from scipy.stats import norm
from typing import Dict, Optional
from app.config import settings


class ReorderEngine:
    """
    Statistical safety stock + EOQ-based reorder recommendation engine.
    
    Follows standard inventory management formulae:
    - Safety Stock:   SS = Z × σ_demand × √(Lead Time)  
    - Reorder Point:  ROP = (Avg Daily Demand × Lead Time) + Safety Stock
    - EOQ:            √(2 × Annual Demand × Order Cost / Holding Cost)
    - Days of Stock:  Current Inventory / Avg Daily Demand
    """

    def __init__(self, service_level: float = 0.95):
        self.z_score = norm.ppf(service_level)  # 1.645 for 95%

    def compute_safety_stock(
        self,
        avg_daily_demand: float,
        demand_std: float,
        lead_time_days: int,
        lead_time_std: float = 0.0
    ) -> int:
        """
        Safety stock accounts for both demand variability and lead time variability.
        """
        demand_uncertainty = (demand_std ** 2) * lead_time_days
        lead_time_uncertainty = (lead_time_std ** 2) * (avg_daily_demand ** 2)
        safety_stock = self.z_score * np.sqrt(demand_uncertainty + lead_time_uncertainty)
        return max(0, int(np.ceil(safety_stock)))

    def compute_reorder_point(
        self,
        avg_daily_demand: float,
        lead_time_days: int,
        safety_stock: int
    ) -> int:
        return int(np.ceil(avg_daily_demand * lead_time_days)) + safety_stock

    def compute_eoq(
        self,
        annual_demand: float,
        order_cost: float,
        unit_cost: float,
        holding_cost_pct: float = 0.20
    ) -> int:
        """Economic Order Quantity — optimal order size balancing order vs holding costs."""
        holding_cost = unit_cost * holding_cost_pct
        if holding_cost <= 0 or annual_demand <= 0:
            return int(annual_demand / 4)  # Fallback: quarterly order
        eoq = np.sqrt((2 * annual_demand * order_cost) / holding_cost)
        return max(100, int(np.ceil(eoq)))

    def generate_recommendation(self, medicine: Dict, forecast: Dict) -> Dict:
        """
        Full reorder recommendation for a single medicine.
        
        Args:
            medicine: Dict with inventory and cost data
            forecast: Dict with Prophet forecast outputs
        
        Returns:
            Recommendation dict with quantity, cost, urgency, horizon
        """
        avg_daily = forecast['avg_daily_demand']
        std_daily = forecast.get('std_daily_demand', avg_daily * 0.15)
        lead_time = medicine.get('lead_time_days', 14)
        current_stock = medicine.get('current_stock_units', 0)
        unit_cost = medicine.get('unit_cost', 10.0)
        order_cost = 500.0  # Fixed order processing cost (₹)

        ss = self.compute_safety_stock(avg_daily, std_daily, lead_time)
        rop = self.compute_reorder_point(avg_daily, lead_time, ss)
        eoq = self.compute_eoq(avg_daily * 365, order_cost, unit_cost)

        days_of_stock = current_stock / avg_daily if avg_daily > 0 else 999

        # Urgency classification
        if days_of_stock <= 30:
            urgency = 'URGENT'
            horizon = 30
        elif days_of_stock <= 60:
            urgency = 'WARNING'
            horizon = 60
        else:
            urgency = 'MONITOR'
            horizon = 90

        estimated_cost = eoq * unit_cost

        return {
            'medicine_id':       medicine['id'],
            'medicine_name':     medicine['name'],
            'urgency':           urgency,
            'horizon_days':      horizon,
            'current_stock':     current_stock,
            'days_of_stock':     round(days_of_stock, 1),
            'safety_stock':      ss,
            'reorder_point':     rop,
            'recommended_qty':   eoq,
            'estimated_cost_inr': round(estimated_cost, 2),
            'avg_daily_demand':  round(avg_daily, 1),
            'lead_time_days':    lead_time,
        }