# Starting kit — Toy Linear Regression (example bundle)

Welcome! This is a minimal worked example shipped with the benchmark-builder skill —
it exists to prove out the Codabench bundle mechanics, not as an interesting ML task.

## Task

Given two features `x1, x2`, predict a continuous target `y`. Training data is in
`public_data/`. The real held-out test inputs live in each phase's `input_data/` and
are only visible to the ingestion program at scoring time — you won't see them directly.

## What you need to submit

A zip file containing **`model.py` at its root** (no wrapping folder), defining a
class `Model` with:

```python
class Model:
    def __init__(self): ...
    def fit(self, X, y): ...       # X: (n, 2) array, y: (n,) array
    def predict(self, X): ...      # returns an (n,) array of predictions
```

`model.py` in this folder is a deliberately weak baseline (predicts the training
mean) — replace it with your own approach, keeping the same interface, then zip just
that one file:

```bash
cd starting_kit
zip -j my_submission.zip model.py
```

`sample_submission.zip` in this folder is a ready-to-upload example (the reference
solution — ordinary least squares) if you want to see a working submission before
writing your own.

## Scoring

Your predictions are compared against the held-out labels using R² and RMSE (see
`pages/evaluation.md`). Both appear on the leaderboard; R² is the primary ranking
column (higher is better).
