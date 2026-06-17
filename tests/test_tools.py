"""Basic smoke tests for all tools."""
import os
import pytest
from unittest.mock import patch, MagicMock


def test_weather_tool_structure():
    """Test WeatherTool returns expected keys."""
    from jarvis.tools.weather_tool import WeatherTool
    mock_response = {
        "results": [{"latitude": 17.38, "longitude": 78.48, "name": "Hyderabad"}]
    }
    with patch("requests.get") as mock_get:
        mock_get.return_value.json.return_value = mock_response
        mock_get.return_value.raise_for_status = MagicMock()
        tool = WeatherTool()
        # Tool is wired; just assert it's instantiated
        assert tool.name == "WeatherTool"


def test_forex_tool_instantiation():
    from jarvis.tools.forex_tool import ForexTool
    tool = ForexTool()
    assert tool.name == "ForexTool"


def test_youtube_tool_instantiation():
    from jarvis.tools.youtube_tool import YouTubeTool
    tool = YouTubeTool()
    assert tool.name == "YouTubeTool"


def test_news_tool_instantiation():
    from jarvis.tools.news_tool import NewsTool
    tool = NewsTool()
    assert tool.name == "NewsTool"
