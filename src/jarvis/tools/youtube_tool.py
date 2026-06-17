"""YouTube tool — searches YouTube and returns video metadata for playback."""
from youtubesearchpython import VideosSearch
from crewai.tools import BaseTool
from pydantic import BaseModel, Field


class YouTubeInput(BaseModel):
    query: str = Field(..., description="Music or video search query, e.g. 'Believer by Imagine Dragons'")
    max_results: int = Field(default=1, description="Number of results to return (1-5)")


class YouTubeTool(BaseTool):
    name: str = "YouTubeTool"
    description: str = (
        "Searches YouTube for music videos or songs. "
        "Returns video ID, title, channel, duration, URL, and thumbnail for playback."
    )
    args_schema: type[BaseModel] = YouTubeInput

    def _run(self, query: str, max_results: int = 1) -> list[dict]:
        search = VideosSearch(query, limit=max_results)
        results = search.result()

        videos = []
        for video in results.get("result", []):
            vid_id = video.get("id", "")
            videos.append({
                "video_id": vid_id,
                "title": video.get("title", ""),
                "channel": video.get("channel", {}).get("name", ""),
                "duration": video.get("duration", ""),
                "url": f"https://www.youtube.com/watch?v={vid_id}",
                "thumbnail_url": video.get("thumbnails", [{}])[0].get("url", ""),
                "embed_url": f"https://www.youtube.com/embed/{vid_id}?autoplay=1",
            })

        return videos
