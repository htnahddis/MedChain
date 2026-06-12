<<<<<<< HEAD
# backend/app/models/consumption.py
from sqlalchemy import Column, Integer, String, Boolean, Date, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class ConsumptionRecord(Base):
    __tablename__ = "consumption_records"

    id              = Column(Integer, primary_key=True, index=True)
    medicine_id     = Column(Integer, ForeignKey("medicines.id"), nullable=False, index=True)
    date            = Column(Date, nullable=False, index=True)
    units_consumed  = Column(Integer, nullable=False)
    facility_type   = Column(String(100), default="500-bed")
    is_synthetic    = Column(Boolean, default=True)
    created_at      = Column(DateTime(timezone=True), server_default=func.now())

=======
# backend/app/models/consumption.py
from sqlalchemy import Column, Integer, String, Boolean, Date, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class ConsumptionRecord(Base):
    __tablename__ = "consumption_records"

    id              = Column(Integer, primary_key=True, index=True)
    medicine_id     = Column(Integer, ForeignKey("medicines.id"), nullable=False, index=True)
    date            = Column(Date, nullable=False, index=True)
    units_consumed  = Column(Integer, nullable=False)
    facility_type   = Column(String(100), default="500-bed")
    is_synthetic    = Column(Boolean, default=True)
    created_at      = Column(DateTime(timezone=True), server_default=func.now())

>>>>>>> another_branch_soham
    medicine        = relationship("Medicine", back_populates="consumption_records")