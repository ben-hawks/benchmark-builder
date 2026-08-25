"""Scoring program for the toy linear-regression example bundle.

Compares the ingestion program's prediction.csv (or, for a results-only submission, a
participant-uploaded prediction.csv directly) against the held-out testing_label.csv,
and writes scores.json with keys matching competition.yaml's leaderboard columns.

CODABENCH_ROOT defaults to /app to match a real Codabench container exactly; a local
dry run (see scripts/validate_codabench_bundle.py) overrides it to a temp directory.
See references/codabench.md.
"""

import json
import os

import numpy as np

from metrics import r_squared, rmse

ROOT = os.environ.get("CODABENCH_ROOT", "/app")
reference_dir = os.path.join(ROOT, "input", "ref")
prediction_dir = os.path.join(ROOT, "input", "res")
score_dir = os.path.join(ROOT, "output")


def main():
    print("Reading prediction and reference")
    prediction = np.genfromtxt(os.path.join(prediction_dir, "prediction.csv"), delimiter=",")
    truth = np.genfromtxt(os.path.join(reference_dir, "testing_label.csv"), delimiter=",")

    duration = -1.0
    metadata_path = os.path.join(prediction_dir, "metadata.json")
    if os.path.exists(metadata_path):
        with open(metadata_path) as f:
            duration = json.load(f).get("duration", -1.0)

    scores = {
        "r_squared": r_squared(truth, prediction),
        "rmse": rmse(truth, prediction),
        "duration": duration,
    }
    print("Scores:", scores)

    os.makedirs(score_dir, exist_ok=True)
    with open(os.path.join(score_dir, "scores.json"), "w") as f:
        json.dump(scores, f)


if __name__ == "__main__":
    main()
