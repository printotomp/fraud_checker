# Order Fraud Checker

A lightweight, explainable fraud-risk API for small online sellers who
can't afford (or don't need) enterprise fraud tooling like Stripe Radar
add-ons or Signifyd. Point your checkout at it, get back a verdict —
`allow`, `review`, or `block` — plus a plain-English list of exactly
which signals fired and why.

## Why this exists

Enterprise fraud tools are built for large order volumes and come with
enterprise pricing. A lot of indie stores just want the basics covered:
mismatched billing/shipping countries, a burst of orders in a short
window, a brand-new customer placing an unusually large order, and so
on. This project covers that gap with simple, tunable, auditable rules
— no black-box model, no vendor lock-in.

## How it works

Each incoming order is run through a set of independent rules
(`fraud_checker/rules.py`). Each rule contributes points if it fires.
The total is compared against two thresholds:

| Total points | Verdict |
|---|---|
| < 20 | `allow` |
| 20–44 | `review` |
| ≥ 45 | `block` |

Rules included out of the box:

- Billing vs shipping country mismatch
- Checkout IP country vs billing country mismatch
- Card issuing country vs billing country mismatch
- High-value order from a new customer
- Order velocity (burst of orders in a short window — classic card-testing pattern)
- Unusually large basket
- Guest checkout with no linked account

Thresholds and point weights are defaults, not gospel — tune them
against your own chargeback history in `fraud_checker/scorer.py`.

## Quick start

```bash
pip install -r requirements.txt
pytest                                   # run the test suite
uvicorn fraud_checker.api:app --reload   # start the API on :8000
```

Then:

```bash
curl -X POST http://localhost:8000/check-order \
  -H "Content-Type: application/json" \
  -d '{
    "order_id": "ord_123",
    "customer_email": "buyer@example.com",
    "customer_id": null,
    "amount": 450.00,
    "currency": "GBP",
    "billing_address": {"country": "GB", "postcode": "SW1A 1AA"},
    "shipping_address": {"country": "NG", "postcode": "100001"},
    "ip_country": "RU",
    "created_at": "2026-09-05T12:00:00",
    "is_new_customer": true,
    "items_count": 12
  }'
```

## Using it as a library

```python
from datetime import datetime
from fraud_checker import Order, Address, FraudScorer

order = Order(
    order_id="ord_123",
    customer_email="buyer@example.com",
    customer_id=None,
    amount=450.00,
    currency="GBP",
    billing_address=Address(country="GB", postcode="SW1A 1AA"),
    shipping_address=Address(country="NG", postcode="100001"),
    ip_country="RU",
    created_at=datetime.utcnow(),
    is_new_customer=True,
    items_count=12,
)

report = FraudScorer().score(order)
print(report.verdict, report.total_points)
for rule in report.triggered_rules:
    print("-", rule.reason)
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Forks and PRs welcome — this is
meant to be genuinely useful to other small sellers, not just a solo
project. Issue and PR templates live under `.github/` so both bot-driven
and human contributions come in with the same structure.

### Repo settings for accepting outside PRs

These are one-time settings you set in GitHub itself (Settings tab), not
anything in this codebase:

1. **Settings → General → "Allow forking"** — on by default for public
   repos, just confirm it's not disabled.
2. **Settings → Branches → Add branch protection rule** for `main`:
   require a pull request before merging, and optionally require the
   `pytest` check (once you add a CI workflow that runs it) to pass
   before merge. This is what actually lets you accept PRs safely —
   external contributors work on their own fork/branch and can never
   push to `main` directly.
3. **Settings → Actions → General → Fork pull request workflows** —
   decide whether Actions run automatically on PRs from forks or need
   approval first (recommended: require approval for first-time
   contributors, so a malicious PR can't run arbitrary code in your
   Actions environment).

## License

MIT — see [LICENSE](LICENSE).
