# backend/app/models/medicine.py
from sqlalchemy import Column, Integer, String, Boolean, Float, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class Medicine(Base):
    __tablename__ = "medicines"

    id                  = Column(Integer, primary_key=True, index=True)
    name                = Column(String(200), nullable=False, index=True)
    generic_name        = Column(String(200))
    category            = Column(String(100), index=True)
    is_who_essential    = Column(Boolean, default=False)
    shelf_life_days     = Column(Integer, default=365)
    unit                = Column(String(50), default="tabs")  # tabs/sachets/vials/caps
    current_stock_units = Column(Integer, default=0)
    unit_cost_inr       = Column(Float, default=10.0)
    supplier_count      = Column(Integer, default=1)
    china_api_pct       = Column(Float, default=0.0)   # % API from China
    lead_time_days      = Column(Integer, default=14)
    reorder_point       = Column(Integer, default=0)
    notes               = Column(Text, nullable=True)
    created_at          = Column(DateTime(timezone=True), server_default=func.now())
    updated_at          = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    consumption_records     = relationship("ConsumptionRecord", back_populates="medicine")
    risk_scores             = relationship("RiskScore", back_populates="medicine")
    forecasts               = relationship("Forecast", back_populates="medicine")
    reorder_recommendations = relationship("ReorderRecommendation", back_populates="medicine")
    medicine_suppliers      = relationship("MedicineSupplier", back_populates="medicine")