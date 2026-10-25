from pathlib import Path

import pytest

from tools.governance.approval_engine import ApprovalEngine


def test_routes_configured_decision_types() -> None:
    engine = ApprovalEngine()

    assert engine.route("release").approver == "CAB"
    assert engine.route("budget_overrun").approver == "Sponsor"


def test_routes_high_risk_to_programme_manager() -> None:
    route = ApprovalEngine().route("unspecified", "critical")

    assert route.approver == "Programme Manager"
    assert route.approval_type == "high_risk"


def test_missing_high_risk_rule_fails_closed(tmp_path: Path) -> None:
    config = tmp_path / "approval.yaml"
    config.write_text("approvals:\n  low_risk:\n    approver: ProjectManager\n", encoding="utf-8")
    engine = ApprovalEngine(config)

    with pytest.raises(KeyError):
        engine.route("unconfigured", "high")
