<<<<<<< HEAD
# backend/app/schemas/forecast.py
from pydantic import BaseModel
from typing import List, Optional
from datetime import date

class ForecastPoint(BaseModel):
    forecast_date: date
    predicted_units: int
    upper_ci: int
    lower_ci: int

class ForecastResponse(BaseModel):
    medicine_id: int
    medicine_name: str
    category: str
    horizon_days: int
    model_mape: Optional[float] = None
    avg_daily_demand: Optional[float] = None
    forecasts: List[dict]

class StockoutRiskItem(BaseModel):
    medicine_id: int
    medicine_name: str
    category: str
    avg_daily_demand: float
    current_stock: int
    stock_days: float
    stockout_probability_pct: float
    horizon_days: int
    risk_tier: str

class ReorderItem(BaseModel):
    medicine_id: int
    medicine_name: str
    urgency: str
    horizon_days: int
    current_stock: int
    days_of_stock: float
    safety_stock: int
    reorder_point: int
    recommended_qty: int
    estimated_cost_inr: float
    avg_daily_demand: float
    lead_time_days: int
=======
# backend/app/schemas/forecast.py
from pydantic import BaseModel
from typing import List, Optional
from datetime import date

class ForecastPoint(BaseModel):
    forecast_date: date
    predicted_units: int
    upper_ci: int
    lower_ci: int

class ForecastResponse(BaseModel):
    medicine_id: int
    medicine_name: str
    category: str
    horizon_days: int
    model_mape: Optional[float] = None
    avg_daily_demand: Optional[float] = None
    forecasts: List[dict]

class StockoutRiskItem(BaseModel):
    medicine_id: int
    medicine_name: str
    category: str
    avg_daily_demand: float
    current_stock: int
    stock_days: float
    stockout_probability_pct: float
    horizon_days: int
    risk_tier: str

class ReorderItem(BaseModel):
    medicine_id: int
    medicine_name: str
    urgency: str
    horizon_days: int
    current_stock: int
    days_of_stock: float
    safety_stock: int
    reorder_point: int
    recommended_qty: int
    estimated_cost_inr: float
    avg_daily_demand: float
    lead_time_days: int
>>>>>>> another_branch_soham
    suggested_supplier: Optional[str] = None