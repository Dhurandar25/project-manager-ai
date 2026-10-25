import pytest

from tools.governance.approval_engine import ApprovalEngine
from tools.governance.audit_logger import AuditLogger
from tools.governance.middleware import ApprovalMiddleware
from tools.governance.models import ApprovalRequest, HumanApproval


def test_execution_only_occurs_after_approval_and_audit(tmp_path) -> None:
    executed: list[bool] = []
    middleware = ApprovalMiddleware(ApprovalEngine(), AuditLogger(tmp_path))

    result = middleware.process(
        ApprovalRequest(
            decision="Deploy release",
            decision_type="release",
            risk_level="high",
            workflow="release_readiness",
            agent_source="release_agent",
        ),
        request_human_approval=lambda _decision, route: HumanApproval(
            outcome="approved", approver=f"{route.approver} Chair", approver_role=route.approver
        ),
        execute=lambda: executed.append(True),
    )

    assert result.executed is True
    assert executed == [True]
    assert (tmp_path / "decisions.jsonl").exists()


def test_rejection_does_not_execute(tmp_path) -> None:
    executed: list[bool] = []
    middleware = ApprovalMiddleware(ApprovalEngine(), AuditLogger(tmp_path))

    result = middleware.process(
        ApprovalRequest(
            decision="Increase budget",
            decision_type="budget_overrun",
            risk_level="medium",
            workflow="budget_review",
            agent_source="financial_agent",
        ),
        request_human_approval=lambda _decision, _route: HumanApproval(
            outcome="rejected", approver="Sponsor", approver_role="Sponsor"
        ),
        execute=lambda: executed.append(True),
    )

    assert result.executed is False
    assert not executed


def test_wrong_role_is_audited_and_cannot_execute(tmp_path) -> None:
    middleware = ApprovalMiddleware(ApprovalEngine(), AuditLogger(tmp_path))
    executed: list[bool] = []

    with pytest.raises(PermissionError, match="not authorized"):
        middleware.process(
            ApprovalRequest(
                decision="Deploy release",
                decision_type="release",
                workflow="release_readiness",
                agent_source="release_agent",
            ),
            request_human_approval=lambda _decision, _route: HumanApproval(
                outcome="approved", approver="Unauthorized user", approver_role="Sponsor"
            ),
            execute=lambda: executed.append(True),
        )
    assert not executed
    assert '"authorization_denied":true' in (tmp_path / "decisions.jsonl").read_text(encoding="utf-8")
