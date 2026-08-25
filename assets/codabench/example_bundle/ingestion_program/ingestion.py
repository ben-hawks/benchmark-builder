"""Ingestion program for the toy linear-regression example bundle.

Reads the participant's submitted model.py (from CODABENCH_ROOT/ingested_program),
trains it on the task's training data, predicts on the test inputs, and writes the
prediction plus timing metadata for the scoring program to consume.

CODABENCH_ROOT defaults to /app to match a real Codabench container exactly; a local
dry run (see scripts/validate_codabench_bundle.py) overrides it to a temp directory so
this same script can be tested without Docker. See references/codabench.md.
"""

import json
import os
import sys
import time

import numpy as np

ROOT = os.environ.get("CODABENCH_ROOT", "/app")
input_dir = os.path.join(ROOT, "input_data")
output_dir = os.path.join(ROOT, "output")
program_dir = os.path.join(ROOT, "program")
submission_dir = os.path.join(ROOT, "ingested_program")

sys.path.append(program_dir)
sys.path.append(submission_dir)


def get_training_data():
    X_train = np.genfromtxt(os.path.join(input_dir, "training_data.csv"), delimiter=",")
    y_train = np.genfromtxt(os.path.join(input_dir, "training_label.csv"), delimiter=",")
    return X_train, y_train


def get_prediction_data():
    return np.genfromtxt(os.path.join(input_dir, "testing_data.csv"), delimiter=",")


def main():
    from model import Model  # provided by the participant's submission

    print("Reading data")
    X_train, y_train = get_training_data()
    X_test = get_prediction_data()

    print("Training model")
    start = time.time()
    m = Model()
    m.fit(X_train, y_train)

    print("Running prediction")
    prediction = m.predict(X_test)
    duration = time.time() - start
    print(f"Completed prediction in {duration:.4f}s")

    os.makedirs(output_dir, exist_ok=True)
    np.savetxt(os.path.join(output_dir, "prediction.csv"), prediction, delimiter=",")
    with open(os.path.join(output_dir, "metadata.json"), "w") as f:
        json.dump({"duration": duration}, f)

    print("Ingestion finished.")


if __name__ == "__main__":
    main()
