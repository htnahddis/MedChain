<<<<<<< HEAD
import anthropic
from app.config import settings

client = anthropic.AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
=======
from groq import Groq
from app.config import settings

client = Groq(api_key=settings.GROQ_API_KEY)
>>>>>>> another_branch_soham

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
<<<<<<< HEAD
    if not settings.ANTHROPIC_API_KEY:
        return "AI insights unavailable — ANTHROPIC_API_KEY not configured."
=======
    if not settings.GROQ_API_KEY:
        return "AI insights unavailable — GROQ_API_KEY not configured."
>>>>>>> another_branch_soham

    context_summary = f"""
Current supply chain snapshot:
- High risk medicines: {dashboard_context.get('high_risk_count', 0)}
- Immediate stockout threats (30d): {dashboard_context.get('stockout_30d', [])}
- Top China API exposure: {dashboard_context.get('top_api_exposure', [])}
- Pending reorders: {dashboard_context.get('pending_reorders', [])}
- Season: {dashboard_context.get('current_season', 'Standard')}
    """
<<<<<<< HEAD
    
    try:
        message = await client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=600,
            system=SYSTEM_PROMPT,
            messages=[{
                "role": "user",
                "content": f"{context_summary}\n\nQuestion: {question}"
            }]
        )
        return message.content[0].text
=======

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"{context_summary}\n\nQuestion: {question}"}
            ],
            max_tokens=600,
            temperature=0.7
        )
        return response.choices[0].message.content
>>>>>>> another_branch_soham
    except Exception as e:
        return f"AI analysis error: {str(e)}"