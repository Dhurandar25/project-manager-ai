"""Validated governance request models."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, field_validator


class ApprovalRequest(BaseModel):
    """Structured recommendation context required before asking for approval."""

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    decision: str
    decision_type: str
    risk_level: str = "low"
    workflow: str
    agent_source: str

    @field_validator("decision", "decision_type", "workflow", "agent_source")
    @classmethod
    def require_non_empty_value(cls, value: str) -> str:
        if not value:
            raise ValueError("Approval request fields cannot be empty")
        return value

    @field_validator("risk_level")
    @classmethod
    def normalize_risk_level(cls, value: str) -> str:
        normalized = value.lower()
        if normalized not in {"low", "medium", "high", "critical"}:
            raise ValueError("Risk level must be low, medium, high, or critical")
        return normalized


class HumanApproval(BaseModel):
    """Human decision and role resolved by the host's authenticated identity layer."""

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    outcome: Literal["approved", "rejected", "deferred"]
    approver: str
    approver_role: str

    @field_validator("outcome", mode="before")
    @classmethod
    def normalize_outcome(cls, value: str) -> str:
        if isinstance(value, str):
            return value.strip().lower()
        return value

    @field_validator("approver", "approver_role")
    @classmethod
    def require_non_empty_value(cls, value: str) -> str:
        if not value:
            raise ValueError("Approver identity and role cannot be empty")
        return value
