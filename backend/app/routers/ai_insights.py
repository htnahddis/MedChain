from fastapi import APIRouter
from pydantic import BaseModel
from typing import Dict, Any
from app.services.ai_insights import get_supply_chain_insight as generate_insight

router = APIRouter(prefix="/ai-insights", tags=["AI Insights"])

class InsightRequest(BaseModel):
    question: str
    dashboard_context: Dict[str, Any]

@router.post("/")
async def get_supply_chain_insight_endpoint(request: InsightRequest):
    insight = await generate_insight(request.question, request.dashboard_context)
    return {"insight": insight}