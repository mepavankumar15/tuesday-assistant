"""
News Specialist Sub-Agent
Domain: Finding recent news articles on specific topics and daily top headlines by category.
Tools: get_news, get_top_headlines
"""
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from tools.news_tool import get_news, get_top_headlines

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
