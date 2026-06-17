"""
Weather Specialist Agent.
ReAct loop using LangChain tool-calling agent over weather_tools.
"""
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from tools.weather_tools import get_current_weather, get_weather_forecast
from config.settings import settings
from state.agent_state import AgentState
from utils.logger import logger


_SYSTEM = """You are FRIDAY's Weather Specialist with access to real-time weather data.

Rules:
- Temperatures always in Celsius (°C)
- Mention: temperature, feels like, humidity, wind, sky condition
- For forecasts show each day clearly as min/max range
- Keep tone friendly and practical ("Great day for a run!" / "Carry an umbrella!")
- If the city can't be found, ask for clarification

Tools available: get_current_weather, get_weather_forecast
"""

_TOOLS = [get_current_weather, get_weather_forecast]


def weather_agent_node(state: AgentState) -> AgentState:
    logger.info(f"[WeatherAgent] '{state['user_query']}'")
    llm = ChatOpenAI(api_key=settings.xai_api_key, base_url=settings.xai_base_url,
                     model=settings.xai_model, temperature=0.2)
    agent = create_react_agent(llm, tools=_TOOLS, prompt=_SYSTEM)
    try:
        response = agent.invoke({"messages": [("user", state["user_query"])]})
        out = response["messages"][-1].content
        return {**state, "final_answer": out,
                "agent_response": {"type": "weather", "text": out},
                "metadata": {**state.get("metadata", {}), "agent": "weather"}}
    except Exception as e:
        logger.error(f"[WeatherAgent] {e}")
        msg = f"⚠️ Couldn't fetch weather data right now. Please try again.\n`{e}`"
        return {**state, "final_answer": msg, "agent_response": {"type": "error", "text": msg}}
