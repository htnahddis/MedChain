<<<<<<< HEAD
# backend/app/models/supplier.py
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class Supplier(Base):
    __tablename__ = "suppliers"

    id                  = Column(Integer, primary_key=True, index=True)
    name                = Column(String(200), nullable=False)
    country             = Column(String(100), default="India")
    reliability_score   = Column(Float, default=70.0)   # 0-100
    lead_time_days      = Column(Integer, default=14)
    contact_email       = Column(String(200), nullable=True)
    specialties         = Column(String(500), nullable=True)
    is_active           = Column(Boolean, default=True)
    created_at          = Column(DateTime(timezone=True), server_default=func.now())

    medicine_suppliers  = relationship("MedicineSupplier", back_populates="supplier")


class MedicineSupplier(Base):
    __tablename__ = "medicine_suppliers"

    id              = Column(Integer, primary_key=True, index=True)
    medicine_id     = Column(Integer, ForeignKey("medicines.id"), nullable=False)
    supplier_id     = Column(Integer, ForeignKey("suppliers.id"), nullable=False)
    china_api_pct   = Column(Float, default=0.0)
    is_primary      = Column(Boolean, default=False)
    created_at      = Column(DateTime(timezone=True), server_default=func.now())

    medicine        = relationship("Medicine", back_populates="medicine_suppliers")
=======
# backend/app/models/supplier.py
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class Supplier(Base):
    __tablename__ = "suppliers"

    id                  = Column(Integer, primary_key=True, index=True)
    name                = Column(String(200), nullable=False)
    country             = Column(String(100), default="India")
    reliability_score   = Column(Float, default=70.0)   # 0-100
    lead_time_days      = Column(Integer, default=14)
    contact_email       = Column(String(200), nullable=True)
    specialties         = Column(String(500), nullable=True)
    is_active           = Column(Boolean, default=True)
    created_at          = Column(DateTime(timezone=True), server_default=func.now())

    medicine_suppliers  = relationship("MedicineSupplier", back_populates="supplier")


class MedicineSupplier(Base):
    __tablename__ = "medicine_suppliers"

    id              = Column(Integer, primary_key=True, index=True)
    medicine_id     = Column(Integer, ForeignKey("medicines.id"), nullable=False)
    supplier_id     = Column(Integer, ForeignKey("suppliers.id"), nullable=False)
    china_api_pct   = Column(Float, default=0.0)
    is_primary      = Column(Boolean, default=False)
    created_at      = Column(DateTime(timezone=True), server_default=func.now())

    medicine        = relationship("Medicine", back_populates="medicine_suppliers")
>>>>>>> another_branch_soham
    supplier        = relationship("Supplier", back_populates="medicine_suppliers")