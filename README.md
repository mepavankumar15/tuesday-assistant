# Grok Assistant

An Alexa-like AI assistant powered by xAI's Grok model.
Available as a **CLI terminal chatbot** and a **Streamlit web app**.

## Features
- 🎵 YouTube search & playback links
- 🌤️ Live weather by city
- 💱 Forex exchange rates
- 📰 News search & top headlines (NewsAPI.org)
- 💬 General AI conversation

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
├── cli.py              ← Terminal chatbot
├── streamlit_app.py    ← Streamlit web UI
├── agent.py            ← LangChain agent (Grok LLM)
├── tools/
│   ├── youtube_tool.py
│   ├── weather_tool.py
│   ├── forex_tool.py
│   └── news_tool.py
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── .env
```
