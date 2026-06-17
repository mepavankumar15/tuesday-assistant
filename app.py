"""
FRIDAY AI Assistant — Streamlit Application
Run: streamlit run app.py
"""
import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage
from graph.workflow import run_query
from ui.styles import FRIDAY_CSS
from ui.components import render_response, render_routing_sidebar
from utils.logger import logger
from config.settings import settings

# ── Page config ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title=f"{settings.app_name} — AI Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)
st.markdown(FRIDAY_CSS, unsafe_allow_html=True)

# ── Session state ────────────────────────────────────────────────────────────
if "messages"    not in st.session_state: st.session_state.messages    = []
if "lc_history"  not in st.session_state: st.session_state.lc_history  = []
if "last_meta"   not in st.session_state: st.session_state.last_meta   = {}
if "prefill"     not in st.session_state: st.session_state.prefill     = None

# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"""
    <div style="text-align:center;padding:12px 0 20px">
      <div style="font-size:40px">🤖</div>
      <div style="font-size:20px;font-weight:800;color:#60a5fa;letter-spacing:-0.03em">{settings.app_name.upper()}</div>
      <div style="font-size:10px;color:#334155;letter-spacing:0.2em;text-transform:uppercase">
        AI ASSISTANT · XAI GROK
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("#### ⚡ What I can do")
    for icon, cap, desc in [
        ("🌤️", "Weather",   "Conditions & forecast for any city"),
        ("💱", "Forex",     "Live currency rates & conversion"),
        ("🎵", "Music",     "Search & play YouTube music"),
        ("📰", "News",      "Headlines & topic search"),
        ("🤖", "General",   "Anything else via XAI Grok"),
    ]:
        st.markdown(f"""
        <div style="padding:7px 0;border-bottom:1px solid #0f1829">
          <span style="font-size:15px">{icon}</span>
          <span style="color:#93c5fd;font-weight:600;margin-left:8px">{cap}</span>
          <div style="color:#64748b;font-size:11px;margin-left:28px">{desc}</div>
        </div>
        """, unsafe_allow_html=True)

    if st.session_state.last_meta:
        render_routing_sidebar(st.session_state.last_meta)

# ── Main chat area ───────────────────────────────────────────────────────────
st.markdown("<div class='friday-header'>", unsafe_allow_html=True)
st.markdown("<div class='friday-title'>FRIDAY</div>", unsafe_allow_html=True)
st.markdown("<div class='friday-sub'>Intelligent Assistant</div>", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

# Render chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        if msg["role"] == "assistant":
            if "agent_response" in msg and msg["agent_response"]:
                render_response(msg["agent_response"], msg["content"])
            else:
                st.markdown(msg["content"])
        else:
            st.markdown(msg["content"])

# ── Input handling ───────────────────────────────────────────────────────────
if query := st.chat_input("Ask FRIDAY..."):
    # Append user message
    st.session_state.messages.append({"role": "user", "content": query})
    st.session_state.lc_history.append(HumanMessage(content=query))
    
    with st.chat_message("user"):
        st.markdown(query)

    # FRIDAY thinking and responding
    with st.chat_message("assistant"):
        with st.spinner("Processing..."):
            try:
                # Run the LangGraph workflow
                result_state = run_query(query, st.session_state.lc_history)
                
                final_answer = result_state.get("final_answer", "")
                agent_resp = result_state.get("agent_response", {})
                meta = result_state.get("metadata", {})
                
                # Render the response
                if agent_resp:
                    render_response(agent_resp, final_answer)
                else:
                    st.markdown(final_answer)
                
                # Update session state
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": final_answer,
                    "agent_response": agent_resp
                })
                st.session_state.lc_history.append(AIMessage(content=final_answer))
                st.session_state.last_meta = meta
                
            except Exception as e:
                error_msg = f"⚠️ An error occurred: `{e}`"
                render_response({"type": "error", "text": error_msg}, error_msg)
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": error_msg,
                    "agent_response": {"type": "error", "text": error_msg}
                })
