"""
Supervisor Agent — the central router of the FRIDAY StateGraph.

Uses XAI Grok at temperature=0 to classify the user's intent into one of five
routing categories. Returns a routing JSON dict (not a user-facing answer).

Graph role: START → supervisor → [conditional edge] → specialist node → END
"""
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from config.settings import settings
from state.agent_state import AgentState
from utils.logger import logger
import json


ROUTE_VALUES = {"weather", "forex", "music", "news", "general"}

SYSTEM_PROMPT = f"""
You are the routing supervisor for {settings.app_name}, an AI assistant.
Your ONLY job: read the user's query and output ONE routing decision as JSON.
DO NOT answer the query. DO NOT add explanation. ONLY output raw JSON.

Route to exactly one of these agents:
  "weather"  → weather conditions, temperature, forecast, rain, climate, humidity
  "forex"    → exchange rates, currency conversion, money amounts, USD/INR/EUR/GBP/JPY etc.
  "music"    → play music, songs, artists, bands, YouTube, playlist, album
  "news"     → news, headlines, current events, sports results, politics, tech news today
  "general"  → everything else: math, coding, facts, trivia, explanations, general knowledge

RESPOND ONLY with this exact JSON schema, no markdown fences:
{
  "route": "<one of: weather | forex | music | news | general>",
  "extracted_query": "<cleaned, intent-specific version of the user query>",
  "confidence": <float 0.0 to 1.0>
}

Examples:
  "whats the weather in mumbai tmrw"
  → {"route":"weather","extracted_query":"weather forecast Mumbai tomorrow","confidence":0.98}

  "play some old hindi songs"
  → {"route":"music","extracted_query":"old Hindi songs","confidence":0.97}

  "1 dollar to rupees"
  → {"route":"forex","extracted_query":"convert 1 USD to INR","confidence":0.99}

  "latest ipl news"
  → {"route":"news","extracted_query":"IPL cricket news","confidence":0.96}

  "what is the speed of light"
  → {"route":"general","extracted_query":"speed of light","confidence":0.99}
"""


def _build_llm() -> ChatOpenAI:
    return ChatOpenAI(
        api_key=settings.xai_api_key,
        base_url=settings.xai_base_url,
        model=settings.xai_model,
        temperature=0.0,
        max_tokens=150,
    )


def supervisor_node(state: AgentState) -> AgentState:
    """
    Supervisor node function — called by LangGraph as a graph node.
    Reads user_query, sets next_agent and updates metadata.
    """
    query = state["user_query"]
    logger.info(f"[Supervisor] Routing: '{query[:70]}...' " if len(query) > 70 else
                f"[Supervisor] Routing: '{query}'")

    try:
        llm = _build_llm()
        response = llm.invoke([
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=query),
        ])
        raw = response.content.strip()
        routing: dict = json.loads(raw)

        route = routing.get("route", "general")
        if route not in ROUTE_VALUES:
            route = "general"

        extracted = routing.get("extracted_query", query)
        confidence = float(routing.get("confidence", 0.8))

        logger.info(f"[Supervisor] → '{route}' (confidence: {confidence:.0%})")

        return {
            **state,
            "next_agent": route,
            "user_query": extracted,
            "metadata": {
                **state.get("metadata", {}),
                "route": route,
                "confidence": confidence,
                "original_query": query,
            },
        }

    except (json.JSONDecodeError, Exception) as e:
        logger.warning(f"[Supervisor] Routing failed ({e}), defaulting to 'general'")
        return {
            **state,
            "next_agent": "general",
            "metadata": {**state.get("metadata", {}), "route": "general",
                         "confidence": 0.5, "supervisor_error": str(e)},
        }


def route_after_supervisor(state: AgentState) -> str:
    """
    Conditional edge function: tells LangGraph which node to run next.
    This is the only function that reads next_agent from state.
    """
    return state.get("next_agent", "general")
