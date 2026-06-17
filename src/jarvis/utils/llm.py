"""
LLM factory — returns a CrewAI LLM instance pointed at Grok xAI.
Grok uses an OpenAI-compatible REST API, so we just override the base_url.
"""
import os
from functools import lru_cache
from crewai import LLM
import litellm

# Monkey-patch LiteLLM to forcibly remove 'stop' parameter for xAI
_orig_completion = litellm.completion
_orig_acompletion = litellm.acompletion

def _custom_completion(*args, **kwargs):
    kwargs.pop("stop", None)
    return _orig_completion(*args, **kwargs)

async def _custom_acompletion(*args, **kwargs):
    kwargs.pop("stop", None)
    return await _orig_acompletion(*args, **kwargs)

litellm.completion = _custom_completion
litellm.acompletion = _custom_acompletion

@lru_cache(maxsize=1)
def get_llm(temperature: float = 0.3) -> LLM:
    """Return a singleton Grok LLM instance."""
    # We prefix with openai/ so LiteLLM treats it as an OpenAI-compatible endpoint
    model_name = os.environ.get("XAI_MODEL", "grok-3")
    if not model_name.startswith("openai/"):
        model_name = f"openai/{model_name}"
        
    return LLM(
        model=model_name,
        api_key=os.environ.get("XAI_API_KEY"),
        base_url=os.environ.get("XAI_BASE_URL", "https://api.x.ai/v1"),
        temperature=temperature,
        max_tokens=2048,
    )
