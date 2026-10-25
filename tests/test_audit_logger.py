import json
from pathlib import Path

import pytest

from tools.governance.audit_logger import AuditLogger


def test_audit_logger_persists_required_fields(tmp_path: Path) -> None:
    logger = AuditLogger(tmp_path)

    record = logger.log_decision(
        decision="Proceed with release",
        approver="CAB Chair",
        approval_outcome="approved",
        workflow="daily_governance",
        agent_source="approval_agent",
    )

    persisted = json.loads((tmp_path / "decisions.jsonl").read_text(encoding="utf-8"))
    assert persisted == record
    assert "timestamp" in record


def test_audit_logger_rejects_empty_identity(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="cannot be empty"):
        AuditLogger(tmp_path).log_decision(
            decision="Decision",
            approver=" ",
            approval_outcome="approved",
            workflow="workflow",
            agent_source="agent",
        )
