"""
Assembles the full LangGraph StateGraph.

Graph topology:

    ┌─────────────────────────────────────────────┐
    │                START                        │
    └───────────────────┬─────────────────────────┘
                        ▼
                  [ supervisor ]          ← classifies intent
                        │
          ┌─────────────┼──────────────┐
          ▼             ▼              ▼
       weather        forex          music
          │             │              │
          └──────┬──────┘              │
                 │         ┌───────────┘
                 ▼         ▼
              news      general
                 │         │
                 └────┬────┘
                      ▼
                    END
"""
from langgraph.graph import StateGraph, START, END
from state.agent_state import AgentState
from agents.supervisor import supervisor_node, route_after_supervisor
from agents.weather_agent import weather_agent_node
from agents.forex_agent import forex_agent_node
from agents.music_agent import music_agent_node
from agents.news_agent import news_agent_node
from agents.general_agent import general_agent_node
from utils.logger import logger


def build_workflow():
    """Compile and return the runnable LangGraph StateGraph."""
    logger.info("Assembling LangGraph StateGraph...")

    g = StateGraph(AgentState)

    # ── Nodes ──────────────────────────────────────────────────────────────
    g.add_node("supervisor", supervisor_node)
    g.add_node("weather",    weather_agent_node)
    g.add_node("forex",      forex_agent_node)
    g.add_node("music",      music_agent_node)
    g.add_node("news",       news_agent_node)
    g.add_node("general",    general_agent_node)

    # ── Entry ───────────────────────────────────────────────────────────────
    g.add_edge(START, "supervisor")

    # ── Conditional routing from supervisor ─────────────────────────────────
    g.add_conditional_edges(
        "supervisor",
        route_after_supervisor,
        {"weather": "weather", "forex": "forex",
         "music": "music", "news": "news", "general": "general"},
    )

    # ── All specialists go to END ────────────────────────────────────────────
    for node in ("weather", "forex", "music", "news", "general"):
        g.add_edge(node, END)

    graph = g.compile()
    logger.info("StateGraph compiled ✓")
    return graph


# Module-level singleton — built once at import time
friday_graph = build_workflow()


def run_query(user_query: str, chat_history: list = None) -> AgentState:
    """
    Public API: run any user query through the full agent graph.

    Args:
        user_query:   Raw user text input
        chat_history: List of LangChain BaseMessage objects (conversation so far)

    Returns:
        Final AgentState after graph execution completes
    """
    return friday_graph.invoke({
        "messages":      chat_history or [],
        "user_query":    user_query,
        "next_agent":    "",
        "agent_response": None,
        "final_answer":  "",
        "metadata":      {},
    })
