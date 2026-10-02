# Repository snippets

Starting points for the benchmark repository described in `references/repo-structure.md`.
These are **snippets to adapt, not a skeleton to copy**. Generate each benchmark's repo
from the structure spec, and pull in a snippet where it fits.

Every snippet uses the placeholder package `benchpkg` and the env-var prefix `BENCH_`;
rename both to the benchmark's own (axess-benchmark uses `wa_hls4ml_bench` and `WA_`).

The snippets assume the package provides:
- `data.OUTPUT_COLUMNS`;
- `truth.truth_frame(cache_dir, split)` and `truth.scored_ids(cache_dir, split)`, the
  single truth function;
- per-sample prediction CSVs keyed by `sample_id`.

Everything task-specific is left as a hook to fill from this benchmark's own decisions:
metrics, what counts as a valid prediction, the weak baseline, test tolerances, and the
cache format. None of them defaults to axess's choices.

| Snippet | Becomes | Adapt |
|---|---|---|
| `score_all.sh` | `scripts/score_all.sh` | package name, splits, truth/score arguments |
| `submission.py` | `src/<pkg>/submission.py` | `SPLITS`; `check_values()` for this task's output type; a different packager if outputs aren't per-sample |
| `report.py` | `src/<pkg>/report.py` | `TITLE`, `METRICS` (required), `SUMMARY_METRIC`, `AUXILIARY` |
| `fetch_weights.py` | `scripts/fetch_weights.py` | `SMALL_ARTIFACTS` (often none) |
| `weights/MANIFEST.json` | `weights/MANIFEST.json` | one entry per checkpoint, with `role` reference/auxiliary |
| `tests/test_pipeline.py` | `tests/test_pipeline.py` | models, splits, weights, entry points, and `RTOL`/`ATOL` from measured spread (required) |
| `CITATION.cff` | `CITATION.cff` | fill `preferred-citation` from doi.org; `cffconvert --validate` |
| `.gitattributes` | `.gitattributes` | add binary types the repo stores |
| `gitignore.snippet` | append to `.gitignore` | local data/cache/results paths |

The reference implementation of each is in
[ben-hawks/axess-benchmark](https://github.com/ben-hawks/axess-benchmark) at the same path,
with axess's own choices filled in. Read it as an example of filled-in hooks, not as
defaults.
