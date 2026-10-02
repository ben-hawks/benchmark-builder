# Repository snippets

Starting points for the benchmark repository described in `references/repo-structure.md`.
These are **snippets to adapt, not a skeleton to copy**. Generate each benchmark's repo
from the structure spec, and pull in a snippet where it fits. Every snippet uses the
placeholder package `benchpkg` and the env-var prefix `BENCH_`; rename both to the
benchmark's own (axess-benchmark uses `wa_hls4ml_bench` and `WA_`).

| Snippet | Becomes | Adapt |
|---|---|---|
| `score_all.sh` | `scripts/score_all.sh` | package name, splits, truth/score arguments |
| `submission.py` | `src/<pkg>/submission.py` | `SPLITS`, `scored_ids()` → this benchmark's cache + truth function |
| `report.py` | `src/<pkg>/report.py` | title, `PRIMARY`/`SECONDARY` metrics, `AUXILIARY` |
| `fetch_weights.py` | `scripts/fetch_weights.py` | `SMALL_ARTIFACTS` |
| `weights/MANIFEST.json` | `weights/MANIFEST.json` | one entry per checkpoint, with `role` reference/auxiliary |
| `tests/test_pipeline.py` | `tests/test_pipeline.py` | models, splits, weights, tolerances |
| `CITATION.cff` | `CITATION.cff` | fill `preferred-citation` from doi.org; `cffconvert --validate` |
| `.gitattributes` | `.gitattributes` | add binary types the repo stores |
| `gitignore.snippet` | append to `.gitignore` | local data/cache/results paths |

The reference implementation of every one of these is in
[ben-hawks/axess-benchmark](https://github.com/ben-hawks/axess-benchmark) at the same path.
