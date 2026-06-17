"""
YouTube Music Specialist Agent.
ReAct loop that searches YouTube, then returns structured JSON for the UI
to render an embedded player.
"""
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from tools.music_tools import search_youtube_music
from config.settings import settings
from state.agent_state import AgentState
from utils.logger import logger
import json, re


_SYSTEM = f"""You are {settings.app_name}'s Music & YouTube Specialist.

When the user wants to play or find music:
1. Call search_youtube_music with a clean search query
2. Choose the best result (first official/audio/video result)
3. Respond with ONLY this JSON (no markdown, no extra text):

{{
  "message": "Playing <song/artist> for you! 🎵",
  "video_id": "<youtube_video_id>",
  "title": "<exact video title from tool>",
  "channel": "<channel name from tool>",
  "embed_url": "<embed_url from tool result>",
  "watch_url": "<watch_url from tool result>",
  "all_results": [<full list of result objects from the tool>]
}}

CRITICAL: Copy video_id, embed_url, watch_url EXACTLY from the tool output.
Tools available: search_youtube_music
"""

_TOOLS = [search_youtube_music]


def music_agent_node(state: AgentState) -> AgentState:
    logger.info(f"[MusicAgent] '{state['user_query']}'")
    llm = ChatOpenAI(api_key=settings.xai_api_key, base_url=settings.xai_base_url,
                     model=settings.xai_model, temperature=0.3)
    agent = create_react_agent(llm, tools=_TOOLS, prompt=_SYSTEM)
    try:
        response = agent.invoke({"messages": [("user", state["user_query"])]})
        raw = response["messages"][-1].content
        # Strip markdown fences if model wrapped JSON anyway
        clean = re.sub(r"```json|```", "", raw).strip()
        music_data = json.loads(clean)
        msg = music_data.get("message", "Here's your music! 🎵")
        return {
            **state,
            "final_answer": msg,
            "agent_response": {"type": "music", "data": music_data, "text": msg},
            "metadata": {**state.get("metadata", {}), "agent": "music"},
        }
    except json.JSONDecodeError:
        # Model gave plain text — still show it
        return {**state, "final_answer": raw,
                "agent_response": {"type": "music_text", "text": raw},
                "metadata": {**state.get("metadata", {}), "agent": "music"}}
    except Exception as e:
        logger.error(f"[MusicAgent] {e}")
        msg = f"⚠️ Couldn't find that music right now.\n`{e}`"
        return {**state, "final_answer": msg, "agent_response": {"type": "error", "text": msg}}
