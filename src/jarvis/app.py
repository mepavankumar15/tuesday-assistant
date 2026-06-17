"""
Streamlit UI for JARVIS Assistant.
Provides a dark, glassmorphic UI with chat, voice input, and live data cards.
"""
import os
import streamlit as st
from dotenv import load_dotenv
from jarvis.crew import JarvisCrew
import requests
import json

# Load environment variables
load_dotenv()

# Set page config
st.set_page_config(layout="wide", page_title=os.getenv("APP_TITLE", "JARVIS Assistant"), page_icon="🤖")

# --- CSS Injection ---
CSS = """
<style>
/* Import fonts */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=JetBrains+Mono&display=swap');

/* Main app background */
.stApp {
    background-color: #0a0a0f !important;
    font-family: 'Inter', sans-serif !important;
}
.stApp [data-testid="stHeader"] {
    background-color: transparent !important;
}

/* Glass cards */
.glass-card {
    background: rgba(255, 255, 255, 0.04);
    border: 1px solid rgba(255, 255, 255, 0.08);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border-radius: 16px;
    padding: 20px;
    margin-bottom: 20px;
    color: #f0f4ff;
    transition: transform 0.2s ease, border-color 0.2s ease;
}
.glass-card:hover {
    border-color: rgba(0, 212, 255, 0.3);
    transform: translateY(-2px);
}

/* Headings and Text */
h1, h2, h3, h4, h5, h6 {
    color: #f0f4ff !important;
    font-family: 'Inter', sans-serif !important;
}
p, span, div {
    color: #8892a4;
}
.primary-text {
    color: #f0f4ff;
}

/* Accent colors */
.cyan-glow {
    color: #00d4ff;
    text-shadow: 0 0 10px rgba(0, 212, 255, 0.5);
}
.purple-badge {
    background-color: rgba(124, 58, 237, 0.2);
    color: #7c3aed;
    padding: 4px 8px;
    border-radius: 8px;
    font-size: 0.8rem;
    font-weight: 600;
}

/* Status indicator */
.status-dot {
    height: 12px;
    width: 12px;
    background-color: #10b981;
    border-radius: 50%;
    display: inline-block;
    box-shadow: 0 0 8px #10b981;
    animation: pulse 2s infinite;
}
@keyframes pulse {
    0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7); }
    70% { transform: scale(1); box-shadow: 0 0 0 6px rgba(16, 185, 129, 0); }
    100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); }
}

/* Chat Input */
[data-testid="stChatInput"] {
    background-color: rgba(255, 255, 255, 0.04) !important;
    border: 1px solid rgba(255, 255, 255, 0.08) !important;
    border-radius: 12px !important;
    color: #f0f4ff !important;
}
[data-testid="stChatInput"]:focus-within {
    border-color: #00d4ff !important;
    box-shadow: 0 0 15px rgba(0, 212, 255, 0.2) !important;
}

/* Quick Action Chips */
.stButton button {
    background: rgba(255, 255, 255, 0.05) !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
    color: #f0f4ff !important;
    border-radius: 20px !important;
    transition: all 0.3s ease !important;
}
.stButton button:hover {
    background: rgba(0, 212, 255, 0.1) !important;
    border-color: #00d4ff !important;
    color: #00d4ff !important;
    box-shadow: 0 0 10px rgba(0, 212, 255, 0.2) !important;
}

/* Prevent Streamlit from dimming/tinting the screen during processing */
[data-testid="stAppViewContainer"], 
.stApp, 
[data-testid="stMainBlockContainer"], 
.stChatInput, 
.stChatInput textarea {
    filter: none !important;
    opacity: 1 !important;
    transition: none !important;
}
[data-testid="stStatusWidget"] {
    visibility: hidden;
}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)


# --- Initialization ---
if "messages" not in st.session_state:
    st.session_state.messages = []
    # Initial greeting
    st.session_state.messages.append({
        "role": "assistant",
        "content": "Hello! I am JARVIS. How can I assist you today?"
    })

if "crew" not in st.session_state:
    with st.spinner("Initializing JARVIS..."):
        st.session_state.crew = JarvisCrew()

if "youtube_url" not in st.session_state:
    st.session_state.youtube_url = None

if "city" not in st.session_state:
    st.session_state.city = os.getenv("DEFAULT_CITY", "Hyderabad")
    
if "currency" not in st.session_state:
    st.session_state.currency = os.getenv("DEFAULT_BASE_CURRENCY", "USD")

# --- Helper Functions ---
def get_live_weather(city: str):
    """Fetch live weather for the card (using open-meteo without crew)."""
    try:
        geo_resp = requests.get(
            f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1", 
            timeout=5
        ).json()
        if not geo_resp.get("results"): return None
        
        lat = geo_resp["results"][0]["latitude"]
        lon = geo_resp["results"][0]["longitude"]
        
        weather = requests.get(
            f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,wind_speed_10m",
            timeout=5
        ).json()
        return {
            "temp": weather["current"]["temperature_2m"],
            "wind": weather["current"]["wind_speed_10m"]
        }
    except Exception:
        return None

def get_live_forex(base: str):
    """Fetch live forex rates for the card."""
    api_key = os.getenv("FOREX_API_KEY")
    if not api_key or api_key == "your_exchangerate_api_key_here":
        return None
    try:
        url = f"https://v6.exchangerate-api.com/v6/{api_key}/latest/{base}"
        data = requests.get(url, timeout=5).json()
        return data.get("conversion_rates", {})
    except Exception:
        return None


# --- UI Layout ---

# Header
st.markdown("""
<div style="display: flex; justify-content: space-between; align-items: center; padding: 10px 0 20px 0;">
    <div>
        <h1 style="margin: 0; padding: 0;"><span class="cyan-glow">🤖 JARVIS</span></h1>
    </div>
    <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.9rem; color: #8892a4;">
        Status: Online <span class="status-dot"></span>
    </div>
