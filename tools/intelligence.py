"""Deterministic dependency and resource analysis primitives."""

from __future__ import annotations

from collections import defaultdict, deque
from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class Dependency:
    dependency_id: str
    predecessor: str
    successor: str
    owner: str
    due_in_days: int
    blocked: bool = False
    duration_days: int = 0


@dataclass(frozen=True)
class DependencyReport:
    critical_dependencies: tuple[Dependency, ...]
    blockers: tuple[Dependency, ...]
    at_risk_dependencies: tuple[Dependency, ...]
    critical_path: tuple[str, ...]
    estimated_impact_days: int


class DependencyIntelligence:
    """Identify blocked/near-term cross-team links and summarize exposure."""

    def analyze(self, dependencies: Iterable[Dependency]) -> DependencyReport:
        items = tuple(dependencies)
        if any(not item.dependency_id.strip() for item in items):
            raise ValueError("Every dependency must have a non-empty ID")
        if any(item.duration_days < 0 for item in items):
            raise ValueError("Dependency duration cannot be negative")
        if len({item.dependency_id for item in items}) != len(items):
            raise ValueError("Dependency IDs must be unique")

        adjacency: dict[str, list[Dependency]] = defaultdict(list)
        nodes: set[str] = set()
        indegree: dict[str, int] = defaultdict(int)
        for item in items:
            adjacency[item.predecessor].append(item)
            nodes.update((item.predecessor, item.successor))
            indegree[item.successor] += 1
            indegree.setdefault(item.predecessor, 0)

        ready = deque(node for node in nodes if indegree[node] == 0)
        distance = {node: 0 for node in nodes}
        path_to: dict[str, tuple[Dependency, ...]] = {node: () for node in nodes}
        visited = 0
        while ready:
            node = ready.popleft()
            visited += 1
            for item in adjacency[node]:
                candidate = distance[node] + item.duration_days
                if candidate > distance[item.successor] or not path_to[item.successor]:
                    distance[item.successor] = candidate
                    path_to[item.successor] = path_to[node] + (item,)
                indegree[item.successor] -= 1
                if indegree[item.successor] == 0:
                    ready.append(item.successor)
        if visited != len(nodes):
            raise ValueError("Dependency graph contains a cycle; critical path is undefined")

        endpoint = (
            max(distance, key=lambda node: (distance[node], bool(path_to[node])))
            if distance
            else None
        )
        critical_path = path_to[endpoint] if endpoint is not None else ()
        blockers = tuple(item for item in items if item.blocked)
        at_risk = tuple(item for item in items if item.due_in_days <= 5)
        impact = sum(item.duration_days for item in blockers) + sum(
            -item.due_in_days for item in items if item.due_in_days < 0
        )
        return DependencyReport(
            critical_dependencies=critical_path,
            blockers=blockers,
            at_risk_dependencies=at_risk,
            critical_path=tuple(item.dependency_id for item in critical_path),
            estimated_impact_days=impact,
        )


@dataclass(frozen=True)
class ResourceForecast:
    capacity_hours: float
    planned_hours: float
    utilization_percent: float
    capacity_gap_hours: float


class ResourceIntelligence:
    """Compute team utilization and capacity gap from supplied hours."""

    def forecast(self, capacity_hours: float, planned_hours: float) -> ResourceForecast:
        if capacity_hours < 0 or planned_hours < 0:
            raise ValueError("Capacity and planned hours cannot be negative")
        if capacity_hours == 0 and planned_hours > 0:
            raise ValueError("Planned hours cannot be forecast with zero capacity")
        utilization = (planned_hours / capacity_hours * 100) if capacity_hours else 0.0
        return ResourceForecast(
            capacity_hours=capacity_hours,
            planned_hours=planned_hours,
            utilization_percent=round(utilization, 2),
            capacity_gap_hours=round(max(0.0, planned_hours - capacity_hours), 2),
        )

    def skill_gaps(
        self,
        required_skills: Iterable[str],
        available_skills: Iterable[str],
    ) -> tuple[str, ...]:
        """Return required skills absent from the available team skill set."""
        available = {skill.strip().casefold() for skill in available_skills if skill.strip()}
        return tuple(
            skill.strip()
            for skill in required_skills
            if skill.strip() and skill.strip().casefold() not in available
        )
