"""Create CrewAI agents from the external YAML configuration."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from crewai import Agent

from tools.config_loader import load_yaml
from tools.crewai_tools import (
    analyze_dependencies,
    analyze_skill_gaps,
    calculate_project_risk,
    forecast_team_capacity,
)


class AgentFactory:
    """Build configured agents without embedding prompts in application code."""

    def __init__(self, config_path: Path | None = None) -> None:
        self._config_path = config_path or Path(__file__).parents[1] / "config" / "agents.yaml"
        self._agents: dict[str, dict[str, Any]] = load_yaml(self._config_path)

    @property
    def names(self) -> tuple[str, ...]:
        return tuple(self._agents)

    def create(self, name: str) -> Agent:
        """Create one named agent; raises KeyError for unknown configured names."""
        config = self._agents[name]
        llm = os.getenv("CREWAI_LLM")
        options: dict[str, Any] = {
            "config": config,
            "verbose": True,
            "allow_delegation": False,
        }
        agent_tools = {
            "project_manager": [
                calculate_project_risk,
                forecast_team_capacity,
                analyze_dependencies,
                analyze_skill_gaps,
            ],
            "risk": [calculate_project_risk],
            "resource": [forecast_team_capacity, analyze_skill_gaps],
            "dependency": [analyze_dependencies],
        }.get(name)
        if agent_tools:
            options["tools"] = agent_tools
        if llm:
            options["llm"] = llm
        return Agent(**options)
