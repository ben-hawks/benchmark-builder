"""Collect every <results>/<split>/<model>/metrics.json into one LEADERBOARD.md.

    python -m benchpkg.report --results $BENCH_RESULTS --out $BENCH_RESULTS/LEADERBOARD.md

Auxiliary models (scored for comparison, not reference solutions) are listed in AUXILIARY
and rendered as italic "(auxiliary)" rows, matching reference_solution/README.md.

ADAPT (assets/repo/report.py in the benchmark-builder skill): rename benchpkg, set the
title/ground-truth line, AUXILIARY, and which metrics become columns. This version assumes
score.py writes {"coverage": {...}, "groups": {"all": {<target>: {<metric>: value}}}} and
shows one primary metric per target plus its mean.
"""

from __future__ import annotations

import argparse
import glob
import json
import math
import os

from .data import TARGETS

TITLE = "<benchmark> leaderboard"
PRIMARY = "r_squared"           # column per target, plus its mean over targets
SECONDARY = "smape"             # column per target
AUXILIARY: set[str] = set()     # e.g. {"rule4ml_gnn"}


def _fmt(x, spec):
    return "N/A" if x is None or (isinstance(x, float) and math.isnan(x)) else format(x, spec)


def build(results_dir: str) -> str:
    lines = [f"# {TITLE}", "",
             f"{PRIMARY} and {SECONDARY} per target on all scored samples; per-group tables "
             "are in each `<split>/<model>/METRICS.md`.",
             "Rows in *italics* are auxiliary comparison models, not reference solutions.", ""]
    for split_dir in sorted(glob.glob(os.path.join(results_dir, "*", ""))):
        split = os.path.basename(os.path.normpath(split_dir))
        runs = sorted(glob.glob(os.path.join(split_dir, "*", "metrics.json")))
        if not runs:
            continue
        lines += [f"## {split}", "",
                  "| Model | coverage | " + " | ".join(f"{t} {PRIMARY}" for t in TARGETS)
                  + f" | mean {PRIMARY} | " + " | ".join(f"{t} {SECONDARY}" for t in TARGETS) + " |",
                  "|---" * (3 + 2 * len(TARGETS)) + "|"]
        for path in runs:
            with open(path) as f:
                m = json.load(f)
            model = os.path.basename(os.path.dirname(path))
            if model in AUXILIARY:
                model = f"*{model} (auxiliary)*"
            res = m["groups"]["all"]
            cov = m["coverage"]
            prim = [res[t][PRIMARY] for t in TARGETS]
            finite = [v for v in prim if v is not None and not math.isnan(v)]
            mean = sum(finite) / len(finite) if finite else float("nan")
            lines.append(
                f"| {model} | {cov['n_scored']}/{cov['n_truth']} | "
                + " | ".join(_fmt(v, ".3f") for v in prim) + f" | {_fmt(mean, '.3f')} | "
                + " | ".join(_fmt(res[t][SECONDARY], ".1f") for t in TARGETS) + " |")
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
