"""Aggregates individual rule results into an overall risk verdict."""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from .models import Order
from .rules import DEFAULT_RULES, RuleResult


class Verdict(str, Enum):
    ALLOW = "allow"
    REVIEW = "review"
    BLOCK = "block"


@dataclass
class ScoreReport:
    order_id: str
    total_points: int
    verdict: Verdict
    triggered_rules: list[RuleResult] = field(default_factory=list)
    all_rules: list[RuleResult] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "order_id": self.order_id,
            "total_points": self.total_points,
            "verdict": self.verdict.value,
            "triggered_rules": [r.__dict__ for r in self.triggered_rules],
        }


class FraudScorer:
    """Runs a configurable set of rules against an order and produces a verdict.

    Thresholds are intentionally conservative defaults — tune them against
    your own chargeback/false-positive history rather than trusting them
    blindly out of the box.
    """

    def __init__(
        self,
        rules=None,
        review_threshold: int = 20,
        block_threshold: int = 45,
    ):
        self.rules = rules if rules is not None else DEFAULT_RULES
        self.review_threshold = review_threshold
        self.block_threshold = block_threshold

    def score(self, order: Order) -> ScoreReport:
        results = [rule(order) for rule in self.rules]
        total = sum(r.points for r in results)

        if total >= self.block_threshold:
            verdict = Verdict.BLOCK
        elif total >= self.review_threshold:
            verdict = Verdict.REVIEW
        else:
            verdict = Verdict.ALLOW

        return ScoreReport(
            order_id=order.order_id,
            total_points=total,
            verdict=verdict,
            triggered_rules=[r for r in results if r.triggered],
            all_rules=results,
        )
