"""Collect every <results>/<split>/<model>/metrics.json into one LEADERBOARD.md.

    python -m benchpkg.report --results $BENCH_RESULTS --out $BENCH_RESULTS/LEADERBOARD.md

Auxiliary models (scored for comparison, not reference solutions) are listed in AUXILIARY
and rendered as italic "(auxiliary)" rows, matching reference_solution/README.md.

ADAPT (assets/repo/report.py in the benchmark-builder skill):
  - set TITLE, METRICS (the benchmark's own metrics, in column order) and AUXILIARY;
  - SUMMARY_METRIC adds a mean-over-outputs column; set it to None unless averaging that
    metric across outputs is meaningful for this benchmark;
  - this version assumes score.py writes
    {"coverage": {...}, "groups": {"all": {<output>: {<metric>: value}}}}. Change the
    lookups if this benchmark's metrics.json is shaped differently (e.g. one value per
    metric instead of per output).
"""

from __future__ import annotations

import argparse
import glob
import json
import math
import os

from .data import OUTPUT_COLUMNS

TITLE = "<benchmark> leaderboard"
METRICS: list[str] = []            # e.g. axess-benchmark: ["r_squared", "smape"]
SUMMARY_METRIC: str | None = None  # e.g. axess-benchmark: "r_squared" (mean R² over targets)
AUXILIARY: set[str] = set()        # comparison models that aren't reference solutions
FMT = ".3f"


def _fmt(x):
    return "N/A" if x is None or (isinstance(x, float) and math.isnan(x)) else format(x, FMT)


def build(results_dir: str) -> str:
    if not METRICS:
        raise SystemExit("report.py: set METRICS to this benchmark's metric names")
    cols = [f"{o} {m}" for m in METRICS for o in OUTPUT_COLUMNS]
    if SUMMARY_METRIC:
        cols.append(f"mean {SUMMARY_METRIC}")
    lines = [f"# {TITLE}", "",
             "Per-group tables are in each `<split>/<model>/METRICS.md`.",
             "Rows in *italics* are auxiliary comparison models, not reference solutions.", ""]
    for split_dir in sorted(glob.glob(os.path.join(results_dir, "*", ""))):
        split = os.path.basename(os.path.normpath(split_dir))
        runs = sorted(glob.glob(os.path.join(split_dir, "*", "metrics.json")))
        if not runs:
            continue
        lines += [f"## {split}", "", "| Model | coverage | " + " | ".join(cols) + " |",
                  "|---" * (2 + len(cols)) + "|"]
        for path in runs:
            with open(path) as f:
                m = json.load(f)
            model = os.path.basename(os.path.dirname(path))
            if model in AUXILIARY:
                model = f"*{model} (auxiliary)*"
            res, cov = m["groups"]["all"], m["coverage"]
            cells = [res[o][met] for met in METRICS for o in OUTPUT_COLUMNS]
            if SUMMARY_METRIC:
                vals = [res[o][SUMMARY_METRIC] for o in OUTPUT_COLUMNS]
                finite = [v for v in vals if v is not None and not math.isnan(v)]
                cells.append(sum(finite) / len(finite) if finite else float("nan"))
            lines.append(f"| {model} | {cov['n_scored']}/{cov['n_truth']} | "
                         + " | ".join(_fmt(v) for v in cells) + " |")
        lines.append("")
    return "\n".join(lines)


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--results", required=True)
    p.add_argument("--out", required=True)
    args = p.parse_args(argv)
    md = build(args.results)
    with open(args.out, "w", encoding="utf-8") as f:
        f.write(md)
    print(md)


if __name__ == "__main__":
    main()
