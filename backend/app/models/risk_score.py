# backend/app/models/risk_score.py
from sqlalchemy import Column, Integer, String, Float, Date, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class RiskScore(Base):
    __tablename__ = "risk_scores"

    id                  = Column(Integer, primary_key=True, index=True)
    medicine_id         = Column(Integer, ForeignKey("medicines.id"), nullable=False, index=True)
    score_date          = Column(Date, nullable=False, index=True)
    supplier_score      = Column(Float)
    api_dependency_score= Column(Float)
    shelf_life_score    = Column(Float)
    criticality_score   = Column(Float)
    composite_score     = Column(Float, index=True)
    risk_tier           = Column(String(10))   # HIGH / MED / LOW
    created_at          = Column(DateTime(timezone=True), server_default=func.now())

    medicine            = relationship("Medicine", back_populates="risk_scores")