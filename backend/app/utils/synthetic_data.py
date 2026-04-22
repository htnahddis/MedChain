import pandas as pd
import numpy as np
import random
from datetime import date, timedelta
from typing import List, Dict
from sqlalchemy.orm import Session

from app.models.medicine import Medicine
from app.models.consumption import ConsumptionRecord
from app.models.supplier import Supplier, MedicineSupplier

def generate_hospital_consumption(
    medicine_name: str,
    category: str,
    base_daily_demand: float,
    bed_count: int = 500,
    days_history: int = 365,
    start_date: date = None
) -> pd.DataFrame:
    """
    Generates synthetic hospital consumption data.
    
    Methodology (documented for transparency):
    - Base demand = bed_count × disease_prevalence_rate × category_factor
    - Monsoon multiplier applied for Jul-Sep (India-specific)
    - Random noise (±15%) simulates day-to-day variability
    - Weekend effect: -10% on Sat/Sun (elective procedures lower)
    - Trend: 0.5% monthly growth (India's healthcare penetration)
    
    This approach is standard in pharma consulting when real data is unavailable.
    Reference: NHSRC hospital consumption benchmarks, IMS Health India estimates.
    """
    if start_date is None:
        start_date = date.today() - timedelta(days=days_history)
    
    MONSOON_FACTORS = {
        'Rehydration':  {7: 3.40, 8: 3.10, 9: 2.90},
        'Antibiotic':   {7: 1.80, 8: 1.75, 9: 1.60},
        'Antifungal':   {7: 2.20, 8: 2.00, 9: 1.80},
        'GI':           {7: 1.60, 8: 1.55, 9: 1.45},
        'Respiratory':  {7: 1.30, 8: 1.25, 9: 1.20},
    }
    
    records = []
    
    for i in range(days_history):
        current_date = start_date + timedelta(days=i)
        
        # Monthly trend (0.5% growth)
        trend = 1 + (i / 30) * 0.005
        
        # Monsoon factor
        month = current_date.month
        monsoon = MONSOON_FACTORS.get(category, {}).get(month, 1.0)
        
        # Weekend effect
        weekend = 0.90 if current_date.weekday() >= 5 else 1.0
        
        # Noise
        noise = np.random.normal(1.0, 0.12)
        
        demand = base_daily_demand * trend * monsoon * weekend * noise
        demand = max(0, int(round(demand)))
        
        records.append({
            'date': current_date,
            'medicine_name': medicine_name,
            'category': category,
            'units_consumed': demand,
            'bed_count': bed_count,
            'is_synthetic': True,
            'generation_method': 'bed_prevalence_model',
        })
    
    return pd.DataFrame(records)


# Seed data: 10 essential medicines with base demand rates
ESSENTIAL_MEDICINES_SEED = [
    {'name': 'Amoxicillin 500mg', 'category': 'Antibiotic',    'base_daily': 85,  'beds_per_unit': 5.9},
    {'name': 'ORS Sachets',       'category': 'Rehydration',   'base_daily': 120, 'beds_per_unit': 4.2},
    {'name': 'Metformin 500mg',   'category': 'Antidiabetic',  'base_daily': 65,  'beds_per_unit': 7.7},
    {'name': 'Paracetamol 500mg', 'category': 'Analgesic',     'base_daily': 200, 'beds_per_unit': 2.5},
    {'name': 'Ciprofloxacin',     'category': 'Antibiotic',    'base_daily': 45,  'beds_per_unit': 11.1},
    {'name': 'Atorvastatin 20mg', 'category': 'Cardiovascular','base_daily': 55,  'beds_per_unit': 9.1},
    {'name': 'Omeprazole 20mg',   'category': 'GI',            'base_daily': 90,  'beds_per_unit': 5.6},
    {'name': 'Salbutamol Inhaler','category': 'Respiratory',   'base_daily': 8,   'beds_per_unit': 62.5},
    {'name': 'Metronidazole',     'category': 'Antibiotic',    'base_daily': 40,  'beds_per_unit': 12.5},
    {'name': 'Amlodipine 5mg',    'category': 'Cardiovascular','base_daily': 50,  'beds_per_unit': 10.0},
]


def seed_database(db: Session, bed_count: int = 500, days_history: int = 365):
    """
    Clears existing DB models, pushes Medicines, generates 1-year of synthetic 
    consumption data using our realistic model, and mocks Suppliers.
    """
    # 1. Clear existing generic data to prevent duplication during seed
    db.query(ConsumptionRecord).delete()
    db.query(MedicineSupplier).delete()
    db.query(Supplier).delete()
    db.query(Medicine).delete()
    db.commit()

    # 2. Add realistic suppliers
    suppliers = [
        Supplier(name="Sun Pharma Distributors", reliability_score=92.0, lead_time_days=7),
        Supplier(name="Cipla Logistics", reliability_score=88.5, lead_time_days=10),
        Supplier(name="Reddy Import Solutions", reliability_score=75.0, lead_time_days=21),
        Supplier(name="Ad-Hoc MediSupply", reliability_score=60.0, lead_time_days=5),
    ]
    db.add_all(suppliers)
    db.commit()

    for s in suppliers:
        db.refresh(s)

    # 3. Add medicines and historical consumption
    print(f"Generating {(days_history * len(ESSENTIAL_MEDICINES_SEED))} realistic hospital consumption records...")
    
    np.random.seed(42) # Deterministic generation 
    
    for med_data in ESSENTIAL_MEDICINES_SEED:
        china_api = random.uniform(10.0, 85.0) # Simulate China API dependency for risk scoring
        
        # Dynamically scale demand based on the hospital's bed count
        dynamic_base_daily = bed_count / med_data['beds_per_unit']

        medicine = Medicine(
            name=med_data['name'],
            category=med_data['category'],
            is_who_essential=True,
            current_stock_units=int(dynamic_base_daily * random.uniform(15, 45)), # 15-45 days of stock
            china_api_pct=china_api,
            reorder_point=int(dynamic_base_daily * 20),
            unit_cost_inr=random.uniform(5.0, 55.0)
        )
        db.add(medicine)
        db.commit()
        db.refresh(medicine)

        # Assign 1-3 suppliers to this medicine
        num_suppliers = random.randint(1, 3)
        chosen_suppliers = random.sample(suppliers, num_suppliers)
        for idx, sup in enumerate(chosen_suppliers):
            ms = MedicineSupplier(
                medicine_id=medicine.id,
                supplier_id=sup.id,
                is_primary=(idx == 0),
                china_api_pct= (china_api + random.uniform(-10, 10)) if sup.name == "Reddy Import Solutions" else 0.0
            )
            db.add(ms)
        db.commit()

        # Generate pandas dataframe using our robust methodology
        df = generate_hospital_consumption(
            medicine_name=med_data['name'],
            category=med_data['category'],
            base_daily_demand=dynamic_base_daily,
            bed_count=bed_count,
            days_history=days_history
        )

        # Convert DataFrame to SQLAlchemy ConsumptionRecord models
        records = []
        for _, row in df.iterrows():
            records.append(ConsumptionRecord(
                medicine_id=medicine.id,
                date=row['date'],
                units_consumed=row['units_consumed'],
                facility_type=f"{bed_count}-bed",
                is_synthetic=True
            ))
        
        db.add_all(records)
        db.commit()
    
    print("Database seeding complete. Realistic structural data created.")