"""Structured Pydantic model for executive project health reporting."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class ExecutiveReport(BaseModel):
    """Validated executive report shape returned by the reporting task."""

    model_config = ConfigDict(extra="forbid")

    project_health: Literal["Green", "Amber", "Red"]
    executive_summary: str
    top_risks: list[str] = Field(default_factory=list)
    budget_forecast: str
    capacity_forecast: str
    actions_required: list[str] = Field(default_factory=list)
    upcoming_decisions: list[str] = Field(default_factory=list)
    evidence_gaps: list[str] = Field(default_factory=list)
