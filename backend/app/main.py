# backend/app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import engine, Base

# Import all models so tables get created
from app.models import (
    Medicine, Supplier, MedicineSupplier,
    ConsumptionRecord, RiskScore, Forecast, ReorderRecommendation
)

# Import routers
from app.routers import forecast, medicine, reorder, ai_insights

# Create tables (use Alembic for production — this is a dev convenience)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="MedChain API",
    description="Pharmaceutical Supply Chain Disruption Predictor — India",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS — allow frontend to call backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        settings.FRONTEND_URL,
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(medicine.router)
app.include_router(forecast.router)
app.include_router(reorder.router)
app.include_router(ai_insights.router)

@app.get("/")
def root():
    return {
        "project": "MedChain",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs"
    }

@app.get("/health")
def health_check():
    return {"status": "healthy"}