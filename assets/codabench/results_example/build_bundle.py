#!/usr/bin/env python3
"""Build the toy results-submission bundle: bundle_src/ + generated data -> build/.

    python assets/codabench/results_example/build_bundle.py
    python scripts/validate_codabench_bundle.py assets/codabench/results_example/build/bundle \
        --submission assets/codabench/results_example/build/bundle/starting_kit/sample_submission.zip

A runnable miniature of the pattern in ../build_bundle.py (and axess-benchmark's
codabench/build_bundle.py). The "benchmark" here is the code-submission example's toy
data (../example_bundle): split "test" = dev-phase test set, "holdout" = final-phase test
set, reference model = least squares on the training set, weak baseline = training mean.

Everything hidden or derived (truth, scored-id lists, solution, sample submission, weak
baseline) comes from ONE truth function, truth_frame(), the way a real benchmark's
build_bundle.py imports its package's truth.truth_frame, so the bundle can't diverge
from the benchmark. To show that unscored samples are handled, the last test sample is
treated as "missing ground truth": excluded from truth, but still predicted (the scoring
program ignores extra rows).

Writes (build/ is git-ignored, regenerate it):
    build/bundle/                         the bundle directory (validate this)
    build/competition_bundle.zip          what would be uploaded
    build/extra/baseline_mean_submission.zip   weak baseline, for the discrimination check
"""

import os
import shutil
import zipfile

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "example_bundle")
SPLITS = {"test": "dev_phase", "holdout": "final_phase"}
TARGETS = ["y"]
COLUMNS = ["sample_id"] + TARGETS


def load_split(split):
    phase = SPLITS[split]
    X = np.loadtxt(os.path.join(DATA, phase, "input_data", "testing_data.csv"), delimiter=",")
    y = np.loadtxt(os.path.join(DATA, phase, "reference_data", "testing_label.csv"), delimiter=",")
    ids = [f"{split}-{i:03d}" for i in range(len(y))]
    return ids, X, y


def truth_frame(split):
    """The single truth function: scored samples only (missing ground truth excluded)."""
    ids, _, y = load_split(split)
    df = pd.DataFrame({"sample_id": ids, "y": y})
    if split == "test":
        df = df.iloc[:-1]  # pretend the last sample has no ground truth
    return df.reset_index(drop=True)


def zip_flat(zip_path, files):
    """Zip files at the archive root (Codabench expects no wrapping folder)."""
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as z:
        for path in files:
            z.write(path, arcname=os.path.basename(path))


def zip_tree(zip_path, root):
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as z:
        for dirpath, _, files in os.walk(root):
            for name in sorted(files):
                path = os.path.join(dirpath, name)
                z.write(path, arcname=os.path.relpath(path, root))


def main():
    out = os.path.join(HERE, "build")
    bundle, extra = os.path.join(out, "bundle"), os.path.join(out, "extra")
    shutil.rmtree(out, ignore_errors=True)
    shutil.copytree(os.path.join(HERE, "bundle_src"), bundle,
                    ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    for d in (os.path.join(bundle, "reference_data"), os.path.join(bundle, "solution"), extra):
        os.makedirs(d, exist_ok=True)

    X_train = np.loadtxt(os.path.join(DATA, "public_data", "training_data.csv"), delimiter=",")
    y_train = np.loadtxt(os.path.join(DATA, "public_data", "training_label.csv"), delimiter=",")
    A = np.c_[X_train, np.ones(len(X_train))]
    coef, *_ = np.linalg.lstsq(A, y_train, rcond=None)

    solution_files, baseline_files = [], []
    for split in SPLITS:
        truth = truth_frame(split)
        truth.to_csv(os.path.join(bundle, "reference_data", f"truth_{split}.csv"), index=False)
        truth[["sample_id"]].to_csv(os.path.join(bundle, "starting_kit", f"{split}_sample_ids.csv"), index=False)

        ids, X, _ = load_split(split)  # predictions cover every sample, scored or not
        pred = pd.DataFrame({"sample_id": ids, "y": np.c_[X, np.ones(len(X))] @ coef})
        path = os.path.join(bundle, "solution", f"predictions_{split}.csv")
        pred[COLUMNS].to_csv(path, index=False)
        solution_files.append(path)

        base = pd.DataFrame({"sample_id": truth["sample_id"], "y": float(y_train.mean())})
        path = os.path.join(extra, f"predictions_{split}.csv")
        base.to_csv(path, index=False)
        baseline_files.append(path)
        print(f"{split}: {len(truth)} scored of {len(ids)} samples")

    zip_flat(os.path.join(bundle, "starting_kit", "sample_submission.zip"), solution_files)
    zip_flat(os.path.join(extra, "baseline_mean_submission.zip"), baseline_files)
    for path in baseline_files:
        os.remove(path)
    zip_tree(os.path.join(out, "competition_bundle.zip"), bundle)
    print(f"wrote {os.path.join(out, 'competition_bundle.zip')}")


if __name__ == "__main__":
    main()
