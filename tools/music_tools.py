"""
LangChain @tool functions for YouTube Data API v3.
Searches for music videos and returns embeddable data.
"""
from langchain_core.tools import tool
from config.settings import settings
from utils.logger import logger
import requests


@tool
def search_youtube_music(query: str, max_results: int = 5) -> dict:
    """
    Search YouTube for music videos matching a query.
    Returns video IDs, titles, channels, thumbnails, and embed URLs.

    Args:
        query:       Song / artist / genre to search (e.g. 'Arijit Singh Tum Hi Ho')
        max_results: Number of results to return (1–10, default 5)
    """
    try:
        resp = requests.get(
            "https://www.googleapis.com/youtube/v3/search",
            params={
                "part": "snippet",
                "q": f"{query} official audio",
                "type": "video",
                "videoCategoryId": "10",         # Music category
                "maxResults": min(max_results, 10),
                "key": settings.youtube_api_key,
            },
            timeout=10,
        )
        resp.raise_for_status()
        data = resp.json()

        results = []
        for item in data.get("items", []):
            vid = item["id"].get("videoId", "")
            s = item["snippet"]
            results.append({
                "video_id": vid,
                "title": s.get("title", ""),
                "channel": s.get("channelTitle", ""),
                "thumbnail": s["thumbnails"]["medium"]["url"],
                "embed_url": f"https://www.youtube.com/embed/{vid}?autoplay=1",
                "watch_url": f"https://www.youtube.com/watch?v={vid}",
            })

        return {"query": query, "results": results, "total": len(results)}
    except Exception as e:
        logger.error(f"[MusicTool] search_youtube_music({query}): {e}")
        return {"error": str(e), "query": query}
