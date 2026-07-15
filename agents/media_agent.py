"""
Media Specialist Sub-Agent
Domain: YouTube video searching, song/music playback, and video details.
Tools: search_youtube, get_youtube_video_details
"""
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from tools.youtube_tool import search_youtube, get_youtube_video_details

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
