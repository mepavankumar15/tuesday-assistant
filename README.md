# 🤖 JARVIS — Multi-Agent AI Assistant

## Quick Start

1. Clone the repo and install:
   ```bash
   pip install -e ".[dev]"
   ```

2. Copy and fill in your API keys:
   ```bash
   cp .env.example .env
   ```

3. Run JARVIS:
   ```bash
   streamlit run src/jarvis/app.py
   ```

## Agent Architecture

```
User Query
    │
    ▼
┌─────────────────┐
│   SUPERVISOR    │  ← Grok xAI LLM
│   (Router)      │
└────────┬────────┘
         │  delegates to
    ┌────┴────────────────────────┐
    │         │         │         │
    ▼         ▼         ▼         ▼
Weather    Forex     Music     News
 Agent     Agent     Agent     Agent
    │         │         │         │
    ▼         ▼         ▼         ▼
Open-Meteo ExchRate  YouTube   NewsAPI
 API        API      Search    API
```

## API Keys Required
- **Grok xAI**: https://console.x.ai
- **ExchangeRate-API**: https://www.exchangerate-api.com (free tier: 1500 calls/month)
- **NewsAPI**: https://newsapi.org (free tier: 100 calls/day)
- **Open-Meteo**: https://open-meteo.com/en/docs (No API key required)
