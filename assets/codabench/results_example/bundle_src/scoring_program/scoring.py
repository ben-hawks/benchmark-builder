"""Scoring program for the toy results-submission example (benchmark-builder skill).

A results submission: the participant runs their model offline and uploads a zip with one
predictions CSV per split (SUBMISSION_FILES below), each with columns sample_id + TARGETS.
They're scored against the hidden truth in reference_data/ (truth_<split>.csv), and
scores.json is written with keys matching competition.yaml's leaderboard columns.

Contract (pattern from axess-benchmark's codabench/bundle_src/scoring_program/scoring.py):
  - every scored sample needs a finite prediction; otherwise fail with a message naming
    the problem (missing file, missing column, duplicate id, missing sample, non-finite);
  - extra rows (unscored samples) are ignored;
  - one wrapping folder inside the zip is tolerated;
  - NaN scores are written as null (JSON has no NaN).

SUBMISSION_FILES is the declared submission contract. The skill's validator reads this
constant (tier 2) instead of guessing filenames from the code. Building the paths with
a literal file name passed to os.path.join on prediction_dir (as PREDICTION_FILES does)
also keeps its regex fallback working for validators that don't read the constant.

CODABENCH_ROOT defaults to /app, the layout of a real Codabench container; the
validator overrides it to dry-run this program locally.
"""

import json
import math
import os
import sys

import numpy as np
import pandas as pd

from metrics import r_squared, rmse

ROOT = os.environ.get("CODABENCH_ROOT", "/app")
reference_dir = os.path.join(ROOT, "input", "ref")
prediction_dir = os.path.join(ROOT, "input", "res")
score_dir = os.path.join(ROOT, "output")

SPLITS = ("test", "holdout")
TARGETS = ["y"]

# The submission must provide exactly these files at the root of its zip.
SUBMISSION_FILES = ["predictions_test.csv", "predictions_holdout.csv"]
PREDICTION_FILES = {
    "test": os.path.join(prediction_dir, "predictions_test.csv"),
    "holdout": os.path.join(prediction_dir, "predictions_holdout.csv"),
}


def fail(msg):
    print(f"SUBMISSION ERROR: {msg}", file=sys.stderr)
    sys.exit(1)


def find_file(split):
    """Codabench unzips the submission into input/res. Tolerate a wrapping folder."""
    expected = PREDICTION_FILES[split]
    if os.path.exists(expected):
        return expected
    name = os.path.basename(expected)
    for dirpath, _, files in os.walk(prediction_dir):
        if name in files:
            return os.path.join(dirpath, name)
    fail(f"'{name}' not found in the submission. Zip {' and '.join(SUBMISSION_FILES)} "
         "at the root of the archive.")


def load_predictions(split, truth):
    name = os.path.basename(PREDICTION_FILES[split])
    pred = pd.read_csv(find_file(split), dtype={"sample_id": str})
    missing_cols = [c for c in ["sample_id"] + TARGETS if c not in pred.columns]
    if missing_cols:
        fail(f"{name} is missing columns {missing_cols}")
    if pred["sample_id"].duplicated().any():
        fail(f"{name} has duplicate sample_id values")
    pred = pred.set_index("sample_id")
    missing = truth.index.difference(pred.index)
    if len(missing):
        fail(f"{name} has no prediction for {len(missing)} of {len(truth)} scored samples "
             f"(e.g. {list(missing[:3])}); every scored sample is required")
    pred = pred.loc[truth.index, TARGETS]  # extra rows are ignored here
    try:
        values = pred.to_numpy(dtype=float)
    except ValueError:
        fail(f"{name} contains non-numeric predictions")
    if not np.isfinite(values).all():
        fail(f"{name} contains NaN/inf predictions for scored samples")
    return pd.DataFrame(values, index=truth.index, columns=TARGETS)


def main():
    scores = {}
    for split in SPLITS:
        truth = pd.read_csv(os.path.join(reference_dir, f"truth_{split}.csv"),
                            dtype={"sample_id": str}).set_index("sample_id")
        pred = load_predictions(split, truth)
        for t in TARGETS:
            scores[f"{split}_r2"] = r_squared(truth[t], pred[t])
            scores[f"{split}_rmse"] = rmse(truth[t], pred[t])
        print(f"[{split}] n={len(truth)} R^2={scores[f'{split}_r2']:.4f} RMSE={scores[f'{split}_rmse']:.4f}")

    scores = {k: (None if isinstance(v, float) and math.isnan(v) else v) for k, v in scores.items()}
    print("Scores:", json.dumps(scores))
    os.makedirs(score_dir, exist_ok=True)
    with open(os.path.join(score_dir, "scores.json"), "w") as f:
        json.dump(scores, f)


if __name__ == "__main__":
    main()
