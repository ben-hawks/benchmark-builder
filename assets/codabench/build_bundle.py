#!/usr/bin/env python3
"""Assemble a benchmark's Codabench competition bundle from bundle_src/ plus generated data.

TEMPLATE (benchmark-builder skill, assets/codabench/build_bundle.py). Becomes the
benchmark's codabench/build_bundle.py. Pattern from axess-benchmark; a runnable miniature
is assets/codabench/results_example/build_bundle.py. See references/codabench.md,
"Building the bundle from the benchmark".

    PYTHONPATH=src python codabench/build_bundle.py --cache-dir $BENCH_CACHE \
        --results-dir $BENCH_RESULTS --reference-model <model> --out codabench/build

Inputs (from a normal benchmark run):
    ground truth, read through the benchmark's own truth function (truth.truth_frame)
    <results-dir>/<split>/predictions_<reference-model>.csv   reference predictions

Writes (codabench/build/ is git-ignored):
    <out>/bundle/                    the bundle directory (validate this)
    <out>/competition_bundle.zip     the file to upload
    <out>/extra/baseline_submission.zip
        a deliberately weak submission for the discrimination check (reference vs
        baseline); not part of the bundle

Everything hidden or derived comes from the benchmark's own truth function, the same one
score.py and submission.py use, so the bundle can't diverge from the benchmark.

ADAPT:
  - rename benchpkg; set SPLITS to the splits a submission covers;
  - implement weak_baseline() for THIS task (see its docstring);
  - for a code submission, also generate input_data/ per task here, from the same loaders,
    instead of only reference_data/;
  - this shape assumes per-sample prediction files; adapt it for other output types.
"""

from __future__ import annotations

import argparse
import os
import shutil
import sys
import zipfile

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "src"))

from benchpkg import data as D  # noqa: E402
from benchpkg.truth import truth_frame  # noqa: E402  (the benchmark's single truth function)

SPLITS = ("test",)
ID_COLUMN = "sample_id"
OUTPUT_COLUMNS = list(D.OUTPUT_COLUMNS)
COLUMNS = [ID_COLUMN] + OUTPUT_COLUMNS


def weak_baseline(cache_dir: str, ids: pd.Series) -> pd.DataFrame | None:
    """Predictions a deliberately weak model would make for `ids`, or None to skip.

    Pick what is trivially weak for THIS task and say what it is in codabench/README.md,
    e.g. the training mean per output (regression; what axess-benchmark used), the majority
    class (classification), a random policy (control), or random samples from the training
    distribution (generative). Return a frame with COLUMNS.
    """
    return None


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


def scored_predictions(pred_csv, ids):
    df = pd.read_csv(pred_csv, dtype={ID_COLUMN: str}).set_index(ID_COLUMN)
    missing = ids[~ids.isin(df.index)]
    if len(missing):
        sys.exit(f"{pred_csv}: no prediction for {len(missing)} scored samples")
    out = df.loc[ids, OUTPUT_COLUMNS]
    if out.isna().any().any():
        sys.exit(f"{pred_csv}: missing values for scored samples")
    return out.reset_index()


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--cache-dir", required=True, help="where the truth function reads ground truth from")
    p.add_argument("--results-dir", required=True)
    p.add_argument("--reference-model", required=True,
                   help="whose predictions become solution/ and sample_submission.zip")
    p.add_argument("--out", default=os.path.join(HERE, "build"))
    args = p.parse_args()

    bundle = os.path.join(args.out, "bundle")
    extra = os.path.join(args.out, "extra")
    shutil.rmtree(args.out, ignore_errors=True)
    shutil.copytree(os.path.join(HERE, "bundle_src"), bundle,
                    ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    for d in (os.path.join(bundle, "reference_data"), os.path.join(bundle, "solution"), extra):
        os.makedirs(d, exist_ok=True)

    solution_files, baseline_files = [], []
    for split in SPLITS:
        truth = truth_frame(args.cache_dir, split)
        truth.to_csv(os.path.join(bundle, "reference_data", f"truth_{split}.csv"), index=False)
        truth[[ID_COLUMN]].to_csv(os.path.join(bundle, "starting_kit", f"{split}_sample_ids.csv"), index=False)

        pred = scored_predictions(
            os.path.join(args.results_dir, split, f"predictions_{args.reference_model}.csv"), truth[ID_COLUMN])
        path = os.path.join(bundle, "solution", f"predictions_{split}.csv")
        pred[COLUMNS].to_csv(path, index=False)
        solution_files.append(path)

        base = weak_baseline(args.cache_dir, truth[ID_COLUMN])
        if base is not None:
            path = os.path.join(extra, f"predictions_{split}.csv")
            base[COLUMNS].to_csv(path, index=False)
            baseline_files.append(path)
        print(f"{split}: {len(truth)} scored samples")

    zip_flat(os.path.join(bundle, "starting_kit", "sample_submission.zip"), solution_files)
    if baseline_files:
        zip_flat(os.path.join(extra, "baseline_submission.zip"), baseline_files)
        for path in baseline_files:
            os.remove(path)
    else:
        print("WARNING: weak_baseline() returned nothing; the discrimination check needs a weak baseline.")

    if not os.path.exists(os.path.join(bundle, "logo.png")):
        print("WARNING: no logo.png in bundle_src/. competition.yaml requires `image`; "
              "add it and rebuild before uploading.")
    zip_tree(os.path.join(args.out, "competition_bundle.zip"), bundle)
    size = os.path.getsize(os.path.join(args.out, "competition_bundle.zip")) / 1e6
    print(f"wrote {args.out}/competition_bundle.zip ({size:.1f} MB)")


if __name__ == "__main__":
    main()
