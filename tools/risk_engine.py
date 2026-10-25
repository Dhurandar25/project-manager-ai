"""Deterministic risk scoring and baseline mitigation recommendations."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from tools.config_loader import load_yaml


@dataclass(frozen=True)
class RiskAssessment:
    probability: int
    impact: int
    score: int
    category: str
    mitigation: str


class RiskCalculator:
    """Calculate a 1-25 probability-times-impact score using 1-5 inputs."""

    def __init__(self, config_path: Path | None = None) -> None:
        path = config_path or (
            Path(__file__).parents[1] / "config" / "governance_rules.yaml"
        )
        config = load_yaml(path)
        governance_config = config.get("governance")
        if not isinstance(governance_config, dict):
            raise ValueError("Governance configuration must define risk rules")
        risk_config = governance_config.get("risk")
        if not isinstance(risk_config, dict):
            raise ValueError("Governance configuration must define risk rules")
        self._probability_scale = self._read_scale(risk_config, "probability_scale")
        self._impact_scale = self._read_scale(risk_config, "impact_scale")
        configured_categories = risk_config.get("categories")
        configured_mitigations = risk_config.get("mitigations")
        required_categories = {"low", "medium", "high", "critical"}
        if not isinstance(configured_categories, dict) or set(configured_categories) != required_categories:
            raise ValueError("Risk configuration must define low, medium, high, and critical ranges")
        if not isinstance(configured_mitigations, dict) or not required_categories.issubset(
            configured_mitigations
        ):
            raise ValueError("Risk configuration must define mitigations for every category")
        self._categories: dict[str, tuple[int, int]] = {}
        for name, bounds in configured_categories.items():
            if not isinstance(bounds, list) or len(bounds) != 2:
                raise ValueError(f"Invalid score range for risk category {name!r}")
            minimum, maximum = bounds
            if (
                not isinstance(minimum, int)
                or not isinstance(maximum, int)
                or minimum < 1
                or minimum > maximum
            ):
                raise ValueError(f"Invalid score range for risk category {name!r}")
            self._categories[name] = (minimum, maximum)
        mitigations: dict[str, str] = {}
        for name in required_categories:
            mitigation = configured_mitigations[name]
            if not isinstance(mitigation, str) or not mitigation.strip():
                raise ValueError(f"Risk category {name!r} must define a mitigation")
            mitigations[name] = mitigation
        self._mitigations = mitigations
        for probability_value in range(
            self._probability_scale[0], self._probability_scale[1] + 1
        ):
            for impact_value in range(self._impact_scale[0], self._impact_scale[1] + 1):
                score = probability_value * impact_value
                matches = sum(
                    minimum <= score <= maximum
                    for minimum, maximum in self._categories.values()
                )
                if matches != 1:
                    raise ValueError(
                        f"Configured risk categories must cover score {score} exactly once"
                    )

    def assess(self, probability: int, impact: int) -> RiskAssessment:
        if not self._probability_scale[0] <= probability <= self._probability_scale[1]:
            raise ValueError(
                "Probability must be between "
                f"{self._probability_scale[0]} and {self._probability_scale[1]}"
            )
        if not self._impact_scale[0] <= impact <= self._impact_scale[1]:
            raise ValueError(
                f"Impact must be between {self._impact_scale[0]} and {self._impact_scale[1]}"
            )
        score = probability * impact
        category = next(
            (
                name
                for name, (minimum, maximum) in self._categories.items()
                if minimum <= score <= maximum
            ),
            None,
        )
        if category is None:
            raise ValueError(f"Risk score {score} is not covered by configured categories")
        return RiskAssessment(
            probability,
            impact,
            score,
            category.title(),
            self._mitigations[category],
        )

    @staticmethod
    def _read_scale(config: dict[str, object], key: str) -> tuple[int, int]:
        value = config.get(key)
        if not isinstance(value, list) or len(value) != 2:
            raise ValueError(f"Risk configuration must define a valid {key}")
        minimum, maximum = value
        if (
            not isinstance(minimum, int)
            or not isinstance(maximum, int)
            or minimum < 1
            or minimum > maximum
        ):
            raise ValueError(f"Risk configuration must define a valid {key}")
        return minimum, maximum
