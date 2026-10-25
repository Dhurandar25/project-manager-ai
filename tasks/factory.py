"""Create CrewAI tasks from YAML task definitions."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from crewai import Agent, Task

from tools.config_loader import load_yaml
from tools.reporting import ExecutiveReport


class TaskFactory:
    """Build task instances with explicit agents and optional context tasks."""

    def __init__(self, config_path: Path | None = None) -> None:
        self._config_path = config_path or Path(__file__).parents[1] / "config" / "tasks.yaml"
        self._tasks: dict[str, dict[str, Any]] = load_yaml(self._config_path)

    @property
    def names(self) -> tuple[str, ...]:
        return tuple(self._tasks)

    def create(
        self,
        name: str,
        agent: Agent,
        *,
        context: list[Task] | None = None,
    ) -> Task:
        """Create a task, preserving its human-input gate when configured."""
        config = dict(self._tasks[name])
        output_model = config.pop("output_model", None)
        options: dict[str, Any] = {
            "config": config,
            "agent": agent,
        }
        if output_model == "ExecutiveReport":
            options["output_pydantic"] = ExecutiveReport
        elif output_model is not None:
            raise ValueError(f"Unknown task output model: {output_model}")
        if context:
            options["context"] = context
        return Task(**options)
