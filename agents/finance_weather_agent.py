"""
Finance & Weather Specialist Sub-Agent
Domain: Real-time city weather conditions and currency conversion / foreign exchange rates.
Tools: get_weather, get_forex_rate
"""
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from tools.weather_tool import get_weather
from tools.forex_tool import get_forex_rate

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
