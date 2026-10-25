"""Dependency-injected Jira service for delivery reporting."""

from __future__ import annotations

from typing import Any, Protocol


class JiraClient(Protocol):
    """Client contract implemented by a configured Jira SDK or adapter."""

    def search(self, jql: str) -> Any: ...

    def get_sprints(self, board_id: int) -> Any: ...

    def get_versions(self, project_key: str) -> Any: ...


class JiraService:
    """Provide focused Jira queries without owning credentials or HTTP setup."""

    def __init__(self, client: JiraClient) -> None:
        self._client = client

    def stories(self, project_key: str, sprint_id: int | None = None) -> Any:
        sprint_clause = f" AND sprint = {sprint_id}" if sprint_id is not None else ""
        return self._client.search(
            f'project = "{project_key}" AND issuetype in (Story, Bug){sprint_clause}'
        )

    def epics(self, project_key: str) -> Any:
        return self._client.search(f'project = "{project_key}" AND issuetype = Epic')

    def sprint_metrics(self, board_id: int) -> Any:
        return self._client.get_sprints(board_id)

    def release_tracking(self, project_key: str) -> Any:
        return self._client.get_versions(project_key)
