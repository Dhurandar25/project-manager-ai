"""Config-driven approval routing for project decisions."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from tools.config_loader import load_yaml


@dataclass(frozen=True)
class ApprovalRoute:
    """Configured human role and routing key for an approval request."""

    approval_type: str
    approver: str


class ApprovalEngine:
    """Resolve decision types and risk levels using approval_matrix.yaml."""

    def __init__(self, config_path: Path | None = None) -> None:
        self._config_path = config_path or (
            Path(__file__).parents[2] / "config" / "approval_matrix.yaml"
        )
        config = load_yaml(self._config_path)
        approvals = config.get("approvals")
        if not isinstance(approvals, dict) or not approvals:
            raise ValueError("Approval configuration must define a non-empty 'approvals' map")
        self._approvals: dict[str, dict[str, str]] = {}
        for key, value in approvals.items():
            if not isinstance(value, dict) or not isinstance(value.get("approver"), str):
                raise ValueError(f"Approval entry {key!r} must define an approver")
            self._approvals[key] = value

    def route(self, decision_type: str, risk_level: str = "low") -> ApprovalRoute:
        """Return configured approver; unknown high/critical risks fail closed."""
        normalized_type = decision_type.strip().lower()
        normalized_risk = risk_level.strip().lower()
        if normalized_type in self._approvals:
            selected = normalized_type
        elif normalized_risk in {"high", "critical"}:
            selected = "high_risk"
        else:
            selected = "low_risk"
        if selected not in self._approvals:
            raise KeyError(f"No approval rule configured for {selected!r}")
        return ApprovalRoute(selected, self._approvals[selected]["approver"])
