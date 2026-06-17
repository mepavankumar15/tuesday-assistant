"""News tool — wraps NewsAPI for latest headlines by topic."""
import os
from datetime import datetime, timedelta
import requests
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from tenacity import retry, stop_after_attempt, wait_exponential


class NewsInput(BaseModel):
    topic: str = Field(..., description="News topic or keyword, e.g. 'AI', 'cricket', 'Telangana'")
    max_articles: int = Field(default=5, description="Number of articles to return (1-10)")


class NewsTool(BaseTool):
    name: str = "NewsTool"
    description: str = (
        "Fetches the latest news headlines for any topic using NewsAPI. "
        "Returns title, source, summary, publication time, and article URL."
    )
    args_schema: type[BaseModel] = NewsInput

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=4))
    def _run(self, topic: str, max_articles: int = 5) -> list[dict]:
        api_key = os.environ["NEWS_API_KEY"]
        from_date = (datetime.utcnow() - timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%S")

        resp = requests.get(
            "https://newsapi.org/v2/everything",
            params={
                "q": topic,
                "apiKey": api_key,
                "sortBy": "publishedAt",
                "language": "en",
                "from": from_date,
                "pageSize": max_articles,
            },
            timeout=10,
        )
        resp.raise_for_status()
        data = resp.json()

        articles = []
        for art in data.get("articles", [])[:max_articles]:
            articles.append({
                "title": art.get("title", ""),
                "source": art.get("source", {}).get("name", "Unknown"),
                "published_at": art.get("publishedAt", ""),
                "summary": (art.get("description") or "No summary available.")[:200],
                "url": art.get("url", ""),
            })

        return articles
