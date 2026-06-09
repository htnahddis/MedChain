import google.generativeai as genai
from app.config import settings

genai.configure(api_key=settings.GEMINI_API_KEY)

SYSTEM_PROMPT = """You are MedChain AI, an expert pharmaceutical supply chain analyst 
specialising in India's essential medicines supply chain. 

You have real-time access to:
- Stockout risk forecasts (30/60/90 day horizons)
- Supplier concentration scores
- China API dependency data
- WHO essential medicines criticality
- Hospital consumption patterns and monsoon seasonality factors

Provide concise, data-driven, actionable insights. Reference specific medicines, 
quantities, and timelines. Frame recommendations in terms a hospital CMO or 
procurement director would immediately act on. Keep responses under 300 words."""

async def get_supply_chain_insight(question: str, dashboard_context: dict) -> str:
    """
    Streams AI analysis of current supply chain state.
    dashboard_context contains live risk scores, forecasts, and reorder data.
    """
    if not settings.GEMINI_API_KEY:
        return "AI insights unavailable — GEMINI_API_KEY not configured."

    context_summary = f"""
Current supply chain snapshot:
- High risk medicines: {dashboard_context.get('high_risk_count', 0)}
- Immediate stockout threats (30d): {dashboard_context.get('stockout_30d', [])}
- Top China API exposure: {dashboard_context.get('top_api_exposure', [])}
- Pending reorders: {dashboard_context.get('pending_reorders', [])}
- Season: {dashboard_context.get('current_season', 'Standard')}
    """
    
    try:
        model = genai.GenerativeModel(
            model_name="gemini-2.0-flash",
            system_instruction=SYSTEM_PROMPT
        )
        
        prompt = f"{context_summary}\n\nQuestion: {question}"
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                max_output_tokens=600,
                temperature=0.7
            )
        )
        return response.text
    except Exception as e:
        return f"AI analysis error: {str(e)}"