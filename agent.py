"""
Hierarchical Multi-Agent System using xAI Grok via OpenAI-compatible endpoint.
Architecture:
- Supervisor Agent (Orchestrator): Routes requests, maintains conversation, synthesizes outputs.
- Specialist Agents (Workers wrapped as Tools):
  1. Media_Specialist_Agent: YouTube video & music searching / playback.
  2. Finance_Weather_Specialist_Agent: Live weather conditions & foreign exchange rates.
  3. News_Specialist_Agent: Topic news queries & category top headlines.
"""
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.tools import Tool

from tools.youtube_tool import search_youtube, get_youtube_video_details
from tools.weather_tool import get_weather
from tools.forex_tool import get_forex_rate
from tools.news_tool import get_news, get_top_headlines

load_dotenv()

# ─── LLM Factory ─────────────────────────────────────────────────────────────
def _get_llm(temperature=0.7):
    return ChatOpenAI(
        model=os.getenv("XAI_MODEL", "grok-3"),
        api_key=os.getenv("XAI_API_KEY"),
        base_url="https://api.x.ai/v1",
        temperature=temperature,
        streaming=True,
    )


# ─── 1. Media Specialist Sub-Agent ───────────────────────────────────────────
MEDIA_SYSTEM_PROMPT = """
You are the Media Specialist Agent of Alex Assistant.
Your sole domain is searching YouTube for music, songs, videos, or detailed video info.
You have access to: search_youtube, get_youtube_video_details.

Rules:
1. When asked to find or play any song, video, or music, use `search_youtube`.
2. Once you get results, pick the most relevant result's `video_id` and `title`.
3. You MUST format your final response with a concise summary AND include the following JSON block EXACTLY at the very END of your output:
   {{"action": "play_youtube", "video_id": "VIDEO_ID_HERE", "title": "VIDEO TITLE HERE"}}
4. Never omit the JSON block when a playable video/song is found.
"""

def build_media_agent(llm):
    tools = [search_youtube, get_youtube_video_details]
    prompt = ChatPromptTemplate.from_messages([
        ("system", MEDIA_SYSTEM_PROMPT),
        ("human", "{input}"),
        MessagesPlaceholder("agent_scratchpad"),
    ])
    agent = create_tool_calling_agent(llm, tools, prompt)
    return AgentExecutor(agent=agent, tools=tools, verbose=True, handle_parsing_errors=True, max_iterations=4)


# ─── 2. Finance & Weather Specialist Sub-Agent ───────────────────────────────
FINANCE_WEATHER_SYSTEM_PROMPT = """
You are the Finance & Weather Specialist Agent of Alex Assistant.
Your domain is real-time environmental data (weather) and financial rates (forex).
You have access to: get_weather, get_forex_rate.

Rules:
1. For weather queries, extract the city name and use `get_weather`.
2. For currency queries, extract the base/target 3-letter currency codes (e.g., USD, EUR, INR, GBP) and use `get_forex_rate`.
3. Provide a clear, natural, accurate summary of the conditions or exchange rates returned by the tools.
"""

def build_finance_weather_agent(llm):
    tools = [get_weather, get_forex_rate]
    prompt = ChatPromptTemplate.from_messages([
        ("system", FINANCE_WEATHER_SYSTEM_PROMPT),
        ("human", "{input}"),
        MessagesPlaceholder("agent_scratchpad"),
    ])
    agent = create_tool_calling_agent(llm, tools, prompt)
    return AgentExecutor(agent=agent, tools=tools, verbose=True, handle_parsing_errors=True, max_iterations=4)


# ─── 3. News Specialist Sub-Agent ────────────────────────────────────────────
NEWS_SYSTEM_PROMPT = """
You are the News Specialist Agent of Alex Assistant.
Your domain is finding recent news articles on topics or browsing top daily headlines.
You have access to: get_news, get_top_headlines.

Rules:
1. For specific topics or keywords (e.g. 'AI', 'SpaceX', 'elections'), use `get_news`.
2. For general/trending news by category (general, business, technology, sports, science, health, entertainment), use `get_top_headlines`.
3. Summarize the top headlines clearly with their source names and short descriptions. Do not dump raw URLs.
"""

def build_news_agent(llm):
    tools = [get_news, get_top_headlines]
    prompt = ChatPromptTemplate.from_messages([
        ("system", NEWS_SYSTEM_PROMPT),
        ("human", "{input}"),
        MessagesPlaceholder("agent_scratchpad"),
    ])
    agent = create_tool_calling_agent(llm, tools, prompt)
    return AgentExecutor(agent=agent, tools=tools, verbose=True, handle_parsing_errors=True, max_iterations=4)


# ─── 4. Supervisor / Orchestrator Agent ──────────────────────────────────────
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
    llm = _get_llm()
    
    # Initialize sub-agents
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
agent_executor = build_supervisor_agent()


def run_agent(user_input: str, chat_history: list) -> str:
    """Run the multi-agent supervisor with chat history. Returns full response string."""
    history_messages = []
    for msg in chat_history[-10:]:  # last 10 turns to avoid context overflow
        if msg["role"] == "user":
            history_messages.append(HumanMessage(content=msg["content"]))
        elif msg["role"] == "assistant":
            history_messages.append(AIMessage(content=msg["content"]))

    result = agent_executor.invoke({
        "input": user_input,
        "chat_history": history_messages,
    })
    
    return result.get("output", "I'm sorry, I couldn't process that request.")
