import pytest

from tools.intelligence import Dependency, DependencyIntelligence, ResourceIntelligence


def test_dependency_analysis_finds_longest_path_and_blocker_impact() -> None:
    dependencies = [
        Dependency("D1", "Team A", "Team B", "Owner A", 10, duration_days=3),
        Dependency("D2", "Team B", "Team C", "Owner B", 8, blocked=True, duration_days=4),
        Dependency("D3", "Team A", "Team C", "Owner A", 4, duration_days=5),
    ]

    report = DependencyIntelligence().analyze(dependencies)

    assert report.critical_path == ("D1", "D2")
    assert [item.dependency_id for item in report.blockers] == ["D2"]
    assert [item.dependency_id for item in report.at_risk_dependencies] == ["D3"]
    assert report.estimated_impact_days == 4


def test_dependency_analysis_rejects_circular_graph() -> None:
    dependencies = [
        Dependency("D1", "Team A", "Team B", "Owner A", 10, duration_days=1),
        Dependency("D2", "Team B", "Team A", "Owner B", 10, duration_days=1),
    ]

    with pytest.raises(ValueError, match="cycle"):
        DependencyIntelligence().analyze(dependencies)


def test_resource_skill_gap_comparison_is_case_insensitive() -> None:
    gaps = ResourceIntelligence().skill_gaps(["Python", "Azure"], ["python"])

    assert gaps == ("Azure",)
