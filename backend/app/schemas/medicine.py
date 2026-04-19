# backend/app/schemas/medicine.py
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class MedicineBase(BaseModel):
    name: str
    generic_name: Optional[str] = None
    category: str
    is_who_essential: bool = False
    shelf_life_days: int = 365
    unit: str = "tabs"
    current_stock_units: int = 0
    unit_cost_inr: float = 10.0
    supplier_count: int = 1
    china_api_pct: float = 0.0
    lead_time_days: int = 14

class MedicineCreate(MedicineBase):
    pass

class MedicineResponse(MedicineBase):
    id: int
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class RiskScoreResponse(BaseModel):
    medicine_id: int
    medicine_name: str
    category: str
    composite_score: float
    risk_tier: str
    supplier_score: float
    api_dependency_score: float
    shelf_life_score: float
    criticality_score: float
    supplier_count: int
    china_api_pct: float
    is_who_essential: bool
    stock_days: Optional[float] = None

    class Config:
        from_attributes = True