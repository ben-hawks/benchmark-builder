# Evaluation

Two metrics, computed by `scoring_program/scoring.py`:

- **R²** (coefficient of determination) — primary leaderboard column, higher is better.
- **RMSE** (root mean square error) — secondary column, lower is better.

Both are computed once per phase, comparing your submitted predictions against the
held-out `testing_label.csv` for that phase. See `references/ontology.md`'s note on
Performance Metrics for why a benchmark should state its metric formulas exactly like
this rather than just naming them.
