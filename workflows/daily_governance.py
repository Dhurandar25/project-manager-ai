"""Daily governance workflow composition and approval-gate helpers."""

from __future__ import annotations

from typing import Any

from crews.daily_governance_crew import DailyGovernanceCrew


class DailyGovernanceWorkflow:
    """Launch the configured CrewAI daily governance review."""

    def __init__(self, crew: DailyGovernanceCrew | None = None) -> None:
        self._crew = crew or DailyGovernanceCrew()

    def run(self, project_context: str) -> Any:
        if not project_context.strip():
            raise ValueError("Project context is required for a daily review")
        return self._crew.kickoff(project_context=project_context)
