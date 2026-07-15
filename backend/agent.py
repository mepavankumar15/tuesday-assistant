"""
LangChain agent using xAI Grok via OpenAI-compatible endpoint.
Tools: YouTube search, weather, forex, news.
Uses create_tool_calling_agent with chat history memory.
"""
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage

from tools.youtube_tool import search_youtube, get_youtube_video_details
from tools.weather_tool import get_weather
from tools.forex_tool import get_forex_rate
from tools.news_tool import get_news, get_top_headlines

load_dotenv()

SYSTEM_PROMPT = """
You are Grok Assistant, an intelligent, friendly AI assistant like Alexa.
You have a natural, conversational voice. Keep responses concise and clear — 
ideal for being read aloud (2-4 sentences max unless asked for detail).

You have access to these tools:
- search_youtube: Search for YouTube videos or music. Use when user asks to play, 
  find, or search for a song, video, or anything on YouTube.
- get_youtube_video_details: Get more details about a specific YouTube video.
- get_weather: Get current weather for any city. Use when user asks about weather, 
  temperature, or conditions.
- get_forex_rate: Get live exchange rate between two currencies. 
  Use when user asks about currency conversion or exchange rates.
- get_news: Search for recent news on any topic. Use when user asks about 
  news, current events, or what's happening about a specific topic.
- get_top_headlines: Get today's top headlines by category (general, business, 
  technology, sports, science, health, entertainment). Use when user asks 
  for top news or trending headlines.

When you use a YouTube tool, always include the video_id in your response 
as a JSON block like: {{"action": "play_youtube", "video_id": "VIDEO_ID", "title": "VIDEO TITLE"}}
Place this JSON block at the END of your text response.

For weather, forex, and news, format the data naturally in your spoken response.
For news results, summarize the top headlines briefly — don't list URLs.

For general conversation, respond naturally and helpfully.
Today's date is accessible via the system. Be helpful, warm, and efficient.
"""

def build_agent():
    llm = ChatOpenAI(
        model=os.getenv("XAI_MODEL", "grok-3"),
        api_key=os.getenv("XAI_API_KEY"),
        base_url="https://api.x.ai/v1",
        temperature=0.7,
        streaming=True,
    )

    tools = [search_youtube, get_youtube_video_details, get_weather, get_forex_rate, get_news, get_top_headlines]

    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        MessagesPlaceholder("chat_history", optional=True),
        ("human", "{input}"),
        MessagesPlaceholder("agent_scratchpad"),
    ])

    agent = create_tool_calling_agent(llm, tools, prompt)
    
    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        handle_parsing_errors=True,
        max_iterations=5,
        return_intermediate_steps=False,
    )
    
    return agent_executor

# Singleton agent instance
agent_executor = build_agent()

def run_agent(user_input: str, chat_history: list) -> str:
    """Run the agent with chat history. Returns full response string."""
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
