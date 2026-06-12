<<<<<<< HEAD
# backend/app/models/reorder.py
from sqlalchemy import Column, Integer, String, Float, Boolean, Date, DateTime, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class ReorderRecommendation(Base):
    __tablename__ = "reorder_recommendations"

    id                      = Column(Integer, primary_key=True, index=True)
    medicine_id             = Column(Integer, ForeignKey("medicines.id"), nullable=False, index=True)
    recommended_date        = Column(Date, nullable=False)
    order_quantity          = Column(Integer)
    estimated_cost_inr      = Column(Numeric(12, 2))
    urgency                 = Column(String(20))   # URGENT / WARNING / MONITOR
    horizon_days            = Column(Integer)       # 30 / 60 / 90
    suggested_supplier_id   = Column(Integer, ForeignKey("suppliers.id"), nullable=True)
    safety_stock            = Column(Integer, default=0)
    reorder_point           = Column(Integer, default=0)
    avg_daily_demand        = Column(Float, default=0.0)
    is_actioned             = Column(Boolean, default=False)
    created_at              = Column(DateTime(timezone=True), server_default=func.now())

=======
# backend/app/models/reorder.py
from sqlalchemy import Column, Integer, String, Float, Boolean, Date, DateTime, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class ReorderRecommendation(Base):
    __tablename__ = "reorder_recommendations"

    id                      = Column(Integer, primary_key=True, index=True)
    medicine_id             = Column(Integer, ForeignKey("medicines.id"), nullable=False, index=True)
    recommended_date        = Column(Date, nullable=False)
    order_quantity          = Column(Integer)
    estimated_cost_inr      = Column(Numeric(12, 2))
    urgency                 = Column(String(20))   # URGENT / WARNING / MONITOR
    horizon_days            = Column(Integer)       # 30 / 60 / 90
    suggested_supplier_id   = Column(Integer, ForeignKey("suppliers.id"), nullable=True)
    safety_stock            = Column(Integer, default=0)
    reorder_point           = Column(Integer, default=0)
    avg_daily_demand        = Column(Float, default=0.0)
    is_actioned             = Column(Boolean, default=False)
    created_at              = Column(DateTime(timezone=True), server_default=func.now())

>>>>>>> another_branch_soham
    medicine                = relationship("Medicine", back_populates="reorder_recommendations")