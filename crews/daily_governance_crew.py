"""CrewAI crew for the daily AI-PMO governance review."""

from __future__ import annotations

from typing import Any

from crewai import Crew, Process

from agents.factory import AgentFactory
from tasks.factory import TaskFactory


class DailyGovernanceCrew:
    """Compose configured project-management and reporting agents."""

    def __init__(
        self,
        agent_factory: AgentFactory | None = None,
        task_factory: TaskFactory | None = None,
    ) -> None:
        self._agents = agent_factory or AgentFactory()
        self._tasks = task_factory or TaskFactory()

    def kickoff(self, *, project_context: str) -> Any:
        project_manager = self._agents.create("project_manager")
        reporter = self._agents.create("reporting")
        review = self._tasks.create("daily_review", project_manager)
        report = self._tasks.create("executive_reporting", reporter, context=[review])
        crew = Crew(
            agents=[project_manager, reporter],
            tasks=[review, report],
            process=Process.sequential,
            verbose=True,
        )
        return crew.kickoff(inputs={"project_context": project_context})
