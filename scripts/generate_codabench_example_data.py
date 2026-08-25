#!/usr/bin/env python3
"""Deterministically regenerate the toy dataset used by
assets/codabench/example_bundle/ (the skill's self-contained, runnable worked example
for the Codabench adaptation step).

The task is a trivial 2-feature linear regression (y = 2*x1 - 3*x2 + 5 + noise) --
intentionally simple, since the point of this fixture is to exercise the *bundle
mechanics* (ingestion -> scoring -> leaderboard keys), not to be an interesting ML
problem. Re-run this script if the example bundle's data ever needs regenerating;
it's deterministic (fixed seed) so the output is always identical.

Usage: python generate_codabench_example_data.py [output_dir]
(defaults to ../assets/codabench/example_bundle relative to this script)
"""

import os
import sys

import numpy as np

SEED = 42
N_TRAIN = 60
N_DEV_TEST = 20
N_FINAL_TEST = 20
TRUE_WEIGHTS = np.array([2.0, -3.0])
TRUE_BIAS = 5.0
NOISE_STD = 0.5


def make_split(rng, n):
    X = rng.uniform(-5, 5, size=(n, 2))
    y = X @ TRUE_WEIGHTS + TRUE_BIAS + rng.normal(0, NOISE_STD, size=n)
    return X, y


def write_csv(path, array):
    np.savetxt(path, array, delimiter=",", fmt="%.6f")


def main():
    out_dir = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
        os.path.dirname(__file__), "..", "assets", "codabench", "example_bundle"
    )
    rng = np.random.default_rng(SEED)

    X_train, y_train = make_split(rng, N_TRAIN)
    X_dev_test, y_dev_test = make_split(rng, N_DEV_TEST)
    X_final_test, y_final_test = make_split(rng, N_FINAL_TEST)

    for phase, X_test, y_test in [
        ("dev_phase", X_dev_test, y_dev_test),
        ("final_phase", X_final_test, y_final_test),
    ]:
        input_dir = os.path.join(out_dir, phase, "input_data")
        ref_dir = os.path.join(out_dir, phase, "reference_data")
        os.makedirs(input_dir, exist_ok=True)
        os.makedirs(ref_dir, exist_ok=True)
        write_csv(os.path.join(input_dir, "training_data.csv"), X_train)
        write_csv(os.path.join(input_dir, "training_label.csv"), y_train)
        write_csv(os.path.join(input_dir, "testing_data.csv"), X_test)
        write_csv(os.path.join(ref_dir, "testing_label.csv"), y_test)

    public_dir = os.path.join(out_dir, "public_data")
    os.makedirs(public_dir, exist_ok=True)
    write_csv(os.path.join(public_dir, "training_data.csv"), X_train)
    write_csv(os.path.join(public_dir, "training_label.csv"), y_train)
    write_csv(os.path.join(public_dir, "testing_data.csv"), X_dev_test)
    write_csv(os.path.join(public_dir, "testing_label.csv"), y_dev_test)

    print(f"Wrote dev_phase, final_phase, and public_data CSVs under {out_dir}")


if __name__ == "__main__":
    main()
