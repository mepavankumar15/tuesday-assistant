"""
Grok Assistant — Streamlit Chat UI
Run: streamlit run streamlit_app.py
"""
import json
import streamlit as st
from agent import run_agent

# ─── Page Config ───────────────────────────────────────────
st.set_page_config(
    page_title="Alex Assistant",
    page_icon="🤖",
    layout="centered",
    initial_sidebar_state="expanded",
)

# ─── Custom CSS ────────────────────────────────────────────
st.markdown("""
<style>
    /* Dark-ish chat area */
    .stApp {
        background: linear-gradient(135deg, #0f0f23 0%, #1a1a3e 50%, #0f0f23 100%);
    }
    /* Remove extra padding */
    .block-container { padding-top: 2rem; }
    /* Chat input styling */
    .stChatInput textarea {
        background-color: #1e1e3f !important;
        color: #e0e0ff !important;
        border: 1px solid #4a4a8a !important;
    }
    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #12122b;
    }
    /* User message */
    .stChatMessage[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
        background-color: #1e1e3f;
        border-radius: 12px;
        border: 1px solid #2a2a5a;
    }
    /* Assistant message */
    .stChatMessage[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) {
        background-color: #16163a;
        border-radius: 12px;
        border: 1px solid #2a2a5a;
    }
</style>
""", unsafe_allow_html=True)

# ─── Sidebar ───────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🤖 Alex Assistant")
    st.caption("Alexa-like AI • Multi-Agent System")
    st.divider()

    st.markdown("### 🛠️ Specialist Agents")
    st.markdown("""
    - 🎵 **Media Specialist** — search & play YouTube
    - 🌤️/💱 **Finance & Weather Specialist** — live weather & forex
    - 📰 **News Specialist** — current events & headlines
    """)

    st.divider()

    st.markdown("### 💡 Try saying")
    st.code("Play Coldplay Yellow", language=None)
    st.code("Weather in Mumbai", language=None)
    st.code("Convert 500 USD to EUR", language=None)
    st.code("Latest news on AI", language=None)

    st.divider()

    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# ─── Chat State ────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []

# ─── Header ────────────────────────────────────────────────
st.markdown(
    "<h1 style='text-align:center; color:#7c7cff;'>🤖 Alex Assistant</h1>"
    "<p style='text-align:center; color:#888; margin-bottom:1.5rem;'>"
    "Ask me anything — weather, news, music, currencies, or just chat!</p>",
    unsafe_allow_html=True,
)

# ─── Display Chat History ──────────────────────────────────
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

        # Render YouTube button if present
        if msg["role"] == "assistant" and msg.get("youtube"):
            yt = msg["youtube"]
            vid = yt.get("video_id", "")
            title = yt.get("title", "Watch on YouTube")
            st.link_button(
                f"▶ Play: {title}",
                f"https://www.youtube.com/watch?v={vid}",
                use_container_width=True,
            )

# ─── Chat Input ────────────────────────────────────────────
if prompt := st.chat_input("Ask Alex something..."):
    # Show user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Build history for agent (excluding youtube metadata)
    chat_history = [
        {"role": m["role"], "content": m["content"]}
        for m in st.session_state.messages[:-1]  # exclude current message
    ]

    # Get agent response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                response = run_agent(prompt, chat_history)
            except Exception as e:
                response = f"❌ Error: {str(e)}"

        # Parse YouTube action
        youtube_action = None
        display_text = response

        if '{"action": "play_youtube"' in response:
            try:
                start = response.rfind('{"action": "play_youtube"')
                end = response.find("}", start) + 1
                action_json = response[start:end]
                youtube_action = json.loads(action_json)
                display_text = response[:start].strip()
            except json.JSONDecodeError:
                pass

        st.markdown(display_text)

        if youtube_action:
            vid = youtube_action.get("video_id", "")
            title = youtube_action.get("title", "Watch on YouTube")
            st.link_button(
                f"▶ Play: {title}",
                f"https://www.youtube.com/watch?v={vid}",
                use_container_width=True,
            )

    # Save to state
    st.session_state.messages.append({
        "role": "assistant",
        "content": display_text,
        "youtube": youtube_action,
    })
