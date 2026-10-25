"""Credential-free Azure DevOps integration interface."""

from __future__ import annotations

from typing import Any, Protocol


class AzureDevOpsClient(Protocol):
    """Minimal client contract supplied by an application composition root."""

    def get(self, resource: str, params: dict[str, Any] | None = None) -> Any: ...


class AzureDevOpsService:
    """Expose common Azure DevOps resources through an injected client."""

    def __init__(self, client: AzureDevOpsClient) -> None:
        self._client = client

    def work_items(self, ids: list[int]) -> Any:
        return self._client.get("workitems", {"ids": ids})

    def boards(self, team: str | None = None) -> Any:
        return self._client.get("boards", {"team": team} if team else None)

    def features(self) -> Any:
        return self._client.get("features")

    def epics(self) -> Any:
        return self._client.get("epics")

    def sprint_status(self, sprint_id: str) -> Any:
        return self._client.get("sprints/status", {"sprint_id": sprint_id})

    def delivery_metrics(self, team: str, period: str) -> Any:
        return self._client.get("delivery/metrics", {"team": team, "period": period})

    def releases(self) -> Any:
        return self._client.get("releases")

    def pipelines(self, pipeline_id: str | None = None) -> Any:
        return self._client.get(
            "pipelines", {"pipeline_id": pipeline_id} if pipeline_id else None
        )
