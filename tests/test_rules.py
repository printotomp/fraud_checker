from datetime import datetime, timedelta

from fraud_checker.models import Address, Order
from fraud_checker.scorer import FraudScorer, Verdict


def make_order(**overrides) -> Order:
    defaults = dict(
        order_id="ord_1",
        customer_email="buyer@example.com",
        customer_id="cust_1",
        amount=50.0,
        currency="GBP",
        billing_address=Address(country="GB", postcode="SW1A 1AA"),
        shipping_address=Address(country="GB", postcode="SW1A 1AA"),
        ip_country="GB",
        created_at=datetime(2026, 1, 1, 12, 0, 0),
        is_new_customer=False,
        previous_order_count=5,
        recent_order_timestamps=[],
        items_count=2,
        card_country="GB",
    )
    defaults.update(overrides)
    return Order(**defaults)


def test_clean_order_is_allowed():
    order = make_order()
    report = FraudScorer().score(order)
    assert report.verdict == Verdict.ALLOW
    assert report.triggered_rules == []


def test_billing_shipping_mismatch_adds_points():
    order = make_order(shipping_address=Address(country="NG", postcode="100001"))
    report = FraudScorer().score(order)
    names = {r.rule_name for r in report.triggered_rules}
    assert "billing_shipping_mismatch" in names
    assert report.total_points >= 15


def test_high_value_new_customer_flags_review():
    order = make_order(is_new_customer=True, amount=350.0)
    report = FraudScorer().score(order)
    names = {r.rule_name for r in report.triggered_rules}
    assert "high_value_new_customer" in names
    assert report.verdict in (Verdict.REVIEW, Verdict.BLOCK)


def test_order_velocity_triggers_on_burst():
    now = datetime(2026, 1, 1, 12, 0, 0)
    order = make_order(
        created_at=now,
        recent_order_timestamps=[
            now - timedelta(minutes=5),
            now - timedelta(minutes=10),
            now - timedelta(minutes=20),
        ],
    )
    report = FraudScorer().score(order)
    names = {r.rule_name for r in report.triggered_rules}
    assert "order_velocity" in names


def test_multiple_signals_stack_to_block():
    order = make_order(
        is_new_customer=True,
        amount=500.0,
        shipping_address=Address(country="NG", postcode="100001"),
        ip_country="RU",
        card_country="CN",
        customer_id=None,
        items_count=15,
    )
    report = FraudScorer().score(order)
    assert report.verdict == Verdict.BLOCK
    assert report.total_points >= 45


def test_missing_customer_id_is_low_weight_alone():
    order = make_order(customer_id=None)
    report = FraudScorer().score(order)
    assert report.verdict == Verdict.ALLOW
