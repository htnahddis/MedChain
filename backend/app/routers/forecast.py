from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.services.forecasting import DemandForecaster
from app.models.medicine import Medicine
from app.models.consumption import ConsumptionRecord
from app.schemas.forecast import ForecastResponse
import pandas as pd

router = APIRouter(prefix="/api/forecast", tags=["Forecast"])

@router.get("/{medicine_id}", response_model=ForecastResponse)
async def get_forecast(
    medicine_id: int,
    horizon_days: int = Query(default=90, ge=7, le=180),
    db: Session = Depends(get_db)
):
    """
    Returns time-series demand forecast for a specific medicine.
    
    Uses Prophet + ARIMA ensemble. Factors in:
    - Historical hospital consumption
    - Monsoon seasonality (Jul-Sep)
    - Disease outbreak signals
    """
    medicine = db.query(Medicine).filter(Medicine.id == medicine_id).first()
    if not medicine:
        raise HTTPException(status_code=404, detail="Medicine not found")

    records = db.query(ConsumptionRecord).filter(
        ConsumptionRecord.medicine_id == medicine_id
    ).order_by(ConsumptionRecord.date).all()

    if len(records) < 30:
        raise HTTPException(
            status_code=422,
            detail=f"Insufficient data: need ≥30 records, have {len(records)}"
        )

    consumption_dicts = [{'date': r.date, 'units_consumed': r.units_consumed} for r in records]
    
    forecaster = DemandForecaster(medicine_category=medicine.category)
    df = forecaster.prepare_dataframe(consumption_dicts)
    forecast_df = forecaster.forecast(df, horizon_days=horizon_days)

    # Compute MAPE on last 30 days holdout
    holdout_df = df.tail(30)
    holdout_forecast = forecaster.forecast(df.iloc[:-30], horizon_days=30)
    mape = forecaster.calculate_mape(
        holdout_df['y'].values,
        holdout_forecast['predicted_units'].values
    )

    return ForecastResponse(
        medicine_id=medicine_id,
        medicine_name=medicine.name,
        category=medicine.category,
        horizon_days=horizon_days,
        model_mape=round(mape, 2),
        forecasts=forecast_df.to_dict('records')
    )


@router.get("/stockout-risk/all")
async def get_stockout_risk_all(
    horizon: int = Query(default=30, description="30, 60, or 90 days"),
    db: Session = Depends(get_db)
):
    """
    Returns stockout probability for all medicines within the given horizon.
    Used to power the main risk table.
    """
    medicines = db.query(Medicine).all()
    results = []
    
    for med in medicines:
        records = db.query(ConsumptionRecord).filter(
            ConsumptionRecord.medicine_id == med.id
        ).order_by(ConsumptionRecord.date).all()
        
        if len(records) < 30:
            continue
            
        avg_daily = sum(r.units_consumed for r in records[-30:]) / 30
        stock_days = (med.current_stock_units / avg_daily) if avg_daily > 0 else 999
        
        # Stockout probability: sigmoid function of (stock_days - horizon)
        import math
        gap = stock_days - horizon
        prob = 1 / (1 + math.exp(0.15 * gap))  # S-curve centred at gap=0
        
        results.append({
            'medicine_id': med.id,
            'medicine_name': med.name,
            'category': med.category,
            'avg_daily_demand': round(avg_daily, 1),
            'current_stock': med.current_stock_units,
            'stock_days': round(stock_days, 1),
            'stockout_probability_pct': round(prob * 100, 1),
            'horizon_days': horizon,
        })
    
    return sorted(results, key=lambda x: -x['stockout_probability_pct'])


@router.get("/risk-scores/all")
async def get_all_risk_scores(db: Session = Depends(get_db)):
    """Returns composite risk scores for all medicines."""
    from app.services.riskscoring import RiskScorer
    scorer = RiskScorer()
    medicines = db.query(Medicine).all()
    
    results = []
    for med in medicines:
        data = {
            'id': med.id,
            'name': med.name,
            'category': med.category,
            'supplier_count': med.supplier_count,
            'china_api_pct': med.china_api_pct,
            'shelf_life_days': med.shelf_life_days,
            'is_who_essential': med.is_who_essential,
        }
        score = scorer.compute_composite(data)
        results.append({**data, **score})
    
    return sorted(results, key=lambda x: -x['composite_score'])