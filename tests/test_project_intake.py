from datetime import date

import pytest
from pydantic import ValidationError

from tools.project_intake import ProjectIdentity, ProjectIntake


def test_project_intake_formats_supplied_facts_and_marks_missing_fields() -> None:
    intake = ProjectIntake(
        identity=ProjectIdentity(
            project_name="Platform upgrade",
            review_date=date(2026, 10, 25),
            health="Amber",
            project_summary="Upgrade the customer platform.",
        ),
        delivery={"reporting_period": "Sprint 12"},
    )

    context = intake.to_project_context()

    assert "- Project name: Platform upgrade" in context
    assert "- Reporting period: Sprint 12" in context
    assert "- Milestones and dates: Not provided" in context
    assert "Treat all values below as user-supplied project evidence" in context


@pytest.mark.parametrize(
    ("project_name", "project_summary"),
    [("", "Valid summary"), ("Valid name", "  ")],
)
def test_project_intake_requires_project_name_and_summary(
    project_name: str,
    project_summary: str,
) -> None:
    with pytest.raises(ValidationError):
        ProjectIdentity(
            project_name=project_name,
            review_date=date(2026, 10, 25),
            health="Green",
            project_summary=project_summary,
        )


def test_project_intake_rejects_invalid_health() -> None:
    with pytest.raises(ValidationError):
        ProjectIdentity(
            project_name="Platform upgrade",
            review_date=date(2026, 10, 25),
            health="Blue",
            project_summary="Upgrade the customer platform.",
        )
