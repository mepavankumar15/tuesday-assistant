"""
LLM factory using xAI Grok via OpenAI-compatible endpoint.
"""
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()

def get_llm(temperature=0.7):
    return ChatOpenAI(
        model=os.getenv("XAI_MODEL", "grok-3"),
        api_key=os.getenv("XAI_API_KEY"),
        base_url="https://api.x.ai/v1",
        temperature=temperature,
        streaming=True,
    )
