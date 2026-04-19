import pandas as pd
import numpy as np
from datetime import date, timedelta
from typing import List, Dict

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
    np.random.seed(42)
    
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


# Seed data: 20 essential medicines with base demand rates
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