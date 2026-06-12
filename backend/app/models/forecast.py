<<<<<<< HEAD
# backend/app/models/forecast.py
from sqlalchemy import Column, Integer, String, Float, Date, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class Forecast(Base):
    __tablename__ = "forecasts"

    id              = Column(Integer, primary_key=True, index=True)
    medicine_id     = Column(Integer, ForeignKey("medicines.id"), nullable=False, index=True)
    forecast_date   = Column(Date, nullable=False)
    target_date     = Column(Date, nullable=False)
    predicted_units = Column(Integer)
    upper_ci        = Column(Integer)
    lower_ci        = Column(Integer)
    model_used      = Column(String(50), default="prophet")
    mape            = Column(Float, nullable=True)
    created_at      = Column(DateTime(timezone=True), server_default=func.now())

=======
# backend/app/models/forecast.py
from sqlalchemy import Column, Integer, String, Float, Date, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class Forecast(Base):
    __tablename__ = "forecasts"

    id              = Column(Integer, primary_key=True, index=True)
    medicine_id     = Column(Integer, ForeignKey("medicines.id"), nullable=False, index=True)
    forecast_date   = Column(Date, nullable=False)
    target_date     = Column(Date, nullable=False)
    predicted_units = Column(Integer)
    upper_ci        = Column(Integer)
    lower_ci        = Column(Integer)
    model_used      = Column(String(50), default="prophet")
    mape            = Column(Float, nullable=True)
    created_at      = Column(DateTime(timezone=True), server_default=func.now())

>>>>>>> another_branch_soham
    medicine        = relationship("Medicine", back_populates="forecasts")