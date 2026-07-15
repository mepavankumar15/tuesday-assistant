# Alex Assistant (Multi-Agent System)

An Alexa-like AI assistant powered by xAI's Grok model and built with a **Hierarchical Supervisor-Specialist Multi-Agent Architecture**.
Available as a **CLI terminal chatbot** and a **Streamlit web app**.

## Multi-Agent Architecture
Instead of a single monolithic agent, **Alex Assistant** uses a coordinating **Supervisor Agent** that delegates domain queries to autonomous specialized sub-agents:
- 🎵 **Media Specialist Agent**: Autonomous agent managing YouTube music/video search & playback links.
- 🌤️/💱 **Finance & Weather Specialist Agent**: Autonomous agent managing live weather conditions & foreign exchange rates.
- 📰 **News Specialist Agent**: Autonomous agent managing topic news search & top daily headlines (`NewsAPI.org`).
- 💬 **Supervisor / Orchestrator Agent**: Routes queries, synthesizes multi-specialist outputs, and handles conversational AI directly.

## Quick Start

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Set up API keys

Create a `.env` file (or copy from `.env.example`) with:

| Key | Source |
|-----|--------|
| `XAI_API_KEY` | https://console.x.ai |
| `YOUTUBE_API_KEY` | https://console.cloud.google.com (YouTube Data API v3) |
| `EXCHANGERATE_API_KEY` | https://www.exchangerate-api.com |
| `NEWS_API_KEY` | https://newsapi.org/register (free: 100 req/day) |
| Weather | Open-Meteo — free, no key needed |

### 3. Run

**CLI Mode (terminal chatbot):**
```bash
python cli.py
```

**Streamlit Mode (web UI):**
```bash
streamlit run streamlit_app.py
```
*(If `streamlit` command is not recognized on Windows, run `python -m streamlit run streamlit_app.py`)*

### 4. Stopping & Troubleshooting

**Stopping the App:**
- Press `Ctrl + C` in your terminal to stop either `cli.py` or `streamlit_app.py`.

**If `Ctrl + C` is unresponsive on Windows:**
1. Press `Ctrl + Pause/Break` inside the terminal window.
2. Or open a new terminal window and run:
   ```powershell
   taskkill /IM python.exe /F
   ```

## Docker

```bash
docker compose up --build
```
Opens Streamlit at **http://localhost:8501**.

## Example Prompts
- "Play Coldplay Yellow"
- "What's the weather in Mumbai?"
- "Convert 500 USD to EUR"
- "Latest news on AI"
- "Top technology headlines"
- "What's the capital of Australia?"

## Project Structure
```
grok-assistant/
├── cli.py                     ← Terminal chatbot
├── streamlit_app.py           ← Streamlit web UI
├── agent.py                   ← Facade entry point exporting run_agent
├── agents/                    ← Multi-Agent Layer (AI Reasoning & Orchestration)
│   ├── supervisor_agent.py    ← Top-level Orchestrator
│   ├── media_agent.py         ← YouTube/Music Specialist Sub-Agent
│   ├── finance_weather_agent.py ← Weather & Forex Specialist Sub-Agent
│   ├── news_agent.py          ← News Specialist Sub-Agent
│   └── llm.py                 ← Shared Grok LLM factory
├── tools/                     ← Physical Tools Layer (Raw API Connectors)
│   ├── youtube_tool.py
│   ├── weather_tool.py
│   ├── forex_tool.py
│   └── news_tool.py
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── .env
```
