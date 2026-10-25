import pytest

from tools.risk_engine import RiskCalculator


@pytest.mark.parametrize(
    ("probability", "impact", "score", "category"),
    [
        (1, 1, 1, "Low"),
        (2, 3, 6, "Medium"),
        (3, 4, 12, "High"),
        (5, 4, 20, "Critical"),
    ],
)
def test_probability_impact_score_and_category(
    probability: int, impact: int, score: int, category: str
) -> None:
    assessment = RiskCalculator().assess(probability, impact)

    assert assessment.score == score
    assert assessment.category == category
    assert assessment.mitigation


@pytest.mark.parametrize(("probability", "impact"), [(0, 2), (6, 1), (1, 9)])
def test_rejects_out_of_scale_values(probability: int, impact: int) -> None:
    with pytest.raises(ValueError):
        RiskCalculator().assess(probability, impact)
