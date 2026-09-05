# Contributing

Thanks for considering a contribution — this project is meant to be
useful to small sellers beyond just its original author, so outside
PRs are welcome.

## Getting set up

```bash
git clone https://github.com/<your-fork>/fraud-checker.git
cd fraud-checker
pip install -r requirements.txt
pytest
```

## Making a change

1. Fork the repo and create a branch off `main`.
2. Make your change. If you're adding a fraud-detection rule, put it in
   `fraud_checker/rules.py` and add it to `DEFAULT_RULES`.
3. Add or update tests in `tests/` — PRs without tests for new rules
   won't be merged.
4. Run `pytest` and make sure everything passes.
5. Open a pull request describing what changed and why. Link any
   related issue.

## What makes a good rule

A good fraud-detection rule is:
- **Explainable** — a plain-English `reason` string a non-technical
  store owner can understand.
- **Cheap** — no external API calls or heavy computation; this should
  stay fast enough to run at checkout.
- **Tunable** — thresholds/weights as function arguments with sane
  defaults, not hardcoded magic numbers.

## Reporting bugs / suggesting features

Open an issue. Bugs and small, well-scoped feature requests are also
what the weekly automated maintenance pass picks up from, so a clear
issue description is genuinely useful even if you don't plan to fix it
yourself.
