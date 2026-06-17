"""Smoke tests for CrewAI orchestration."""
import pytest
from unittest.mock import patch

def test_jarvis_crew_instantiation():
    import os
    os.environ["OPENAI_API_KEY"] = "dummy_key"
    with patch("jarvis.crew.get_llm") as mock_get_llm:
        mock_get_llm.return_value = "gpt-4"
        from jarvis.crew import JarvisCrew
        # Just test that we can instantiate it without crashing
        crew = JarvisCrew()
        assert crew is not None
        assert crew.supervisor is not None
        assert crew.weather_agent is not None
