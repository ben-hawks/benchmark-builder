"""Package benchmark predictions as upload-ready Codabench submission zips.

    python -m benchpkg.submission --results $BENCH_RESULTS --cache-dir $BENCH_CACHE

For every model with predictions for all SPLITS (``<results>/<split>/predictions_<model>.csv``),
writes ``<results>/codabench/<model>_submission.zip`` holding ``predictions_<split>.csv`` for
each split at the zip root. Each file has exactly the scored samples (the same set as the
Codabench bundle's hidden truth, because both come from truth.truth_frame) and the columns
sample_id + data.TARGETS.

It applies the same checks as the Codabench scoring program (a finite prediction for every
scored sample, no duplicate ids, all columns present), so a zip written here is ready to
upload, and an incomplete model gets no zip and a non-zero exit. scripts/score_all.sh runs
this after scoring.

ADAPT (assets/repo/submission.py in the benchmark-builder skill): rename benchpkg, set
SPLITS to the splits a submission must cover, and point scored_ids() at this benchmark's
cache reader and truth function. Keep the checks and the flat zip layout.
"""

from __future__ import annotations

import argparse
import glob
import os
import sys
import tempfile
import zipfile

import numpy as np
import pandas as pd

from . import data as D
from .cache import SplitCache
from .truth import truth_frame

SPLITS = ("test",)  # every split a Codabench submission must contain
COLUMNS = ["sample_id"] + D.TARGETS


class SubmissionError(ValueError):
    pass


def scored_ids(cache_dir: str, split: str) -> pd.Series:
    """The scored sample ids of a split, from the single truth function."""
    cache = SplitCache(os.path.join(cache_dir, f"{split}.npz"))
    return truth_frame(cache)["sample_id"]


def select_scored(pred: pd.DataFrame, ids: pd.Series, label: str) -> pd.DataFrame:
    """Rows for exactly the scored ids, in their order; raises SubmissionError if incomplete."""
    missing_cols = [c for c in COLUMNS if c not in pred.columns]
    if missing_cols:
        raise SubmissionError(f"{label}: missing columns {missing_cols}")
    if pred["sample_id"].duplicated().any():
        raise SubmissionError(f"{label}: duplicate sample_id values")
    pred = pred.set_index("sample_id")
    missing = ids[~ids.isin(pred.index)]
    if len(missing):
        raise SubmissionError(f"{label}: no prediction for {len(missing)} of {len(ids)} scored samples "
                              f"(e.g. {list(missing[:3])})")
    out = pred.loc[ids.to_numpy(), D.TARGETS]
    if not np.isfinite(out.to_numpy(dtype=float)).all():
        raise SubmissionError(f"{label}: NaN/inf predictions for scored samples")
    return out.reset_index()[COLUMNS]


def write_submission(frames: dict, zip_path: str) -> None:
    os.makedirs(os.path.dirname(os.path.abspath(zip_path)), exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp, \
            zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as z:
        for split, df in frames.items():
            name = f"predictions_{split}.csv"
            path = os.path.join(tmp, name)
            df.to_csv(path, index=False)
            z.write(path, arcname=name)  # zip root, no wrapping folder


def models_with_predictions(results: str) -> list[str]:
    first, rest = SPLITS[0], SPLITS[1:]
    found = []
    for path in sorted(glob.glob(os.path.join(results, first, "predictions_*.csv"))):
        model = os.path.basename(path)[len("predictions_"):-len(".csv")]
        lacking = [s for s in rest if not os.path.exists(os.path.join(results, s, f"predictions_{model}.csv"))]
        if lacking:
            print(f"{model}: no predictions for {lacking}, skipped", file=sys.stderr)
        else:
            found.append(model)
    return found


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--results", required=True, help="results dir with <split>/predictions_<model>.csv")
    p.add_argument("--cache-dir", required=True, help="dir with <split>.npz")
    p.add_argument("--models", nargs="+", help="default: every model with predictions for all splits")
    p.add_argument("--out", help="default: <results>/codabench")
    args = p.parse_args(argv)

    out_dir = args.out or os.path.join(args.results, "codabench")
    ids = {split: scored_ids(args.cache_dir, split) for split in SPLITS}
    failed = 0
    for model in args.models or models_with_predictions(args.results):
        try:
            frames = {}
            for split in SPLITS:
                path = os.path.join(args.results, split, f"predictions_{model}.csv")
                pred = pd.read_csv(path, dtype={"sample_id": str})
                frames[split] = select_scored(pred, ids[split], f"{model}/{split}")
        except (SubmissionError, FileNotFoundError) as e:
            print(f"{model}: NOT packaged: {e}", file=sys.stderr)
            failed += 1
            continue
        zip_path = os.path.join(out_dir, f"{model}_submission.zip")
        write_submission(frames, zip_path)
        rows = " + ".join(f"{len(frames[s])} {s}" for s in SPLITS)
        print(f"{model}: wrote {zip_path} ({rows} rows)")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
