"""
JARVIS CrewAI Crew — wires agents, tasks, and tools together.
Uses hierarchical process with a Supervisor delegating to specialists.
"""
import os
import yaml
from pathlib import Path
from crewai import Agent, Crew, Task, Process
from jarvis.utils.llm import get_llm
from jarvis.tools.weather_tool import WeatherTool
from jarvis.tools.forex_tool import ForexTool
from jarvis.tools.youtube_tool import YouTubeTool
from jarvis.tools.news_tool import NewsTool


CONFIG_DIR = Path(__file__).parent / "config"


def _load_yaml(filename: str) -> dict:
    with open(CONFIG_DIR / filename) as f:
        return yaml.safe_load(f)


class JarvisCrew:
    """Orchestrates the JARVIS multi-agent assistant."""

    def __init__(self):
        self.llm = get_llm(temperature=0.3)
        self._agents_cfg = _load_yaml("agents.yaml")
        self._tasks_cfg = _load_yaml("tasks.yaml")
        self._build_tools()
        self._build_agents()

    def _build_tools(self):
        self.weather_tool = WeatherTool()
        self.forex_tool = ForexTool()
        self.youtube_tool = YouTubeTool()
        self.news_tool = NewsTool()

    def _build_agents(self):
        cfg = self._agents_cfg

        self.weather_agent = Agent(
            role=cfg["weather_agent"]["role"],
            goal=cfg["weather_agent"]["goal"],
            backstory=cfg["weather_agent"]["backstory"],
            tools=[self.weather_tool],
            llm=self.llm,
            verbose=True,
            max_iter=3,
        )

        self.forex_agent = Agent(
            role=cfg["forex_agent"]["role"],
            goal=cfg["forex_agent"]["goal"],
            backstory=cfg["forex_agent"]["backstory"],
            tools=[self.forex_tool],
            llm=self.llm,
            verbose=True,
            max_iter=3,
        )

        self.music_agent = Agent(
            role=cfg["music_agent"]["role"],
            goal=cfg["music_agent"]["goal"],
            backstory=cfg["music_agent"]["backstory"],
            tools=[self.youtube_tool],
            llm=self.llm,
            verbose=True,
            max_iter=3,
        )

        self.news_agent = Agent(
            role=cfg["news_agent"]["role"],
            goal=cfg["news_agent"]["goal"],
            backstory=cfg["news_agent"]["backstory"],
            tools=[self.news_tool],
            llm=self.llm,
            verbose=True,
            max_iter=3,
        )

        # Supervisor has access to delegate
        self.supervisor = Agent(
            role=cfg["supervisor"]["role"],
            goal=cfg["supervisor"]["goal"],
            backstory=cfg["supervisor"]["backstory"],
            llm=self.llm,
            verbose=True,
            allow_delegation=True,
            max_iter=5,
        )

    def run(self, query: str) -> dict:
        """
        Execute the crew for a given user query.
        Returns a dict with 'response' (str) and optional structured data
        keys: 'weather', 'forex', 'music', 'news'.
        """
        task_cfg = self._tasks_cfg["route_query"]

        routing_task = Task(
            description=task_cfg["description"].format(query=query),
            expected_output=task_cfg["expected_output"]
        )

        crew = Crew(
            agents=[
                self.weather_agent,
                self.forex_agent,
                self.music_agent,
                self.news_agent,
            ],
            tasks=[routing_task],
            process=Process.hierarchical,
            manager_agent=self.supervisor,
            verbose=True,
        )

        result = crew.kickoff(inputs={"query": query})

        return {
            "response": str(result),
            "raw": result,
        }
