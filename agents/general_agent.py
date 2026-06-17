"""
General / Fallback Agent — powered directly by XAI Grok.
Handles all queries that don't match a specialist: math, coding,
trivia, explanations, general conversation, etc.
"""
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from config.settings import settings
from state.agent_state import AgentState
from utils.logger import logger


_SYSTEM = """You are FRIDAY — a sharp, witty AI assistant (think Jarvis from Iron Man).
You are powered by XAI Grok.

Personality:
- Highly capable but never arrogant
- Concise by default; expand only when the question needs depth
- Use markdown formatting: headers, code blocks, bold for key terms
- Inject a touch of dry wit when appropriate
- If asked who you are: "I'm FRIDAY, your personal AI assistant powered by XAI Grok."

You handle: general knowledge, math, coding help, explanations, trivia, and anything
not covered by the Weather, Forex, Music, or News agents.
"""


def general_agent_node(state: AgentState) -> AgentState:
    logger.info(f"[GeneralAgent] '{state['user_query'][:60]}...'")
    llm = ChatOpenAI(
        api_key=settings.xai_api_key,
        base_url=settings.xai_base_url,
        model=settings.xai_model,
        temperature=0.7,
        max_tokens=1200,
    )
    # Include last 3 turns of conversation history for context
    history = state.get("messages", [])[-6:]
    msgs = [SystemMessage(content=_SYSTEM)] + history + [HumanMessage(content=state["user_query"])]

    try:
        response = llm.invoke(msgs)
        out = response.content
        return {**state, "final_answer": out,
                "agent_response": {"type": "general", "text": out},
                "metadata": {**state.get("metadata", {}), "agent": "general"}}
    except Exception as e:
        logger.error(f"[GeneralAgent] {e}")
        msg = f"⚠️ Something went wrong: `{e}` — please try again."
        return {**state, "final_answer": msg, "agent_response": {"type": "error", "text": msg}}
