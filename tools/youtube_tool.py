import os
from langchain_core.tools import tool
from googleapiclient.discovery import build

def _get_youtube_client():
    return build("youtube", "v3", developerKey=os.getenv("YOUTUBE_API_KEY"))

@tool
def search_youtube(query: str) -> str:
    """
    Search YouTube for videos or music. 
    Input: search query string (e.g. 'lo fi hip hop', 'Coldplay Yellow', 'Python tutorial').
    Returns: list of top 5 results with video IDs, titles, and channel names.
    Use the video_id from results when the user wants to play something.
    """
    try:
        youtube = _get_youtube_client()
        request = youtube.search().list(
            part="snippet",
            q=query,
            type="video",
            maxResults=5,
            videoCategoryId="10",  # prefer music category but fallback
        )
        response = request.execute()
        
        results = []
        for item in response.get("items", []):
            video_id = item["id"]["videoId"]
            title = item["snippet"]["title"]
            channel = item["snippet"]["channelTitle"]
            results.append(f"- Title: {title} | Channel: {channel} | video_id: {video_id}")
        
        if not results:
            return "No YouTube results found for that query."
        
        return "YouTube search results:\n" + "\n".join(results)
    except Exception as e:
        return f"YouTube search error: {str(e)}"

@tool
def get_youtube_video_details(video_id: str) -> str:
    """
    Get details for a specific YouTube video by its video ID.
    Input: YouTube video_id (e.g. 'dQw4w9WgXcQ').
    Returns: title, description snippet, duration, view count.
    """
    try:
        youtube = _get_youtube_client()
        request = youtube.videos().list(
            part="snippet,contentDetails,statistics",
            id=video_id
        )
        response = request.execute()
        
        if not response.get("items"):
            return f"No video found with ID: {video_id}"
        
        item = response["items"][0]
        snippet = item["snippet"]
        stats = item.get("statistics", {})
        
        return (
            f"Title: {snippet['title']}\n"
            f"Channel: {snippet['channelTitle']}\n"
            f"Views: {stats.get('viewCount', 'N/A')}\n"
            f"Description: {snippet.get('description', '')[:200]}..."
        )
    except Exception as e:
        return f"Error fetching video details: {str(e)}"
