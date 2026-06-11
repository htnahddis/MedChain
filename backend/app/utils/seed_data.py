# backend/app/utils/seed_data.py
"""
Run this ONCE after migrations to populate the database with:
- 28 essential medicines
- 10 suppliers
- 365 days of synthetic consumption data per medicine
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from app.database import SessionLocal
from app.models.medicine import Medicine
from app.models.supplier import Supplier, MedicineSupplier
from app.models.consumption import ConsumptionRecord
from app.utils.synthetic_data import generate_hospital_consumption
from datetime import date

MEDICINES_DATA = [
    {"name":"Amoxicillin 500mg",    "category":"Antibiotic",     "is_who_essential":True,  "shelf_life_days":730,  "unit":"caps",    "current_stock_units":1530,  "unit_cost_inr":12.0,  "supplier_count":2, "china_api_pct":72.0, "lead_time_days":10, "base_daily":85},
    {"name":"ORS Sachets",          "category":"Rehydration",    "is_who_essential":True,  "shelf_life_days":1095, "unit":"sachets", "current_stock_units":1680,  "unit_cost_inr":3.0,   "supplier_count":1, "china_api_pct":45.0, "lead_time_days":7,  "base_daily":120},
    {"name":"Metformin 500mg",      "category":"Antidiabetic",   "is_who_essential":True,  "shelf_life_days":1825, "unit":"tabs",    "current_stock_units":1365,  "unit_cost_inr":8.0,   "supplier_count":2, "china_api_pct":88.0, "lead_time_days":7,  "base_daily":65},
    {"name":"Paracetamol 500mg",    "category":"Analgesic",      "is_who_essential":True,  "shelf_life_days":1825, "unit":"tabs",    "current_stock_units":5600,  "unit_cost_inr":4.0,   "supplier_count":3, "china_api_pct":60.0, "lead_time_days":5,  "base_daily":200},
    {"name":"Ciprofloxacin 500mg",  "category":"Antibiotic",     "is_who_essential":True,  "shelf_life_days":730,  "unit":"tabs",    "current_stock_units":1440,  "unit_cost_inr":18.0,  "supplier_count":2, "china_api_pct":78.0, "lead_time_days":12, "base_daily":45},
    {"name":"Atorvastatin 20mg",    "category":"Cardiovascular", "is_who_essential":True,  "shelf_life_days":1095, "unit":"tabs",    "current_stock_units":1925,  "unit_cost_inr":22.0,  "supplier_count":3, "china_api_pct":65.0, "lead_time_days":10, "base_daily":55},
    {"name":"Omeprazole 20mg",      "category":"GI",             "is_who_essential":True,  "shelf_life_days":730,  "unit":"caps",    "current_stock_units":3420,  "unit_cost_inr":15.0,  "supplier_count":4, "china_api_pct":55.0, "lead_time_days":8,  "base_daily":90},
    {"name":"Metronidazole 400mg",  "category":"Antibiotic",     "is_who_essential":True,  "shelf_life_days":1095, "unit":"tabs",    "current_stock_units":1800,  "unit_cost_inr":9.0,   "supplier_count":4, "china_api_pct":48.0, "lead_time_days":7,  "base_daily":40},
    {"name":"Amlodipine 5mg",       "category":"Cardiovascular", "is_who_essential":True,  "shelf_life_days":1825, "unit":"tabs",    "current_stock_units":2600,  "unit_cost_inr":14.0,  "supplier_count":5, "china_api_pct":52.0, "lead_time_days":10, "base_daily":50},
    {"name":"Salbutamol Inhaler",   "category":"Respiratory",    "is_who_essential":True,  "shelf_life_days":730,  "unit":"units",   "current_stock_units":440,   "unit_cost_inr":85.0,  "supplier_count":4, "china_api_pct":42.0, "lead_time_days":21, "base_daily":8},
    {"name":"Ceftriaxone 1g Inj",   "category":"Antibiotic",     "is_who_essential":True,  "shelf_life_days":730,  "unit":"vials",   "current_stock_units":1160,  "unit_cost_inr":120.0, "supplier_count":3, "china_api_pct":68.0, "lead_time_days":14, "base_daily":20},
    {"name":"Insulin Regular",      "category":"Antidiabetic",   "is_who_essential":True,  "shelf_life_days":365,  "unit":"vials",   "current_stock_units":620,   "unit_cost_inr":280.0, "supplier_count":4, "china_api_pct":35.0, "lead_time_days":14, "base_daily":10},
    {"name":"Doxycycline 100mg",    "category":"Antibiotic",     "is_who_essential":True,  "shelf_life_days":730,  "unit":"tabs",    "current_stock_units":2275,  "unit_cost_inr":11.0,  "supplier_count":5, "china_api_pct":58.0, "lead_time_days":10, "base_daily":35},
    {"name":"Fluconazole 150mg",    "category":"Antifungal",     "is_who_essential":True,  "shelf_life_days":1095, "unit":"tabs",    "current_stock_units":2250,  "unit_cost_inr":32.0,  "supplier_count":4, "china_api_pct":62.0, "lead_time_days":12, "base_daily":30},
    {"name":"Losartan 50mg",        "category":"Cardiovascular", "is_who_essential":True,  "shelf_life_days":1825, "unit":"tabs",    "current_stock_units":2800,  "unit_cost_inr":18.0,  "supplier_count":5, "china_api_pct":48.0, "lead_time_days":10, "base_daily":35},
    {"name":"Cetirizine 10mg",      "category":"Antihistamine",  "is_who_essential":False, "shelf_life_days":1825, "unit":"tabs",    "current_stock_units":4750,  "unit_cost_inr":5.0,   "supplier_count":8, "china_api_pct":42.0, "lead_time_days":7,  "base_daily":50},
    {"name":"Ibuprofen 400mg",      "category":"Analgesic",      "is_who_essential":True,  "shelf_life_days":1825, "unit":"tabs",    "current_stock_units":6000,  "unit_cost_inr":8.0,   "supplier_count":8, "china_api_pct":35.0, "lead_time_days":5,  "base_daily":60},
    {"name":"Prednisolone 5mg",     "category":"Corticosteroid", "is_who_essential":True,  "shelf_life_days":1095, "unit":"tabs",    "current_stock_units":5625,  "unit_cost_inr":9.0,   "supplier_count":9, "china_api_pct":40.0, "lead_time_days":8,  "base_daily":45},
    {"name":"Morphine 10mg Inj",    "category":"Analgesic",      "is_who_essential":True,  "shelf_life_days":730,  "unit":"vials",   "current_stock_units":1560,  "unit_cost_inr":95.0,  "supplier_count":6, "china_api_pct":22.0, "lead_time_days":14, "base_daily":12},
    {"name":"Digoxin 0.25mg",       "category":"Cardiovascular", "is_who_essential":True,  "shelf_life_days":1825, "unit":"tabs",    "current_stock_units":7000,  "unit_cost_inr":12.0,  "supplier_count":7, "china_api_pct":18.0, "lead_time_days":10, "base_daily":50},
    {"name":"Warfarin 5mg",         "category":"Anticoagulant",  "is_who_essential":True,  "shelf_life_days":1825, "unit":"tabs",    "current_stock_units":7250,  "unit_cost_inr":18.0,  "supplier_count":8, "china_api_pct":25.0, "lead_time_days":10, "base_daily":50},
    {"name":"Phenytoin 100mg",      "category":"Anticonvulsant", "is_who_essential":True,  "shelf_life_days":1825, "unit":"tabs",    "current_stock_units":6000,  "unit_cost_inr":7.0,   "supplier_count":8, "china_api_pct":30.0, "lead_time_days":10, "base_daily":40},
    {"name":"Diazepam 5mg",         "category":"Sedative",       "is_who_essential":True,  "shelf_life_days":1825, "unit":"tabs",    "current_stock_units":6050,  "unit_cost_inr":6.0,   "supplier_count":7, "china_api_pct":28.0, "lead_time_days":10, "base_daily":55},
    {"name":"Folic Acid 5mg",       "category":"Supplement",     "is_who_essential":True,  "shelf_life_days":1825, "unit":"tabs",    "current_stock_units":9600,  "unit_cost_inr":3.0,   "supplier_count":12,"china_api_pct":20.0, "lead_time_days":7,  "base_daily":60},
    {"name":"Zinc Sulfate",         "category":"Supplement",     "is_who_essential":True,  "shelf_life_days":1825, "unit":"tabs",    "current_stock_units":10200, "unit_cost_inr":4.0,   "supplier_count":11,"china_api_pct":18.0, "lead_time_days":7,  "base_daily":60},
    {"name":"Multivitamin Tabs",    "category":"Supplement",     "is_who_essential":False, "shelf_life_days":1825, "unit":"tabs",    "current_stock_units":9000,  "unit_cost_inr":45.0,  "supplier_count":10,"china_api_pct":30.0, "lead_time_days":7,  "base_daily":60},
    {"name":"Ranitidine 150mg",     "category":"GI",             "is_who_essential":False, "shelf_life_days":1095, "unit":"tabs",    "current_stock_units":4900,  "unit_cost_inr":7.0,   "supplier_count":6, "china_api_pct":44.0, "lead_time_days":8,  "base_daily":70},
    {"name":"Paracetamol Syrup",    "category":"Analgesic",      "is_who_essential":True,  "shelf_life_days":730,  "unit":"bottles", "current_stock_units":2700,  "unit_cost_inr":28.0,  "supplier_count":7, "china_api_pct":38.0, "lead_time_days":7,  "base_daily":30},
]

SUPPLIERS_DATA = [
    {"name":"Sun Pharmaceutical", "country":"India", "reliability_score":82.0, "lead_time_days":7,  "specialties":"Antibiotics, Antidiabetics"},
    {"name":"Cipla Ltd",           "country":"India", "reliability_score":78.0, "lead_time_days":8,  "specialties":"Respiratory, Generics"},
    {"name":"Dr. Reddys Labs",     "country":"India", "reliability_score":74.0, "lead_time_days":10, "specialties":"Cardiovascular, GI"},
    {"name":"Zydus Cadila",        "country":"India", "reliability_score":70.0, "lead_time_days":7,  "specialties":"Antidiabetics, Supplements"},
    {"name":"Aurobindo Pharma",    "country":"India", "reliability_score":65.0, "lead_time_days":12, "specialties":"Antibiotics, API"},
    {"name":"Hetero Drugs",        "country":"India", "reliability_score":58.0, "lead_time_days":14, "specialties":"Injectables, Generics"},
    {"name":"Granules India",      "country":"India", "reliability_score":62.0, "lead_time_days":8,  "specialties":"Paracetamol, Metformin"},
    {"name":"DIVI Laboratories",   "country":"India", "reliability_score":68.0, "lead_time_days":10, "specialties":"API, Nutraceuticals"},
    {"name":"Sinochem Pharma",     "country":"China", "reliability_score":38.0, "lead_time_days":28, "specialties":"API manufacturer"},
    {"name":"Zhejiang Medicine",   "country":"China", "reliability_score":32.0, "lead_time_days":35, "specialties":"Antibiotic API"},
]


def seed():
    db = SessionLocal()
    try:
        # Skip if already seeded
        if db.query(Medicine).count() > 0:
            print("[OK] Database already seeded. Skipping.")
            return

        print("Seeding suppliers...")
        supplier_objs = []
        for s in SUPPLIERS_DATA:
            obj = Supplier(**s)
            db.add(obj)
            supplier_objs.append(obj)
        db.commit()

        print("Seeding medicines + consumption data...")
        for med_data in MEDICINES_DATA:
            base_daily = med_data.pop("base_daily")
            med = Medicine(**med_data)
            db.add(med)
            db.commit()
            db.refresh(med)

            # Generate 365 days of synthetic consumption
            df = generate_hospital_consumption(
                medicine_name=med.name,
                category=med.category,
                base_daily_demand=base_daily,
                bed_count=500,
                days_history=365
            )
            records = [
                ConsumptionRecord(
                    medicine_id=med.id,
                    date=row['date'],
                    units_consumed=int(row['units_consumed']),
                    facility_type="500-bed",
                    is_synthetic=True
                )
                for _, row in df.iterrows()
            ]
            db.bulk_save_objects(records)
            db.commit()
            print(f"  [OK] {med.name} - {len(records)} consumption records")

        print("\n[DONE] Seeding complete!")
        print(f"   {db.query(Medicine).count()} medicines")
        print(f"   {db.query(Supplier).count()} suppliers")
        print(f"   {db.query(ConsumptionRecord).count()} consumption records")

    except Exception as e:
        db.rollback()
        print(f"[ERROR] Seed error: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()