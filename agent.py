"""
Main Agent Facade (`agent.py`)
Re-exports the top-level Supervisor Agent from `agents/supervisor_agent.py` so that
`cli.py` and `streamlit_app.py` can continue importing `run_agent` seamlessly.

See `agents/` folder for individual specialist sub-agents:
- `agents/supervisor_agent.py`: Top-level orchestrator
- `agents/media_agent.py`: YouTube/Music specialist
- `agents/finance_weather_agent.py`: Weather & Forex specialist
- `agents/news_agent.py`: NewsAPI specialist
"""
from agents.supervisor_agent import run_agent, supervisor_executor as agent_executor

__all__ = ["run_agent", "agent_executor"]
