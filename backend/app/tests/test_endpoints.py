# backend/app/tests/test_endpoints.py
"""
MedChain API — one test per endpoint (11 total).

Uses an in-memory SQLite database so tests are completely self-contained.
No PostgreSQL, Docker, or Groq API key required.

Run with:
    cd backend
    python -m pytest app/tests/test_endpoints.py -v
"""

import math
from datetime import date, timedelta
from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# ── App imports ──────────────────────────────────────────────────────────────
from app.database import Base, get_db
from app.main import app
from app.models.medicine import Medicine
from app.models.consumption import ConsumptionRecord

# ── Test DB (in-memory SQLite) ───────────────────────────────────────────────
SQLALCHEMY_TEST_URL = "sqlite://"

engine = create_engine(
    SQLALCHEMY_TEST_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

# SQLite doesn't enforce FK constraints by default — enable them.
@event.listens_for(engine, "connect")
def _set_sqlite_pragma(dbapi_conn, connection_record):
    cursor = dbapi_conn.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# ── Fixtures ─────────────────────────────────────────────────────────────────
@pytest.fixture(autouse=True)
def setup_database():
    """Create all tables before each test, drop them after."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def db_session():
    """Yield a fresh DB session; rollback on failure."""
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture()
def client(db_session):
    """FastAPI TestClient wired to the in-memory test DB."""

    def _override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = _override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture()
def seed_medicine(db_session) -> Medicine:
    """Insert a single realistic medicine row and return it."""
    med = Medicine(
        id=1,
        name="Amoxicillin 500 mg",
        generic_name="Amoxicillin",
        category="Antibiotic",
        is_who_essential=True,
        shelf_life_days=730,
        unit="caps",
        current_stock_units=5000,
        unit_cost_inr=3.50,
        supplier_count=2,
        china_api_pct=65.0,
        lead_time_days=14,
        reorder_point=500,
    )
    db_session.add(med)
    db_session.commit()
    db_session.refresh(med)
    return med


@pytest.fixture()
def seed_consumption(db_session, seed_medicine) -> list[ConsumptionRecord]:
    """
    Insert 60 synthetic daily consumption records for the seeded medicine.
    Enough data to satisfy the ≥30-record checks in forecast & stockout.
    """
    records = []
    base_date = date.today() - timedelta(days=60)
    for i in range(60):
        rec = ConsumptionRecord(
            medicine_id=seed_medicine.id,
            date=base_date + timedelta(days=i),
            units_consumed=80 + (i % 15),  # 80-94 units/day with variation
            facility_type="500-bed",
            is_synthetic=True,
        )
        records.append(rec)
    db_session.add_all(records)
    db_session.commit()
    return records


# ═════════════════════════════════════════════════════════════════════════════
#  TEST CASES — one per endpoint
# ═════════════════════════════════════════════════════════════════════════════


# ── 1. GET / ─────────────────────────────────────────────────────────────────
def test_root(client):
    """Root endpoint returns project metadata."""
    resp = client.get("/")
    assert resp.status_code == 200
    body = resp.json()
    assert body["project"] == "MedChain"
    assert body["version"] == "1.0.0"
    assert body["status"] == "running"
    assert body["docs"] == "/docs"


# ── 2. GET /health ───────────────────────────────────────────────────────────
def test_health_check(client):
    """Health-check endpoint returns healthy status."""
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "healthy"}


# ── 3. GET /api/medicines/ ───────────────────────────────────────────────────
def test_list_medicines(client, seed_medicine):
    """List medicines returns the seeded medicine with correct fields."""
    resp = client.get("/api/medicines/")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["name"] == "Amoxicillin 500 mg"
    assert data[0]["category"] == "Antibiotic"
    assert data[0]["is_who_essential"] is True


# ── 4. GET /api/medicines/{medicine_id} ──────────────────────────────────────
def test_get_medicine_by_id(client, seed_medicine):
    """Fetching a medicine by valid ID returns the correct record."""
    resp = client.get(f"/api/medicines/{seed_medicine.id}")
    assert resp.status_code == 200
    body = resp.json()
    assert body["id"] == seed_medicine.id
    assert body["generic_name"] == "Amoxicillin"
    assert body["unit_cost_inr"] == 3.50

    # Also verify 404 for a non-existent ID
    resp_404 = client.get("/api/medicines/9999")
    assert resp_404.status_code == 404
    assert resp_404.json()["detail"] == "Medicine not found"


# ── 5. POST /api/medicines/ ──────────────────────────────────────────────────
def test_create_medicine(client):
    """Creating a medicine returns 201 with the generated ID."""
    payload = {
        "name": "Metformin 500 mg",
        "generic_name": "Metformin",
        "category": "Antidiabetic",
        "is_who_essential": True,
        "shelf_life_days": 1095,
        "unit": "tabs",
        "current_stock_units": 12000,
        "unit_cost_inr": 1.80,
        "supplier_count": 5,
        "china_api_pct": 80.0,
        "lead_time_days": 10,
    }
    resp = client.post("/api/medicines/", json=payload)
    assert resp.status_code == 201
    body = resp.json()
    assert body["id"] is not None
    assert body["name"] == "Metformin 500 mg"
    assert body["china_api_pct"] == 80.0

    # Verify it persists — GET should return it
    resp_get = client.get(f"/api/medicines/{body['id']}")
    assert resp_get.status_code == 200
    assert resp_get.json()["generic_name"] == "Metformin"


# ── 6. GET /api/medicines/risk-scores/all ────────────────────────────────────
def test_medicine_risk_scores_all(client, seed_medicine, seed_consumption):
    """Risk-scores endpoint returns computed scores for the seeded medicine."""
    resp = client.get("/api/medicines/risk-scores/all")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) == 1

    item = data[0]
    assert item["medicine_id"] == seed_medicine.id
    assert item["medicine_name"] == "Amoxicillin 500 mg"
    assert item["risk_tier"] in ("HIGH", "MED", "LOW")
    assert 0 <= item["composite_score"] <= 100
    assert item["supplier_count"] == 2
    assert item["china_api_pct"] == 65.0
    assert item["is_who_essential"] is True
    # stock_days should be finite given real consumption data
    assert item["stock_days"] > 0


# ── 7. GET /api/forecast/{medicine_id} ───────────────────────────────────────
def test_forecast_for_medicine(client, seed_medicine, seed_consumption):
    """
    Forecast endpoint returns valid time-series predictions.
    Requires ≥30 consumption records (seed provides 60).
    """
    resp = client.get(
        f"/api/forecast/{seed_medicine.id}",
        params={"horizon_days": 30},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["medicine_id"] == seed_medicine.id
    assert body["medicine_name"] == "Amoxicillin 500 mg"
    assert body["horizon_days"] == 30
    assert isinstance(body["forecasts"], list)
    assert len(body["forecasts"]) == 30  # one per horizon day
    assert body["model_mape"] is not None

    # Each forecast point should have these keys
    point = body["forecasts"][0]
    assert "forecast_date" in point
    assert "predicted_units" in point

    # 404 for non-existent medicine
    resp_404 = client.get("/api/forecast/9999")
    assert resp_404.status_code == 404


# ── 8. GET /api/forecast/stockout-risk/all ───────────────────────────────────
def test_stockout_risk_all(client, seed_medicine, seed_consumption):
    """Stockout-risk endpoint computes probability for all medicines."""
    resp = client.get(
        "/api/forecast/stockout-risk/all",
        params={"horizon": 30},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) >= 1

    item = data[0]
    assert item["medicine_id"] == seed_medicine.id
    assert 0 <= item["stockout_probability_pct"] <= 100
    assert item["avg_daily_demand"] > 0
    assert item["stock_days"] > 0
    assert item["horizon_days"] == 30


# ── 9. GET /api/forecast/risk-scores/all ─────────────────────────────────────
def test_forecast_risk_scores_all(client, seed_medicine):
    """Forecast-router risk-scores endpoint returns structured data."""
    resp = client.get("/api/forecast/risk-scores/all")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) == 1

    item = data[0]
    assert item["name"] == "Amoxicillin 500 mg"
    assert item["composite_score"] >= 0
    assert item["risk_tier"] in ("HIGH", "MED", "LOW")
    assert "supplier_score" in item
    assert "api_dependency_score" in item


# ── 10. GET /api/reorder/recommendations ─────────────────────────────────────
def test_reorder_recommendations(client, seed_medicine, seed_consumption):
    """
    Reorder engine returns recommendations for medicines with
    URGENT or WARNING urgency.
    """
    resp = client.get("/api/reorder/recommendations")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)

    # With 5000 stock and ~87 units/day avg, days_of_stock ≈ 57 → WARNING
    if len(data) > 0:
        item = data[0]
        assert item["urgency"] in ("URGENT", "WARNING")
        assert item["medicine_id"] == seed_medicine.id
        assert item["recommended_qty"] > 0
        assert item["estimated_cost_inr"] > 0
        assert item["safety_stock"] >= 0
        assert item["reorder_point"] >= 0
        assert item["avg_daily_demand"] > 0


# ── 11. POST /ai-insights/ ──────────────────────────────────────────────────
def test_ai_insights(client):
    """
    AI insights endpoint accepts a question + dashboard context
    and returns an insight string. Mocks the Groq call.
    """
    mock_response = (
        "**Risk Summary**: Amoxicillin is at critical supply risk.\n"
        "**Recommended Actions**:\n"
        "- Immediately place emergency order for 10,000 caps\n"
        "- Qualify backup domestic supplier within 15 days\n"
        "**Rationale**: China API dependency at 65% and single-source risk."
    )

    with patch(
        "app.routers.ai_insights.generate_insight",
        new_callable=AsyncMock,
        return_value=mock_response,
    ):
        payload = {
            "question": "What is our biggest supply chain risk right now?",
            "dashboard_context": {
                "high_risk_count": 3,
                "stockout_30d": ["Amoxicillin 500 mg", "ORS Sachets"],
                "top_api_exposure": ["Amoxicillin 500 mg"],
                "pending_reorders": ["Amoxicillin 500 mg"],
                "current_season": "Monsoon",
            },
        }
        resp = client.post("/ai-insights/", json=payload)
        assert resp.status_code == 200
        body = resp.json()
        assert "insight" in body
        assert "Amoxicillin" in body["insight"]
        assert "Risk Summary" in body["insight"]
