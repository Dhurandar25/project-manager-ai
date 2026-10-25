"""Reusable human approval gate that audits before allowing execution."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from tools.governance.approval_engine import ApprovalEngine, ApprovalRoute
from tools.governance.audit_logger import AuditLogger
from tools.governance.models import ApprovalRequest, HumanApproval

ApprovalCallback = Callable[[str, ApprovalRoute], HumanApproval]


@dataclass(frozen=True)
class ApprovalResult:
    """Outcome of approval routing and optional downstream execution."""

    route: ApprovalRoute
    outcome: str
    approver: str
    executed: bool


class ApprovalMiddleware:
    """Require an explicit human decision; execute only after approval and audit."""

    def __init__(self, engine: ApprovalEngine, audit_logger: AuditLogger) -> None:
        self._engine = engine
        self._audit_logger = audit_logger

    def process(
        self,
        request: ApprovalRequest,
        *,
        request_human_approval: ApprovalCallback,
        execute: Callable[[], None] | None = None,
    ) -> ApprovalResult:
        route = self._engine.route(request.decision_type, request.risk_level)
        human_approval = request_human_approval(request.decision, route)
        normalized_role = human_approval.approver_role.casefold()
        if normalized_role != route.approver.casefold():
            self._audit_logger.log_decision(
                decision=request.decision,
                approver=human_approval.approver,
                approval_outcome="rejected",
                workflow=request.workflow,
                agent_source=request.agent_source,
                metadata={
                    "required_role": route.approver,
                    "presented_role": human_approval.approver_role,
                    "authorization_denied": True,
                },
            )
            raise PermissionError(
                f"Approver role {human_approval.approver_role!r} is not authorized; "
                f"{route.approver!r} is required"
            )
        self._audit_logger.log_decision(
            decision=request.decision,
            approver=human_approval.approver,
            approval_outcome=human_approval.outcome,
            workflow=request.workflow,
            agent_source=request.agent_source,
            metadata={"required_role": route.approver, "approval_type": route.approval_type},
        )
        executed = human_approval.outcome == "approved"
        if executed and execute is not None:
            execute()
        return ApprovalResult(route, human_approval.outcome, human_approval.approver, executed)
