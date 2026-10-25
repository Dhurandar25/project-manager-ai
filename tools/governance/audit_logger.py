"""Append-only JSON Lines audit records for human approval decisions."""

from __future__ import annotations

import json
import logging
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)
_REQUIRED_FIELDS = ("decision", "approver", "approval_outcome", "workflow", "agent_source")


class AuditLogger:
    """Persist decision evidence as one UTF-8 JSON record per line."""

    def __init__(self, audit_dir: Path | None = None) -> None:
        self._audit_dir = audit_dir or Path(__file__).parents[2] / "logs" / "audit"
        self._lock = threading.Lock()

    def log_decision(
        self,
        *,
        decision: str,
        approver: str,
        approval_outcome: str,
        workflow: str,
        agent_source: str,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Validate, timestamp, and durably append a decision record."""
        record: dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "decision": decision,
            "approver": approver,
            "approval_outcome": approval_outcome,
            "workflow": workflow,
            "agent_source": agent_source,
        }
        missing = [field for field in _REQUIRED_FIELDS if not record[field].strip()]
        if missing:
            raise ValueError(f"Audit record fields cannot be empty: {', '.join(missing)}")
        if metadata:
            record["metadata"] = metadata
        try:
            self._audit_dir.mkdir(parents=True, exist_ok=True)
            target = self._audit_dir / "decisions.jsonl"
            serialized = json.dumps(record, ensure_ascii=True, separators=(",", ":"))
            with self._lock, target.open("a", encoding="utf-8") as stream:
                stream.write(serialized + "\n")
                stream.flush()
        except (OSError, TypeError, ValueError) as exc:
            logger.exception("Unable to persist governance audit decision")
            raise RuntimeError(f"Unable to persist audit decision: {exc}") from exc
        return record
