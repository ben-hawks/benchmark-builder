# Evaluation

Upload a zip with `predictions_test.csv` and `predictions_holdout.csv` at its root, each
with columns `sample_id,y` and one row per sample (the starting kit lists the ids).
Every scored sample needs a finite prediction; extra rows are ignored.

Ranking: test-split R² (higher is better), then test RMSE. Holdout R² and RMSE are shown
for generalization but don't set the rank.
