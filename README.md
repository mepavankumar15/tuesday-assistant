# Grok Assistant

An Alexa-like AI chat assistant powered by xAI's Grok model.

## Features
- Voice input (microphone) + text input
- Text-to-speech responses
- YouTube search & playback
- Live weather by city
- Forex exchange rates
- General AI conversation

## Quick Start

1. Copy the example env file and fill in your API keys:
   ```
   cp .env.example .env
   ```

2. Required API keys:
   - **XAI_API_KEY** — from https://console.x.ai
   - **YOUTUBE_API_KEY** — from https://console.cloud.google.com (YouTube Data API v3)
   - **EXCHANGERATE_API_KEY** — from https://www.exchangerate-api.com
   - **NEWS_API_KEY** — from https://newsapi.org/register (free tier: 100 requests/day)
   - **Weather** uses Open-Meteo (free, no API key needed)

3. Run with Docker:
   ```
   docker compose up --build
   ```

4. Open http://localhost in your browser.

## Local Development (without Docker)

**Backend:**
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

## Example Prompts
- "Play Coldplay Yellow"
- "What's the weather in Mumbai?"
- "Convert 500 USD to EUR"
- "What's the capital of Australia?"
- "Play some lofi study music"
