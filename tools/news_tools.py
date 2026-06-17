"""
LangChain @tool functions for NewsAPI.org.
Supports top headlines by country/category and keyword search.
"""
from langchain_core.tools import tool
from config.settings import settings
from utils.logger import logger
import requests


@tool
def get_top_headlines(country: str = "in", category: str = "general", page_size: int = 5) -> dict:
    """
    Fetch today's top news headlines for a given country and category.

    Args:
        country:   ISO country code e.g. 'in' (India), 'us' (USA), 'gb' (UK)
        category:  One of: business, entertainment, health, science, sports, technology, general
        page_size: Number of articles (1–10, default 5)
    """
    try:
        resp = requests.get(
            f"{settings.news_base_url}/top-headlines",
            params={
                "country": country,
                "category": category,
                "pageSize": min(page_size, settings.max_news_articles),
                "apiKey": settings.news_api_key,
            },
            timeout=10,
        )
        resp.raise_for_status()
        data = resp.json()
        articles = [
            {
                "title": a.get("title", ""),
                "source": a.get("source", {}).get("name", "Unknown"),
                "description": (a.get("description") or "")[:150],
                "url": a.get("url", ""),
                "published_at": a.get("publishedAt", ""),
                "image_url": a.get("urlToImage", ""),
            }
            for a in data.get("articles", [])
            if a.get("title") and a.get("title") != "[Removed]"
        ]
        return {"country": country, "category": category, "articles": articles}
    except Exception as e:
        logger.error(f"[NewsTool] get_top_headlines: {e}")
        return {"error": str(e)}


@tool
def search_news(query: str, language: str = "en", page_size: int = 5) -> dict:
    """
    Search all news sources for articles on a specific topic.

    Args:
        query:     Topic keywords e.g. 'AI India startup', 'IPL cricket'
        language:  Language code e.g. 'en', 'hi'
        page_size: Number of articles (default 5)
    """
    try:
        resp = requests.get(
            f"{settings.news_base_url}/everything",
            params={
                "q": query,
                "language": language,
                "pageSize": min(page_size, settings.max_news_articles),
                "sortBy": "publishedAt",
                "apiKey": settings.news_api_key,
            },
            timeout=10,
        )
        resp.raise_for_status()
        data = resp.json()
        articles = [
            {
                "title": a.get("title", ""),
                "source": a.get("source", {}).get("name", "Unknown"),
                "description": (a.get("description") or "")[:150],
                "url": a.get("url", ""),
                "published_at": a.get("publishedAt", ""),
            }
            for a in data.get("articles", [])
            if a.get("title") and a.get("title") != "[Removed]"
        ]
        return {"query": query, "total": data.get("totalResults", 0), "articles": articles}
    except Exception as e:
        logger.error(f"[NewsTool] search_news({query}): {e}")
        return {"error": str(e)}
