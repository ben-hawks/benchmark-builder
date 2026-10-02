"""Package benchmark predictions as upload-ready Codabench submission zips.

    python -m benchpkg.submission --results $BENCH_RESULTS --cache-dir $BENCH_CACHE

For every model with predictions for all SPLITS (``<results>/<split>/predictions_<model>.csv``),
writes ``<results>/codabench/<model>_submission.zip`` holding ``predictions_<split>.csv`` for
each split at the zip root. Each file has exactly the scored samples (the same set as the
Codabench bundle's hidden truth, because both come from the benchmark's single truth
function) and the columns ID_COLUMN + OUTPUT_COLUMNS.

It applies the same checks as the Codabench scoring program, so a zip written here is
ready to upload, and an incomplete model gets no zip and a non-zero exit.
scripts/score_all.sh runs this after scoring.

ADAPT (assets/repo/submission.py in the benchmark-builder skill):
  - rename benchpkg; set SPLITS to the splits a submission must cover;
  - point scored_ids() at this benchmark's truth function;
  - make check_values() enforce what a valid output is for THIS task (finite numbers for
    regression, a label from the class set for classification, ...);
  - this shape assumes one prediction row per sample. A task whose output isn't per-sample
    (generated samples, a policy, a ranking) needs its own packaging, with the same
    flat-zip and refuse-if-incomplete rules.
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
from .truth import scored_ids  # the benchmark's single truth function (ids of scored samples)

SPLITS = ("test",)                      # every split a Codabench submission must contain
ID_COLUMN = "sample_id"
OUTPUT_COLUMNS = list(D.OUTPUT_COLUMNS)  # what a prediction file must contain besides the id
COLUMNS = [ID_COLUMN] + OUTPUT_COLUMNS


class SubmissionError(ValueError):
    pass


def check_values(out: pd.DataFrame, label: str) -> None:
    """Reject invalid predictions for scored samples. Default: numeric and finite.
    ADAPT for the task's output type."""
    try:
        values = out.to_numpy(dtype=float)
    except ValueError:
        raise SubmissionError(f"{label}: non-numeric predictions") from None
    if not np.isfinite(values).all():
        raise SubmissionError(f"{label}: NaN/inf predictions for scored samples")


def select_scored(pred: pd.DataFrame, ids: pd.Series, label: str) -> pd.DataFrame:
    """Rows for exactly the scored ids, in their order; raises SubmissionError if incomplete."""
    missing_cols = [c for c in COLUMNS if c not in pred.columns]
    if missing_cols:
        raise SubmissionError(f"{label}: missing columns {missing_cols}")
    if pred[ID_COLUMN].duplicated().any():
        raise SubmissionError(f"{label}: duplicate {ID_COLUMN} values")
    pred = pred.set_index(ID_COLUMN)
    missing = ids[~ids.isin(pred.index)]
    if len(missing):
        raise SubmissionError(f"{label}: no prediction for {len(missing)} of {len(ids)} scored samples "
                              f"(e.g. {list(missing[:3])})")
    out = pred.loc[ids.to_numpy(), OUTPUT_COLUMNS]
    check_values(out, label)
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
    p.add_argument("--cache-dir", required=True, help="where the truth function reads ground truth from")
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
                pred = pd.read_csv(path, dtype={ID_COLUMN: str})
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
