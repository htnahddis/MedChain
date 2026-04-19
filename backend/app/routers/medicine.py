# backend/app/routers/medicines.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.medicine import Medicine
from app.schemas.medicine import MedicineCreate, MedicineResponse, RiskScoreResponse
from app.services.risk_scoring import RiskScorer
import math

router = APIRouter(prefix="/api/medicines", tags=["Medicines"])

@router.get("/", response_model=List[MedicineResponse])
def list_medicines(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(Medicine).offset(skip).limit(limit).all()

@router.get("/{medicine_id}", response_model=MedicineResponse)
def get_medicine(medicine_id: int, db: Session = Depends(get_db)):
    med = db.query(Medicine).filter(Medicine.id == medicine_id).first()
    if not med:
        raise HTTPException(status_code=404, detail="Medicine not found")
    return med

@router.post("/", response_model=MedicineResponse, status_code=201)
def create_medicine(medicine: MedicineCreate, db: Session = Depends(get_db)):
    db_med = Medicine(**medicine.model_dump())
    db.add(db_med)
    db.commit()
    db.refresh(db_med)
    return db_med

@router.get("/risk-scores/all", response_model=List[RiskScoreResponse])
def get_all_risk_scores(db: Session = Depends(get_db)):
    """Compute and return risk scores for all medicines."""
    scorer = RiskScorer()
    medicines = db.query(Medicine).all()
    results = []
    for med in medicines:
        data = {
            'supplier_count': med.supplier_count,
            'china_api_pct': med.china_api_pct,
            'shelf_life_days': med.shelf_life_days,
            'is_who_essential': med.is_who_essential,
            'category': med.category,
        }
        score = scorer.compute_composite(data)
        avg_daily = _get_avg_daily(med, db)
        stock_days = (med.current_stock_units / avg_daily) if avg_daily > 0 else 999
        results.append(RiskScoreResponse(
            medicine_id=med.id,
            medicine_name=med.name,
            category=med.category,
            composite_score=score['composite_score'],
            risk_tier=score['risk_tier'],
            supplier_score=score['supplier_score'],
            api_dependency_score=score['api_dependency_score'],
            shelf_life_score=score['shelf_life_score'],
            criticality_score=score['criticality_score'],
            supplier_count=med.supplier_count,
            china_api_pct=med.china_api_pct,
            is_who_essential=med.is_who_essential,
            stock_days=round(stock_days, 1),
        ))
    return sorted(results, key=lambda x: -x.composite_score)

def _get_avg_daily(med, db):
    from app.models.consumption import ConsumptionRecord
    from sqlalchemy import func
    result = db.query(func.avg(ConsumptionRecord.units_consumed)).filter(
        ConsumptionRecord.medicine_id == med.id
    ).scalar()
    return float(result) if result else 0.0