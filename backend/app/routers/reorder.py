# backend/app/routers/reorder.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.medicine import Medicine
from app.models.consumption import ConsumptionRecord
from app.services.reorder_engine import ReorderEngine
from app.schemas.forecast import ReorderItem
from sqlalchemy import func

router = APIRouter(prefix="/api/reorder", tags=["Reorder"])

@router.get("/recommendations", response_model=List[ReorderItem])
def get_reorder_recommendations(db: Session = Depends(get_db)):
    """
    Generate reorder recommendations for all medicines using
    safety stock + EOQ model.
    """
    engine = ReorderEngine(service_level=0.95)
    medicines = db.query(Medicine).all()
    results = []

    for med in medicines:
        # Get consumption stats from last 90 days
        records = db.query(ConsumptionRecord).filter(
            ConsumptionRecord.medicine_id == med.id
        ).order_by(ConsumptionRecord.date.desc()).limit(90).all()

        if not records:
            continue

        values = [r.units_consumed for r in records]
        import numpy as np
        avg_daily = float(np.mean(values))
        std_daily = float(np.std(values))

        medicine_dict = {
            'id': med.id,
            'name': med.name,
            'current_stock_units': med.current_stock_units,
            'unit_cost': med.unit_cost_inr,
            'lead_time_days': med.lead_time_days,
        }
        forecast_dict = {
            'avg_daily_demand': avg_daily,
            'std_daily_demand': std_daily,
        }

        rec = engine.generate_recommendation(medicine_dict, forecast_dict)
        if rec['urgency'] in ('URGENT', 'WARNING'):
            results.append(ReorderItem(**rec))

    return sorted(results, key=lambda x: (
        0 if x.urgency == 'URGENT' else 1 if x.urgency == 'WARNING' else 2
    ))