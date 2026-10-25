"""CrewAI-callable wrappers for deterministic PMO analysis services."""

from __future__ import annotations

import json

from crewai.tools import tool

from tools.intelligence import (
    Dependency,
    DependencyIntelligence,
    ResourceIntelligence,
)
from tools.risk_engine import RiskCalculator


@tool("Calculate project risk score")
def calculate_project_risk(probability: int, impact: int) -> str:
    """Calculate probability times impact using integer inputs from 1 to 5."""
    assessment = RiskCalculator().assess(probability, impact)
    return json.dumps(
        {
            "probability": assessment.probability,
            "impact": assessment.impact,
            "score": assessment.score,
            "category": assessment.category,
            "mitigation": assessment.mitigation,
        }
    )


@tool("Forecast team capacity")
def forecast_team_capacity(capacity_hours: float, planned_hours: float) -> str:
    """Calculate utilization and capacity gap from weekly available and planned hours."""
    forecast = ResourceIntelligence().forecast(capacity_hours, planned_hours)
    return json.dumps(
        {
            "capacity_hours": forecast.capacity_hours,
            "planned_hours": forecast.planned_hours,
            "utilization_percent": forecast.utilization_percent,
            "capacity_gap_hours": forecast.capacity_gap_hours,
        }
    )


@tool("Analyze cross-team dependencies")
def analyze_dependencies(dependencies_json: str) -> str:
    """Analyze dependencies from a JSON array of dependency objects."""
    try:
        raw_dependencies = json.loads(dependencies_json)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Dependencies must be valid JSON: {exc}") from exc
    if not isinstance(raw_dependencies, list):
        raise ValueError("Dependencies must be a JSON array")
    dependencies = [Dependency(**item) for item in raw_dependencies]
    report = DependencyIntelligence().analyze(dependencies)
    return json.dumps(
        {
            "critical_dependencies": [item.dependency_id for item in report.critical_dependencies],
            "blockers": [item.dependency_id for item in report.blockers],
            "at_risk_dependencies": [
                item.dependency_id for item in report.at_risk_dependencies
            ],
            "critical_path": report.critical_path,
            "estimated_impact_days": report.estimated_impact_days,
        }
    )


@tool("Identify team skill gaps")
def analyze_skill_gaps(required_skills_json: str, available_skills_json: str) -> str:
    """Compare required and available skills supplied as JSON arrays of strings."""
    try:
        required_skills = json.loads(required_skills_json)
        available_skills = json.loads(available_skills_json)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Skills must be valid JSON: {exc}") from exc
    if not isinstance(required_skills, list) or not isinstance(available_skills, list):
        raise ValueError("Required and available skills must be JSON arrays")
    if not all(isinstance(skill, str) for skill in required_skills + available_skills):
        raise ValueError("Every skill must be a string")
    gaps = ResourceIntelligence().skill_gaps(required_skills, available_skills)
    return json.dumps({"skill_gaps": gaps})
