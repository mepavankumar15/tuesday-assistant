"""
Forex / Currency Exchange Specialist Agent.
ReAct loop using LangChain tool-calling agent over forex_tools.
"""
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from tools.forex_tools import get_exchange_rate, convert_currency
from config.settings import settings
from state.agent_state import AgentState
from utils.logger import logger


_SYSTEM = """You are FRIDAY's Currency & Forex Specialist with live exchange rate access.

Rules:
- Use standard ISO 4217 currency codes (USD, EUR, INR, GBP, JPY, AED, SGD...)
- If user gives amount → use convert_currency tool
- If no amount given → use get_exchange_rate tool  
- Format large converted numbers with commas (e.g. ₹83,450.00)
- Always state the rate source timestamp so the user knows data freshness
- Be precise — people make financial decisions on this data

Tools available: get_exchange_rate, convert_currency
"""

_TOOLS = [get_exchange_rate, convert_currency]


def forex_agent_node(state: AgentState) -> AgentState:
    logger.info(f"[ForexAgent] '{state['user_query']}'")
    llm = ChatOpenAI(api_key=settings.xai_api_key, base_url=settings.xai_base_url,
                     model=settings.xai_model, temperature=0.1)
    agent = create_react_agent(llm, tools=_TOOLS, prompt=_SYSTEM)
    try:
        response = agent.invoke({"messages": [("user", state["user_query"])]})
        out = response["messages"][-1].content
        return {**state, "final_answer": out,
                "agent_response": {"type": "forex", "text": out},
                "metadata": {**state.get("metadata", {}), "agent": "forex"}}
    except Exception as e:
        logger.error(f"[ForexAgent] {e}")
        msg = f"⚠️ Couldn't fetch exchange rates right now.\n`{e}`"
        return {**state, "final_answer": msg, "agent_response": {"type": "error", "text": msg}}
