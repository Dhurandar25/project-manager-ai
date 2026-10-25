import json

from tools.crewai_tools import (
    analyze_dependencies,
    analyze_skill_gaps,
    calculate_project_risk,
    forecast_team_capacity,
)


def test_risk_calculator_is_exposed_as_crewai_tool() -> None:
    result = json.loads(calculate_project_risk.run(probability=3, impact=4))

    assert result["score"] == 12
    assert result["category"] == "High"


def test_resource_tool_returns_utilization_forecast() -> None:
    result = json.loads(forecast_team_capacity.run(capacity_hours=100, planned_hours=80))

    assert result["utilization_percent"] == 80
    assert result["capacity_gap_hours"] == 0


def test_dependency_tool_identifies_blockers() -> None:
    dependencies = json.dumps(
        [
            {
                "dependency_id": "D-1",
                "predecessor": "Team A",
                "successor": "Team B",
                "owner": "A. Owner",
                "due_in_days": 2,
                "blocked": True,
            }
        ]
    )

    result = json.loads(analyze_dependencies.run(dependencies_json=dependencies))

    assert result["blockers"] == ["D-1"]


def test_resource_tool_identifies_skill_gaps() -> None:
    result = json.loads(
        analyze_skill_gaps.run(
            required_skills_json='["Python", "Azure"]',
            available_skills_json='["python"]',
        )
    )

    assert result["skill_gaps"] == ["Azure"]
