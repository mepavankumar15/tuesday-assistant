"""
Dark-themed Jarvis/Alexa-style CSS for Streamlit.
Inject with: st.markdown(FRIDAY_CSS, unsafe_allow_html=True)
"""

FRIDAY_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

/* ── Base ── */
*, *::before, *::after { box-sizing: border-box; }

html, body, [data-testid="stAppViewContainer"], [data-testid="stMain"] {
    background: #080d1a !important;
    color: #dde6f0 !important;
    font-family: 'Inter', system-ui, sans-serif !important;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: #0b1120 !important;
    border-right: 1px solid #162035 !important;
}
[data-testid="stSidebar"] * { color: #94a3b8 !important; }
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 { color: #60a5fa !important; }

/* ── Chat messages ── */
[data-testid="stChatMessage"] { background: transparent !important; border: none !important; }

/* ── Input ── */
[data-testid="stChatInputContainer"] {
    background: #0b1120 !important;
    border-top: 1px solid #162035 !important;
    padding: 12px 16px !important;
}
textarea[data-testid="stChatInputTextArea"] {
    background: #0f1829 !important;
    border: 1px solid #1e3a5f !important;
    border-radius: 10px !important;
    color: #dde6f0 !important;
    font-family: 'Inter', sans-serif !important;
    transition: border-color 0.2s !important;
}
textarea[data-testid="stChatInputTextArea"]:focus {
    border-color: #3b82f6 !important;
    box-shadow: 0 0 0 3px rgba(59,130,246,0.15) !important;
    outline: none !important;
}

/* ── Agent type badges ── */
.agent-badge {
    display: inline-flex; align-items: center; gap: 6px;
    padding: 3px 10px; border-radius: 20px;
    font-size: 10px; font-weight: 700;
    letter-spacing: 0.08em; text-transform: uppercase;
    margin-bottom: 6px;
}
.badge-weather { background:#0a1f3d; color:#60a5fa; border:1px solid #1d4ed8; }
.badge-forex   { background:#0a2119; color:#34d399; border:1px solid #059669; }
.badge-music   { background:#1a0d38; color:#c084fc; border:1px solid #7c3aed; }
.badge-news    { background:#291500; color:#fb923c; border:1px solid #c2410c; }
.badge-general { background:#161b27; color:#94a3b8; border:1px solid #334155; }
.badge-error   { background:#2a0808; color:#f87171; border:1px solid #991b1b; }

/* ── Music player card ── */
.music-card {
    background: #0f1829;
    border: 1px solid rgba(124,58,237,0.35);
    border-radius: 14px;
    overflow: hidden;
    margin: 10px 0 6px;
    box-shadow: 0 0 24px rgba(124,58,237,0.12);
}
.music-card iframe { width:100%; border:none; display:block; }

/* ── Sidebar example buttons ── */
.stButton > button {
    background: #0f1829 !important;
    color: #94a3b8 !important;
    border: 1px solid #1e2d4a !important;
    border-radius: 8px !important;
    font-size: 13px !important;
    text-align: left !important;
    transition: all 0.15s !important;
}
.stButton > button:hover {
    background: #162035 !important;
    color: #60a5fa !important;
    border-color: #2563eb !important;
    transform: translateX(3px) !important;
}

/* ── FRIDAY header ── */
.friday-header { text-align: center; padding: 18px 0 12px; }
.friday-title {
    font-size: 48px; font-weight: 800; letter-spacing: -0.04em;
    background: linear-gradient(135deg, #60a5fa 0%, #818cf8 50%, #c084fc 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
}
.friday-sub {
    color: #334155; font-size: 11px; letter-spacing: 0.25em;
    text-transform: uppercase; margin-top: 2px;
}

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: #080d1a; }
::-webkit-scrollbar-thumb { background: #1e3a5f; border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: #2563eb; }

/* ── Metric / stat box ── */
[data-testid="stMetric"] {
    background: #0f1829 !important;
    border: 1px solid #162035 !important;
    border-radius: 10px !important;
    padding: 12px 16px !important;
}
[data-testid="stMetricLabel"]  { color: #475569 !important; font-size: 11px !important; }
[data-testid="stMetricValue"]  { color: #60a5fa !important; }

/* ── Divider ── */
hr { border-color: #162035 !important; }

/* ── Spinner ── */
[data-testid="stSpinner"] { color: #3b82f6 !important; }
</style>
"""
