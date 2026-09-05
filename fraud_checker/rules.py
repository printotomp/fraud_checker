"""Individual fraud-signal rules.

Each rule takes an Order and returns a RuleResult (0 points = clean).
Rules are intentionally simple, explainable heuristics — the goal is a
transparent first line of defence a small merchant can tune, not a
black-box ML model requiring a data science team.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta

from .models import Order


@dataclass
class RuleResult:
    rule_name: str
    triggered: bool
    points: int
    reason: str


def rule_billing_shipping_mismatch(order: Order) -> RuleResult:
    mismatch = order.billing_address.country != order.shipping_address.country
    return RuleResult(
        rule_name="billing_shipping_mismatch",
        triggered=mismatch,
        points=15 if mismatch else 0,
        reason=(
            f"Billing country ({order.billing_address.country}) differs from "
            f"shipping country ({order.shipping_address.country})"
            if mismatch
            else "Billing and shipping countries match"
        ),
    )


def rule_ip_country_mismatch(order: Order) -> RuleResult:
    if not order.ip_country:
        return RuleResult("ip_country_mismatch", False, 0, "No IP country supplied")
    mismatch = order.ip_country != order.billing_address.country
    return RuleResult(
        rule_name="ip_country_mismatch",
        triggered=mismatch,
        points=10 if mismatch else 0,
        reason=(
            f"Checkout IP country ({order.ip_country}) differs from billing "
            f"country ({order.billing_address.country})"
            if mismatch
            else "IP country matches billing country"
        ),
    )


def rule_card_country_mismatch(order: Order) -> RuleResult:
    if not order.card_country:
        return RuleResult("card_country_mismatch", False, 0, "No card country supplied")
    mismatch = order.card_country != order.billing_address.country
    return RuleResult(
        rule_name="card_country_mismatch",
        triggered=mismatch,
        points=15 if mismatch else 0,
        reason=(
            f"Card issuing country ({order.card_country}) differs from billing "
            f"country ({order.billing_address.country})"
            if mismatch
            else "Card country matches billing country"
        ),
    )


def rule_high_value_new_customer(order: Order, threshold: float = 300.0) -> RuleResult:
    triggered = order.is_new_customer and order.amount >= threshold
    return RuleResult(
        rule_name="high_value_new_customer",
        triggered=triggered,
        points=20 if triggered else 0,
        reason=(
            f"New customer placing a {order.currency} {order.amount:.2f} order "
            f"(threshold {threshold:.2f})"
            if triggered
            else "Order value normal for a new customer, or customer is returning"
        ),
    )


def rule_order_velocity(
    order: Order, window_minutes: int = 60, max_orders: int = 3
) -> RuleResult:
    """Flags a burst of orders from the same customer in a short window.

    Common pattern for card testing (stolen card numbers run through
    small orders quickly) or checkout automation abuse.
    """
    window_start = order.created_at - timedelta(minutes=window_minutes)
    recent = [t for t in order.recent_order_timestamps if t >= window_start]
    triggered = len(recent) >= max_orders
    return RuleResult(
        rule_name="order_velocity",
        triggered=triggered,
        points=25 if triggered else 0,
        reason=(
            f"{len(recent)} orders from this customer in the last "
            f"{window_minutes} minutes (limit {max_orders})"
            if triggered
            else "Order frequency within normal range"
        ),
    )


def rule_unusually_large_basket(order: Order, threshold: int = 10) -> RuleResult:
    triggered = order.items_count >= threshold
    return RuleResult(
        rule_name="unusually_large_basket",
        triggered=triggered,
        points=10 if triggered else 0,
        reason=(
            f"{order.items_count} items in a single order (threshold {threshold})"
            if triggered
            else "Basket size normal"
        ),
    )


def rule_missing_customer_id(order: Order) -> RuleResult:
    triggered = order.customer_id is None
    return RuleResult(
        rule_name="missing_customer_id",
        triggered=triggered,
        points=5 if triggered else 0,
        reason=(
            "Guest checkout with no linked customer account"
            if triggered
            else "Order linked to a customer account"
        ),
    )


DEFAULT_RULES = [
    rule_billing_shipping_mismatch,
    rule_ip_country_mismatch,
    rule_card_country_mismatch,
    rule_high_value_new_customer,
    rule_order_velocity,
    rule_unusually_large_basket,
    rule_missing_customer_id,
]
