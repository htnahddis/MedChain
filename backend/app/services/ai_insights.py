import json
import groq
from app.config import settings

client = groq.AsyncGroq(api_key=settings.GROQ_API_KEY)

SYSTEM_PROMPT = """\
You are MedChain AI — a senior pharmaceutical supply chain analyst embedded in an \
Indian hospital's procurement command centre.

## Your Role
You interpret live supply chain data (stockout forecasts, supplier risk scores, \
reorder recommendations) and translate them into decisions a Hospital CMO or \
Procurement Director can act on *today*. You do NOT generate data — you analyse \
what the dashboard already shows.

## Data You Receive
Each query includes a real-time snapshot:
- Medicines at HIGH / MEDIUM / LOW disruption risk (composite score 0-100)
- Stockout probability over 30 / 60 / 90 day horizons
- Supplier concentration & China API dependency percentages
- WHO Essential Medicines List criticality flags
- Seasonal context (monsoon = Jul-Sep demand spikes for ORS, antibiotics, antifungals)

## Response Rules
1. Lead with the single most urgent action. No preamble.
2. Cite specific medicine names, quantities, and timelines from the snapshot.
3. When China API dependency > 60 %, flag it explicitly and suggest domestic alternatives.
4. Never recommend single-sourcing. Always push toward ≥ 2 qualified suppliers.
5. For monsoon-season queries (Jul-Sep), apply category-specific demand multipliers:
   - Rehydration salts: ~3x baseline
   - Antibiotics: ~1.8x baseline
   - Antifungals: ~2x baseline
6. If the data is insufficient to answer confidently, say so — do not fabricate numbers.
7. Keep responses ≤ 250 words. Use bullet points for recommendations.

## Output Structure
**Risk Summary**: 1-2 sentence overview of the current threat landscape.
**Recommended Actions**: Bulleted, prioritised steps with quantities and deadlines.
**Rationale**: Brief explanation of *why* these actions matter (cost, patient safety, \
regulatory risk).
"""


def _build_context(dashboard_context: dict) -> str:
    """
    Formats the raw dashboard dict into a clean, readable context block
    so the LLM doesn't waste tokens parsing messy JSON.
    """
    high_risk = dashboard_context.get("high_risk_count", 0)
    stockout_30d = dashboard_context.get("stockout_30d", [])
    api_exposure = dashboard_context.get("top_api_exposure", [])
    pending = dashboard_context.get("pending_reorders", [])
    season = dashboard_context.get("current_season", "Standard")

    lines = [
        "── LIVE SUPPLY CHAIN SNAPSHOT ──",
        f"Season           : {season}",
        f"HIGH-risk medicines : {high_risk}",
    ]

    if stockout_30d:
        lines.append(f"Stockout threats (30d): {', '.join(str(m) for m in stockout_30d)}")
    if api_exposure:
        lines.append(f"Top China API exposure: {', '.join(str(m) for m in api_exposure)}")
    if pending:
        lines.append(f"Pending reorders     : {', '.join(str(m) for m in pending)}")

    # Include any extra keys the dashboard sends (future-proof)
    known_keys = {"high_risk_count", "stockout_30d", "top_api_exposure",
                  "pending_reorders", "current_season"}
    extras = {k: v for k, v in dashboard_context.items() if k not in known_keys}
    if extras:
        lines.append(f"Additional context   : {json.dumps(extras, default=str)}")

    return "\n".join(lines)


async def get_supply_chain_insight(question: str, dashboard_context: dict) -> str:
    """
    Sends the user's question + live dashboard context to Claude
    and returns a structured procurement insight.
    """
    if not settings.GROQ_API_KEY or settings.GROQ_API_KEY.startswith("your-groq-"):
        return "AI insights unavailable — please configure a valid GROQ_API_KEY in .env"

    context_block = _build_context(dashboard_context)

    try:
        completion = await client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            max_tokens=800,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"{context_block}\n\n--- QUESTION ---\n{question}"}
            ]
        )
        return completion.choices[0].message.content
    except groq.AuthenticationError:
        return "AI analysis error: Invalid API key. Check your GROQ_API_KEY."
    except groq.RateLimitError:
        return "AI analysis error: Rate limit exceeded. Please try again shortly."
    except Exception as e:
        return f"AI analysis error: {str(e)}"