</div>
""", unsafe_allow_html=True)

# 3 Columns
col_left, col_main, col_right = st.columns([1, 2.5, 1], gap="large")

# --- Left Column: Live Data ---
with col_left:
    st.markdown("<h3 style='font-size: 1.2rem; margin-bottom: 15px;'>LIVE DATA</h3>", unsafe_allow_html=True)
    
    # Weather Card
    weather_data = get_live_weather(st.session_state.city)
    if weather_data:
        st.markdown(f"""
        <div class="glass-card">
            <h4 style="margin-top: 0; display: flex; align-items: center; gap: 8px;">🌤 {st.session_state.city} Weather</h4>
            <div style="font-size: 2rem; font-weight: 600; color: #f0f4ff;">{weather_data['temp']}°C</div>
            <div style="color: #8892a4; font-size: 0.9rem;">Wind: {weather_data['wind']} km/h</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="glass-card">
            <h4 style="margin-top: 0;">🌤 Weather</h4>
            <div style="color: #8892a4; font-size: 0.9rem;">Data unavailable</div>
        </div>
        """, unsafe_allow_html=True)

    # Forex Card
    forex_data = get_live_forex(st.session_state.currency)
    if forex_data:
        pairs = ["INR", "EUR", "GBP", "JPY", "BTC"]
        forex_html = "".join([
            f"<div style='display: flex; justify-content: space-between; margin-bottom: 5px;'>"
            f"<span>{st.session_state.currency}/{p}</span> <span style='color: #f0f4ff;'>{forex_data.get(p, 'N/A')}</span></div>"
            for p in pairs if p in forex_data
        ])
        st.markdown(f"""
        <div class="glass-card">
            <h4 style="margin-top: 0;">💱 Forex Rates</h4>
            {forex_html}
        </div>
        """, unsafe_allow_html=True)
    else:
         st.markdown("""
        <div class="glass-card">
            <h4 style="margin-top: 0;">💱 Forex Rates</h4>
            <div style="color: #8892a4; font-size: 0.9rem;">API Key missing or error</div>
        </div>
        """, unsafe_allow_html=True)

    # YouTube Player (if active)
    if st.session_state.youtube_url:
        st.markdown("""
        <div class="glass-card" style="padding: 10px;">
            <h4 style="margin-top: 0; margin-bottom: 10px; padding: 10px;">🎵 Now Playing</h4>
        </div>
        """, unsafe_allow_html=True)
        st.video(st.session_state.youtube_url)


# --- Right Column: Agent Monitor & Settings ---
with col_right:
    st.markdown("<h3 style='font-size: 1.2rem; margin-bottom: 15px;'>AGENT MONITOR</h3>", unsafe_allow_html=True)
    
    st.markdown("""
    <div class="glass-card">
        <div style='margin-bottom: 10px; display: flex; align-items: center; justify-content: space-between;'>
            <span>Supervisor</span> <span class="purple-badge">Active</span>
        </div>
        <div style='margin-bottom: 10px; display: flex; align-items: center; justify-content: space-between; color: #8892a4;'>
            <span>Weather Agent</span> <span>Standby</span>
        </div>
        <div style='margin-bottom: 10px; display: flex; align-items: center; justify-content: space-between; color: #8892a4;'>
            <span>Forex Agent</span> <span>Standby</span>
        </div>
        <div style='margin-bottom: 10px; display: flex; align-items: center; justify-content: space-between; color: #8892a4;'>
            <span>Music Agent</span> <span>Standby</span>
        </div>
        <div style='margin-bottom: 10px; display: flex; align-items: center; justify-content: space-between; color: #8892a4;'>
            <span>News Agent</span> <span>Standby</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    with st.expander("⚙️ Settings"):
        st.session_state.city = st.text_input("Default City", value=st.session_state.city)
        st.session_state.currency = st.text_input("Base Currency", value=st.session_state.currency)


