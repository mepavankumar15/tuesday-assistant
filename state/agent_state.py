"""
The single shared TypedDict that flows through every node in the LangGraph StateGraph.

Data flow:
  User Input → [supervisor sets next_agent] → [specialist fills agent_response + final_answer] → UI
  
The `messages` field uses LangGraph's add_messages reducer (append-only, never overwrites).
Everything else is a simple last-write-wins field.
"""
from typing import TypedDict, Annotated, Optional, Any
from langgraph.graph.message import add_messages


class AgentState(TypedDict):
    # Full conversation history (LangChain BaseMessage objects, append-only)
    messages: Annotated[list, add_messages]

    # The cleaned/extracted user query (may be rewritten by supervisor)
    user_query: str

    # Which node to visit next — set by supervisor, read by conditional edge
    # Values: "weather" | "forex" | "music" | "news" | "general"
    next_agent: str

    # Structured payload from the specialist agent (dict, type-tagged)
    # e.g. {"type": "music", "data": {...}} or {"type": "weather", "text": "..."}
    agent_response: Optional[dict[str, Any]]

    # The final human-readable answer string (rendered in Streamlit)
    final_answer: str

    # Routing metadata: confidence score, agent name, timestamps, errors
    metadata: dict[str, Any]
