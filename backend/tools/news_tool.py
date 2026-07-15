import os
import httpx
from langchain_core.tools import tool


@tool
def get_news(query: str) -> str:
    """
    Search for recent news articles on any topic.
    Input: topic or keyword (e.g. 'AI', 'India elections', 'stock market', 'SpaceX').
    Returns: top 5 recent headlines with source, title, and description.
    Use when user asks about news, headlines, current events, or what's happening.
    """
    try:
        api_key = os.getenv("NEWS_API_KEY")
        if not api_key:
            return "News API key not configured. Please set NEWS_API_KEY in your .env file."

        url = "https://newsapi.org/v2/everything"
        params = {
            "q": query,
            "apiKey": api_key,
            "language": "en",
            "pageSize": 5,
            "sortBy": "publishedAt",
        }

        response = httpx.get(url, params=params, timeout=10.0)
        response.raise_for_status()
        data = response.json()

        if data.get("status") != "ok":
            return f"NewsAPI error: {data.get('message', 'Unknown error')}"

        articles = data.get("articles", [])
        if not articles:
            return f"No recent news found for '{query}'."

        results = []
        for i, article in enumerate(articles, 1):
            title = article.get("title", "No title")
            description = (article.get("description") or "")[:150]
            source = article.get("source", {}).get("name", "Unknown")
            published = (article.get("publishedAt") or "")[:10]  # date only
            article_url = article.get("url", "")

            results.append(
                f"{i}. [{source}] {title}\n"
                f"   {description}\n"
                f"   Published: {published}"
            )

        return f"Latest news on '{query}':\n\n" + "\n\n".join(results)

    except httpx.HTTPStatusError as e:
        if e.response.status_code == 401:
            return "News API key is invalid. Check your NEWS_API_KEY."
        if e.response.status_code == 429:
            return "News API rate limit exceeded. Please try again later."
        return f"News API error: {str(e)}"
    except Exception as e:
        return f"Error fetching news: {str(e)}"


@tool
def get_top_headlines(category: str = "general") -> str:
    """
    Get today's top headlines by category.
    Input: category — one of: general, business, technology, sports, science, health, entertainment.
    Use when user asks for top news, trending news, or headlines without a specific topic.
    """
    try:
        api_key = os.getenv("NEWS_API_KEY")
        if not api_key:
            return "News API key not configured. Please set NEWS_API_KEY in your .env file."

        url = "https://newsapi.org/v2/top-headlines"
        params = {
            "apiKey": api_key,
            "language": "en",
            "category": category,
            "pageSize": 5,
        }

        response = httpx.get(url, params=params, timeout=10.0)
        response.raise_for_status()
        data = response.json()

        if data.get("status") != "ok":
            return f"NewsAPI error: {data.get('message', 'Unknown error')}"

        articles = data.get("articles", [])
        if not articles:
            return f"No top headlines found for category '{category}'."

        results = []
        for i, article in enumerate(articles, 1):
            title = article.get("title", "No title")
            source = article.get("source", {}).get("name", "Unknown")
            description = (article.get("description") or "")[:150]

            results.append(
                f"{i}. [{source}] {title}\n"
                f"   {description}"
            )

        return f"Top {category} headlines:\n\n" + "\n\n".join(results)

    except httpx.HTTPStatusError as e:
        if e.response.status_code == 401:
            return "News API key is invalid. Check your NEWS_API_KEY."
        if e.response.status_code == 429:
            return "News API rate limit exceeded. Please try again later."
        return f"News API error: {str(e)}"
    except Exception as e:
        return f"Error fetching headlines: {str(e)}"