# --- Main Column: Chat Interface ---
with col_main:
    # Quick action chips
    c1, c2, c3, c4 = st.columns(4)
    quick_query = None
    with c1: 
        if st.button("🌤 Weather", use_container_width=True): quick_query = f"What is the weather in {st.session_state.city}?"
    with c2: 
        if st.button("💱 Forex", use_container_width=True): quick_query = f"What is the exchange rate for {st.session_state.currency} to INR?"
    with c3: 
        if st.button("🎵 Play music", use_container_width=True): quick_query = "Play top hits on youtube"
    with c4: 
        if st.button("📰 News", use_container_width=True): quick_query = "What is the latest news in technology?"

    # Chat history container
    chat_container = st.container(height=500)
    with chat_container:
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

    # Process Input
    prompt = st.chat_input("Type your message here...", key="text_input")
    
    user_input = prompt or quick_query
    
    if user_input:
        # Display user message
        st.session_state.messages.append({"role": "user", "content": user_input})
        with chat_container:
            with st.chat_message("user"):
                st.markdown(user_input)

        # Process with CrewAI
        with chat_container:
            with st.chat_message("assistant"):
                with st.status("JARVIS is thinking...", expanded=True) as status:
                    st.write("Supervisor analyzing intent...")
                    try:
                        result = st.session_state.crew.run(user_input)
                        response_text = result["response"]
                        
                        # Hack to check if music tool was called and returned a url
                        if "youtube.com" in response_text or "youtu.be" in response_text:
                            import re
                            urls = re.findall(r'(https?://[^\s]+)', response_text)
                            for url in urls:
                                if "youtube.com" in url or "youtu.be" in url:
                                    st.session_state.youtube_url = url
                                    break
                                    
                        status.update(label="Response ready", state="complete", expanded=False)
                    except Exception as e:
                        response_text = f"I encountered an error: {str(e)}"
                        status.update(label="Error occurred", state="error", expanded=False)

                st.markdown(response_text)

        # Add assistant response to history
        st.session_state.messages.append({
            "role": "assistant", 
            "content": response_text
        })
        st.rerun()

def main():
    pass

if __name__ == "__main__":
    main()
