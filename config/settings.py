"""
Single source of truth for all configuration.
Pydantic BaseSettings auto-loads from .env file.
"""
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    # XAI Grok
    xai_api_key: str = Field(..., env="XAI_API_KEY")
    xai_base_url: str = Field("https://api.x.ai/v1", env="XAI_BASE_URL")
    xai_model: str = Field("grok-3-mini", env="XAI_MODEL")

    # Weather
    # OpenMeteo does not require an API key

    # Forex
    forex_api_key: str = Field(..., env="FOREX_API_KEY")
    forex_base_url: str = Field("https://v6.exchangerate-api.com/v6", env="FOREX_BASE_URL")

    # News
    news_api_key: str = Field(..., env="NEWS_API_KEY")
    news_base_url: str = Field("https://newsapi.org/v2", env="NEWS_BASE_URL")

    # YouTube
    youtube_api_key: str = Field(..., env="YOUTUBE_API_KEY")

    # App
    app_name: str = Field("FRIDAY", env="APP_NAME")
    debug: bool = Field(False, env="DEBUG")
    log_level: str = Field("INFO", env="LOG_LEVEL")
    max_news_articles: int = Field(5, env="MAX_NEWS_ARTICLES")
    default_city: str = Field("Hyderabad", env="DEFAULT_CITY")

    class Config:
        env_file = ".env"
        case_sensitive = False


# Singleton — import this everywhere
settings = Settings()
