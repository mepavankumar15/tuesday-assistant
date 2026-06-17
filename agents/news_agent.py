"""
News Specialist Agent.
ReAct loop using get_top_headlines and search_news tools.
"""
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from tools.news_tools import get_top_headlines, search_news
from config.settings import settings
from state.agent_state import AgentState
from utils.logger import logger


_SYSTEM = """You are FRIDAY's News Specialist with access to live global news.

Rules:
- Broad "news" / "headlines" queries → use get_top_headlines (country='in' by default)
- Specific topics → use search_news  
- Present results as a numbered markdown list: title, source, 1-sentence summary
- Include the publication time if available
- Keep each article entry concise — this is a glance, not a full read
- Suggest the URL for articles the user wants to read fully

Tools: get_top_headlines, search_news
"""

_TOOLS = [get_top_headlines, search_news]


def news_agent_node(state: AgentState) -> AgentState:
    logger.info(f"[NewsAgent] '{state['user_query']}'")
    llm = ChatOpenAI(api_key=settings.xai_api_key, base_url=settings.xai_base_url,
                     model=settings.xai_model, temperature=0.3)
    agent = create_react_agent(llm, tools=_TOOLS, prompt=_SYSTEM)
    try:
        response = agent.invoke({"messages": [("user", state["user_query"])]})
        out = response["messages"][-1].content
        return {**state, "final_answer": out,
                "agent_response": {"type": "news", "text": out},
                "metadata": {**state.get("metadata", {}), "agent": "news"}}
    except Exception as e:
        logger.error(f"[NewsAgent] {e}")
        msg = f"⚠️ Couldn't fetch news right now.\n`{e}`"
        return {**state, "final_answer": msg, "agent_response": {"type": "error", "text": msg}}
