# House rules for automated changes

This repo gets a weekly automated pass (see `.github/workflows/weekly-claude.yml`).
To keep that safe and useful, automated changes must follow these rules:

1. **One change per run.** Either fix one bug, close one issue, or add one
   small feature/rule. Do not bundle unrelated changes.
2. **Never lower detection thresholds silently.** Changes to
   `fraud_checker/scorer.py` review/block thresholds must come with tests
   demonstrating why the new values are correct.
3. **Every rule needs a test.** Any new function in `rules.py` needs a
   corresponding test in `tests/test_rules.py` covering both the triggered
   and non-triggered case.
4. **No new third-party dependencies** without a clear reason in the PR
   description — this project is meant to stay lightweight and auditable.
5. **Always open a pull request.** Never push directly to `main`.
6. **Run `pytest` before finishing** and make sure it's green.
7. **Don't touch `.github/workflows/`** in an automated run — workflow
   changes should be reviewed by a human directly.
