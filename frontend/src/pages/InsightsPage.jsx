import { useState, useMemo } from 'react';
import { Sparkles, Send, Zap, MessageCircle } from 'lucide-react';
import { useRiskScores, useStockoutRisk, useReorderRecommendations } from '../hooks/useData';
import * as api from '../services/api';
import { LoadingState } from '../components/ui';

const SUGGESTED_QUESTIONS = [
  "Which medicines need immediate procurement action?",
  "What's the monsoon season impact on antibiotic demand?",
  "Summarize our China API dependency risk exposure.",
  "Which WHO essential medicines are at highest stockout risk?",
  "Recommend supplier diversification priorities for this quarter.",
  "What would happen if China export restrictions increased by 20%?",
];

export default function InsightsPage() {
  const { data: riskScores } = useRiskScores();
  const { data: stockoutRisk } = useStockoutRisk(30);
  const { data: reorderRecs } = useReorderRecommendations();

  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);

  const dashboardContext = useMemo(() => {
    if (!riskScores || !stockoutRisk || !reorderRecs) return {};
    const highRisk = riskScores.filter(r => r.risk_tier === 'HIGH');
    return {
      high_risk_count: highRisk.length,
      stockout_30d: stockoutRisk.filter(s => s.stockout_probability_pct > 60).map(s => s.medicine_name),
      top_api_exposure: riskScores.filter(r => r.china_api_pct > 70).map(r => `${r.medicine_name} (${r.china_api_pct}%)`),
      pending_reorders: reorderRecs.map(r => `${r.medicine_name} [${r.urgency}]`),
      current_season: new Date().getMonth() >= 6 && new Date().getMonth() <= 8 ? 'Monsoon' : 'Standard',
    };
  }, [riskScores, stockoutRisk, reorderRecs]);

  const handleSend = async (question) => {
    const q = question || input.trim();
    if (!q) return;

    setMessages(prev => [...prev, { role: 'user', content: q }]);
    setInput('');
    setLoading(true);

    try {
      const res = await api.getAIInsight(q, dashboardContext);
      setMessages(prev => [...prev, { role: 'assistant', content: res.insight }]);
    } catch {
      // Offline fallback
      const fallback = generateOfflineInsight(q, dashboardContext);
      setMessages(prev => [...prev, { role: 'assistant', content: fallback }]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="main-content animate-in">
      <div className="page-header">
        <h1>AI Insights</h1>
        <p>Ask MedChain AI about your supply chain — powered by real-time dashboard data</p>
      </div>

      {/* Suggested Questions */}
      <div className="card" style={{ marginBottom: 'var(--space-md)' }}>
        <div className="card-header">
          <div className="card-title"><Zap size={16} /> Suggested Questions</div>
        </div>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
          {SUGGESTED_QUESTIONS.map((q, i) => (
            <button
              key={i}
              className="btn"
              onClick={() => handleSend(q)}
              style={{ fontSize: 'var(--font-size-sm)' }}
            >
              {q}
            </button>
          ))}
        </div>
      </div>

      {/* Chat area */}
      <div className="ai-panel" style={{ minHeight: 400 }}>
        <div className="ai-panel-header">
          <Sparkles size={18} />
          <span style={{ fontWeight: 600 }}>MedChain AI Assistant</span>
          <span style={{ marginLeft: 'auto', fontSize: 'var(--font-size-xs)', color: 'var(--color-text-tertiary)' }}>
            Llama 3.3 70B via Groq
          </span>
        </div>
        <div className="ai-panel-body" style={{ maxHeight: 450, overflowY: 'auto' }}>
          {messages.length === 0 && !loading && (
            <div className="empty-state">
              <MessageCircle size={48} />
              <p>Ask a question about your supply chain to get started</p>
            </div>
          )}

          {messages.map((msg, i) => (
            <div key={i} style={{
              marginBottom: 'var(--space-md)',
              display: 'flex',
              flexDirection: 'column',
              alignItems: msg.role === 'user' ? 'flex-end' : 'flex-start',
            }}>
              <div style={{
                fontSize: 'var(--font-size-xs)',
                color: 'var(--color-text-tertiary)',
                marginBottom: 4,
                textTransform: 'uppercase',
                letterSpacing: '0.08em',
                fontWeight: 600,
              }}>
                {msg.role === 'user' ? 'You' : 'MedChain AI'}
              </div>
              <div style={{
                maxWidth: '80%',
                padding: 'var(--space-md)',
                borderRadius: 'var(--radius-md)',
                background: msg.role === 'user' ? 'rgba(139,92,246,0.12)' : 'var(--color-bg-elevated)',
                border: `1px solid ${msg.role === 'user' ? 'rgba(139,92,246,0.2)' : 'var(--color-border)'}`,
              }}>
                <div className="ai-response">{msg.content}</div>
              </div>
            </div>
          ))}

          {loading && (
            <div style={{ display: 'flex', alignItems: 'center', gap: 8, color: 'var(--color-text-tertiary)', fontSize: 'var(--font-size-sm)' }}>
              <div className="spinner" />
              Analyzing supply chain data…
            </div>
          )}
        </div>

        {/* Input */}
        <div style={{ padding: 'var(--space-md)', borderTop: '1px solid var(--color-border)' }}>
          <div className="ai-panel-input-row">
            <input
              type="text"
              className="ai-panel-input"
              placeholder="Ask about stockout risks, supplier diversification, seasonal demand…"
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              disabled={loading}
              id="ai-chat-input"
            />
            <button
              className="btn btn-primary"
              onClick={() => handleSend()}
              disabled={loading || !input.trim()}
              id="ai-send-btn"
            >
              <Send size={14} />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

/* Offline fallback when Groq API is unavailable */
function generateOfflineInsight(question, ctx) {
  const q = question.toLowerCase();

  if (q.includes('procurement') || q.includes('immediate') || q.includes('action')) {
    const urgent = ctx.pending_reorders?.filter(r => r.includes('URGENT')) || [];
    return `**Immediate Procurement Actions Required:**\n\n${
      urgent.length > 0
        ? urgent.map((r, i) => `${i + 1}. ${r}`).join('\n')
        : 'No urgent reorders at this time.'
    }\n\nThese medicines have less than 30 days of stock remaining. Initiate purchase orders immediately to avoid patient care disruption.\n\n*Note: AI analysis is running in offline mode. Connect the Groq API for full AI-powered insights.*`;
  }

  if (q.includes('china') || q.includes('api') || q.includes('dependency')) {
    const exposed = ctx.top_api_exposure || [];
    return `**China API Dependency Analysis:**\n\nMedicines with >70% China API exposure:\n${
      exposed.map((r, i) => `${i + 1}. ${r}`).join('\n')
    }\n\nThis represents significant geopolitical risk. Recommend diversifying API sourcing to Indian and European manufacturers for critical medicines.\n\n*Offline mode — connect Groq API for deeper analysis.*`;
  }

  if (q.includes('monsoon') || q.includes('season')) {
    return `**Monsoon Season Impact (Jul–Sep):**\n\nCurrent season: ${ctx.current_season}\n\nDuring monsoon, antibiotic demand typically surges 25–40% due to waterborne disease outbreaks (cholera, typhoid, gastroenteritis). ORS and rehydration supplies see a 50–60% demand increase.\n\n**Recommendations:**\n1. Pre-stock antibiotics (Amoxicillin, Ciprofloxacin) to 120% of normal levels by June\n2. Increase ORS buffer stock by 60%\n3. Monitor weather alerts for flood-prone districts\n\n*Offline mode — connect Groq API for detailed forecasts.*`;
  }

  if (q.includes('who') || q.includes('essential') || q.includes('stockout')) {
    const threats = ctx.stockout_30d || [];
    return `**WHO Essential Medicines — Stockout Risk:**\n\nMedicines with >60% stockout probability in 30 days:\n${
      threats.map((r, i) => `${i + 1}. ${r}`).join('\n') || 'None currently at critical level.'
    }\n\nTotal high-risk medicines: ${ctx.high_risk_count || 0}\n\n*Offline mode — connect Groq API for complete analysis.*`;
  }

  return `**Supply Chain Analysis:**\n\nBased on current dashboard data:\n- ${ctx.high_risk_count || 0} medicines at HIGH risk\n- ${(ctx.stockout_30d || []).length} medicines with >60% stockout probability (30d)\n- ${(ctx.pending_reorders || []).length} pending reorder recommendations\n- Season: ${ctx.current_season || 'Standard'}\n\nFor detailed analysis on this topic, please connect the Groq API key in the backend configuration.\n\n*Running in offline mode with pattern-matched responses.*`;
}
