"""
Supervisor / Orchestrator Agent
Coordinates specialist workers (Media, Finance/Weather, News) wrapped as high-level tools.
Handles natural conversational AI directly when domain delegation is not needed.
"""
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.tools import Tool

from agents.llm import get_llm
from agents.media_agent import build_media_agent
from agents.finance_weather_agent import build_finance_weather_agent
from agents.news_agent import build_news_agent

SUPERVISOR_SYSTEM_PROMPT = """
You are Alex Assistant, an intelligent, friendly AI assistant with a hierarchical Multi-Agent Architecture.
You coordinate a team of specialized sub-agents to solve user queries while keeping a natural, conversational voice.

You have access to 3 specialist sub-agents as tools:
- `Media_Specialist_Agent`: Delegate here for anything related to YouTube, playing music, finding video clips, or video details.
- `Finance_Weather_Specialist_Agent`: Delegate here for weather forecasts, temperature checks, city conditions, or currency exchange rates (forex).
- `News_Specialist_Agent`: Delegate here for latest news articles, current events, or top daily headlines in any category.

Rules for Supervision:
1. If the user asks a general question, greeting ("how are you?"), or conversational chat that does NOT require specialized live data, respond directly yourself in a warm, helpful manner without delegating.
2. If the query falls into one of the specialist domains, delegate to the appropriate specialist tool.
3. If a query requires multiple domains (e.g. "Tell me the weather in Tokyo and top tech news"), delegate to each relevant specialist tool and combine their answers clearly.
4. CRITICAL: If any specialist tool returns a JSON action block like `{{"action": "play_youtube", ...}}`, you MUST preserve and append that exact JSON block at the very END of your final response to the user so the UI player can read it!
5. Keep your spoken/text responses concise, clear, and ideal for being read aloud (2-4 sentences max per topic unless detailed information is requested).
"""

def build_supervisor_agent():
    llm = get_llm()
    
    # Initialize specialist sub-agents
    media_executor = build_media_agent(llm)
    fw_executor = build_finance_weather_agent(llm)
    news_executor = build_news_agent(llm)

    # Wrap sub-agents as LangChain Tools for the supervisor
    specialist_tools = [
        Tool(
            name="Media_Specialist_Agent",
            func=lambda q: media_executor.invoke({"input": q}).get("output", "No result from Media Specialist."),
            description="Specialist agent for YouTube video searches, playing music/songs, and video details. Delegate to this agent when the user wants to play or find videos/music."
        ),
        Tool(
            name="Finance_Weather_Specialist_Agent",
            func=lambda q: fw_executor.invoke({"input": q}).get("output", "No result from Finance & Weather Specialist."),
            description="Specialist agent for live weather conditions, city temperatures, and currency conversion / exchange rates (forex). Delegate to this agent for weather or currency queries."
        ),
        Tool(
            name="News_Specialist_Agent",
            func=lambda q: news_executor.invoke({"input": q}).get("output", "No result from News Specialist."),
            description="Specialist agent for searching recent news articles and fetching today's top headlines by category. Delegate to this agent for current events, news topics, or headlines."
        )
    ]

    prompt = ChatPromptTemplate.from_messages([
        ("system", SUPERVISOR_SYSTEM_PROMPT),
        MessagesPlaceholder("chat_history", optional=True),
        ("human", "{input}"),
        MessagesPlaceholder("agent_scratchpad"),
    ])

    agent = create_tool_calling_agent(llm, specialist_tools, prompt)
    
    return AgentExecutor(
        agent=agent,
        tools=specialist_tools,
        verbose=True,
        handle_parsing_errors=True,
        max_iterations=6,
        return_intermediate_steps=False,
    )


# Singleton Supervisor instance
supervisor_executor = build_supervisor_agent()


def run_agent(user_input: str, chat_history: list) -> str:
    """Run the multi-agent supervisor with chat history. Returns full response string."""
    history_messages = []
    for msg in chat_history[-10:]:  # last 10 turns to avoid context overflow
        if msg["role"] == "user":
            history_messages.append(HumanMessage(content=msg["content"]))
        elif msg["role"] == "assistant":
            history_messages.append(AIMessage(content=msg["content"]))

    result = supervisor_executor.invoke({
        "input": user_input,
        "chat_history": history_messages,
    })
    
    return result.get("output", "I'm sorry, I couldn't process that request.")
