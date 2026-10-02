# Benchmark repository structure

This is the layout the skill **recommends strongly by default** for every benchmark it
builds. It's generalized from
[ben-hawks/axess-benchmark](https://github.com/ben-hawks/axess-benchmark), the wa-hls4ml
benchmark built with this skill. That repo self-scores 5.00/5, is a validated Codabench
bundle, and its first full NERSC Perlmutter run reproduced the committed reference results
to ≤2.4e-4 relative. Treat it as the worked example to pattern-match against.

**Generate the tree. Don't copy a skeleton.** Which optional pieces exist, which models,
splits and targets there are, whether there's a training step, and which machines it
runs on all vary per benchmark. Build each file from its contract below, adapted to this
benchmark. The small reusable snippets in `assets/repo/`, `assets/hpc/slurm/` and
`assets/codabench/` are starting points to adapt, not files to drop in unchanged.

**Recommended, not required.** Propose this layout and explain what it buys:

- one uniform pipeline every model runs through;
- a participant's model plugs in by writing one CSV;
- Codabench submissions and the competition bundle come out of the same code, so they
  can't drift from the benchmark.

If the user wants a different layout, or existing working code makes a reorganization more
expensive than it's worth, deviate. Keep the **pipeline contract** below even then, since
that's the part that makes results comparable. Record the deviation in the README so a
reader isn't surprised.

## Canonical layout

`<pkg>` is the benchmark's Python package (axess: `wa_hls4ml_bench`). `<hpc>` is one
directory per cluster family, or a single `slurm/` with per-machine profiles. Entries
marked *(optional)* depend on the benchmark (see "When the optional pieces apply").

```
<repo>/
├── README.md                  benchmark card: 5 ontology elements + quick start + reference results table + known limitations
├── SUBMISSION.md              submission report template (required / strongly recommended / suggested)
├── CITATION.cff               top level = this software; preferred-citation = the paper (DOI)
├── LICENSE                    code license (distinct from the dataset license; README states both)
├── rubric.yaml, SCORE_REPORT.md   self-score + scorer output, kept current
├── pyproject.toml             installable package; extras per model family
├── requirements*.txt          one per environment that must stay separate (e.g. torch vs TF)
├── .gitattributes             `* text=auto eol=lf` plus binary types
├── data/SCHEMA.md             per-field schema: which field is ground truth, which fields are NOT valid inputs
├── docs/
│   ├── VALIDATION.md          how the reference solutions were verified (numbers, dates, hardware)
│   └── <MACHINE>.md           (optional) running on a target cluster: paths, setup, jobs, troubleshooting
├── reference_solution/README.md   per-model table (documentation only, no code)
├── reference_results/         committed outputs of a full run
│   ├── LEADERBOARD.md
│   └── <split>/<model>/{METRICS.md, metrics.json, <plot>.png}
├── weights/
│   ├── MANIFEST.json          per file: URL, sha256, bytes, provenance
│   └── <stats>.json           (optional) small artifacts the weights need (normalization stats, caps)
├── src/<pkg>/
│   ├── data.py                load the dataset (streaming), sample_id rule, ground-truth extraction
│   ├── cache.py               featurize once into a compact cache; multiprocessing
│   ├── features.py            (optional) vendored upstream preprocessing, kept bit-identical
│   ├── stats.py               (optional) one-time rebuild of preprocessing artifacts (provenance only)
│   ├── models/<model>.py      vendored or wrapped model definitions + loaders
│   ├── train.py               (optional) only when the benchmark includes training
│   ├── predict.py             CLI: model × split → predictions CSV (all samples)
│   ├── truth.py               CLI: split → truth CSV (scored samples only)
│   ├── score.py               CLI: metrics overall + per group → METRICS.md, metrics.json, plots
│   ├── report.py              all metrics.json → LEADERBOARD.md (auxiliary models marked)
│   └── submission.py          predictions → upload-ready Codabench zip per model
├── scripts/
│   ├── fetch_data.py          download + record the exact dataset revision
│   ├── fetch_weights.py       download + verify sha256 from weights/MANIFEST.json
│   └── score_all.sh           truth → score every predictions_*.csv → leaderboard → submission zips
├── <hpc>/                     (optional) env.sh, setup.sh, submit.sh, jobs/*.sbatch, tuned per machine
├── codabench/                 (optional)
│   ├── README.md              mode, phases, ranking, validation record, pre-upload checklist
│   ├── build_bundle.py        bundle_src + generated truth/solution/ids → build/competition_bundle.zip
│   └── bundle_src/            competition.yaml, logo.png, pages/, scoring_program/ (vendored metrics), starting_kit/
└── tests/
    ├── test_score.py          metric edge cases (ε, zero variance, NaN rejection)
    ├── test_pipeline.py       golden predictions on real fixture samples (CPU; <PREFIX>_TEST_DEVICE=cuda on GPU)
    ├── test_features_equivalence.py   (optional) bit-equivalence vs upstream preprocessing
    ├── test_submission.py     packaging + refusal of incomplete predictions
    └── fixtures/              a few dozen real samples per split/subset + golden_*.csv
```

The old layout this replaces (`reference_solution/` holding code, a standalone
`metrics/score.py`, one environment file) broke down in practice:

- Code in `reference_solution/` mixed documentation with code that several commands
  share, such as data loading, featurization and scoring.
- A standalone scorer couldn't do truth extraction, per-group breakdowns, a leaderboard
  and submission packaging off the same loader and sample IDs.
- One environment file can't hold reference models with conflicting stacks, such as a
  TensorFlow baseline next to a site PyTorch module.

## The pipeline contract

Every benchmark's run is the same steps, with the same file conventions:

```
fetch_data → cache (featurize) → [train (optional)] → predict (per model, per split) → score_all.sh
                                                         ↑                              (truth, score, leaderboard, submissions)
                                       fetch_weights (sha256-checked), or weights from train
```

| File | Written by | Contents |
|---|---|---|
| `<results>/<split>/predictions_<model>.csv` | `predict` (or a participant) | `sample_id` + one column per target, **every** sample of the split |
| `<results>/<split>/truth.csv` | `truth` | `sample_id` + grouping column(s) + targets, **scored samples only** |
| `<results>/<split>/<model>/metrics.json`, `METRICS.md`, plots | `score` | metrics overall and per group, plus a coverage block |
| `<results>/LEADERBOARD.md` | `report` | one table per split, every model, auxiliary rows marked |
| `<results>/codabench/<model>_submission.zip` | `submission` | upload-ready Codabench results submission |

A participant's model plugs in by writing `predictions_<name>.csv` for each split and
re-running `score_all.sh`; nothing else changes. Say exactly this in the README and in
`SUBMISSION.md`.

Paths come from environment variables with a benchmark-specific prefix (axess: `WA_`; the
snippets use `BENCH_`, so rename them): `<P>_DATA`, `<P>_CACHE`, `<P>_WEIGHTS`,
`<P>_RESULTS`, `<P>_SPLITS`. The same commands then work on a laptop and in Slurm jobs.

## Per-file contracts

### Top level

- **README.md**: start from `assets/benchmark_card_template.md`. On top of the five
  elements it needs:
  - a copy-pasteable quick start (local and, if any, per cluster);
  - a reference-results table copied from `reference_results/LEADERBOARD.md`, with the
    date and hardware of the run;
  - a **Known limitations** section;
  - both licenses (code and dataset) stated separately.
- **SUBMISSION.md**: from `assets/submission_report_template.md`. Tell participants to
  write `predictions_<name>.csv` and run `score_all.sh`, which also produces the
  Codabench zip.
- **CITATION.cff**: shape in `assets/repo/CITATION.cff`, rules in "Citations" below.
- **rubric.yaml / SCORE_REPORT.md**: from `assets/rubric_template.yaml`. Keep its `notes:`
  block dated and current (see SKILL.md § Iterate).
- **pyproject.toml**: an installable package (`src/` layout) with core deps (numpy,
  pandas, plotting, streaming JSON parser) and **extras per model family** (`torch`,
  `mlp`, `fetch`, `test`). A user installs only what the models they run need.
- **requirements*.txt**: one per environment that has to stay separate. axess has
  `requirements.txt` (torch stack on a site PyTorch module) and `requirements-mlp.txt`
  (TensorFlow plus rule4ml, which drags in its own torch). Pin versions the reference
  run used.
- **.gitattributes**: `assets/repo/.gitattributes`. Shell and sbatch files authored on
  Windows otherwise check out with CRLF and fail on the cluster with `$'\r': command not
  found`.

### data/SCHEMA.md

Every field of a sample, with its type and meaning. State explicitly:

- which field is the ground truth;
- which fields are **not valid model inputs**, because they're labels or are derived from
  them. axess's dataset carries `hls_resource_report` next to the ground truth
  `resource_report`, and a model fed one to predict the other would be cheating;
- the `sample_id` rule and its fallbacks (axess: `meta_data.uuid`, but the `2_20` subset
  only has `meta_data.model_id`). The rule must be unique per split, and `cache.py`
  enforces it;
- how missing ground truth is represented and that such samples are excluded from scoring.

### docs/VALIDATION.md

How the reference solutions were verified, with actual numbers, dates, hardware and
software versions. This is what turns "we ran it" into evidence. Sections, as applicable:

1. Preprocessing equivalence with upstream (bit-identical test, sample count).
2. Rebuilt preprocessing artifacts (stats, caps) vs the shipped originals, with max
   relative difference.
3. Per-sample agreement with upstream predictions when those exist, e.g. "max
   |ours − theirs| / (|theirs| + 1) = 2.8e-4 over 92,933 samples".
4. Reproduction of published table cells, and which metric variant reproduces them
   (SKILL.md element C).
5. The training-label audit: which label each reference model was trained on, proven
   on data (SKILL.md element D).
6. Feature-extraction gaps found and how they're handled.
7. Runs on each target machine: job IDs, exit codes, and agreement with
   `reference_results/`.

Anything superseded (e.g. checkpoints that were reference solutions until a retrain) gets
a dated "History" section, not deletion.

### reference_solution/README.md

Documentation only; code lives in `src/<pkg>/models/`. One table, one column per model,
with an extra column for each **auxiliary** model. Rows:

- code location in this repo;
- upstream repo, commit or tag, and paper section;
- weights (file + sha256 prefix, or "bundled in package X==v");
- input representation and architecture;
- **training labels** (which field or definition);
- training recipe (upstream), with epochs/early stopping as reported;
- output post-processing (inverse transform, clamps, caps);
- parameter count, inference hardware and measured cost.

Then a prose section on the preprocessing the models depend on, and why each auxiliary
model is auxiliary.

### reference_results/

The committed outputs of one full run: `LEADERBOARD.md` plus
`<split>/<model>/{METRICS.md, metrics.json, plot}`. Prediction CSVs are usually too big
to commit; metrics are what later runs compare against (docs/VALIDATION.md §7). Re-run
and re-commit when anything that changes numbers changes.

### weights/

- **MANIFEST.json**: shape in `assets/repo/weights/MANIFEST.json`. Per file: download
  `url`, `sha256`, `bytes`, and a `model` or provenance string naming the architecture
  class, the training labels and the source commit or release. Only **reference** and
  **auxiliary** weights the benchmark actually runs go in it. Mark which is which.
- **Small derived artifacts** (normalization stats, prediction caps, vocabularies) that
  the checkpoints need but don't contain go here as versioned files.
  `scripts/fetch_weights.py` copies them next to the downloaded checkpoints.

### src/<pkg>/

- **data.py**: dataset loading, the split list, the target column order (`TARGETS`, used
  by every CSV), `sample_id()`, the grouping used for per-group metrics, and one
  ground-truth function per truth definition. Defaults:
  - **Stream large files.** For JSON arrays use `ijson.items(f, "item", use_float=True)`,
    which yields the same types as `json.load`. axess has a 1.9 GB file that didn't fit
    in the workstation's free memory.
  - **Missing ground truth → excluded, never imputed.** Return `None`/NaN, and report
    coverage (n_truth, n_scored, n_truth_without_prediction,
    n_predictions_without_truth) everywhere metrics are reported.
  - **The training-label filter isn't the scoring filter.** Anything that reproduces
    training, such as rebuilding normalization stats, must use the upstream converter's
    exact filter. Scoring uses the benchmark's own. In axess the converter kept samples
    whose latency report was missing (latency read as 0), giving 433,676 train samples vs
    the benchmark filter's 433,674, which changes the stats. Keep both as separate
    functions.
- **cache.py**: featurize each split once into a compact cache (axess: ragged per-layer
  features + offsets + all truth arrays in one `.npz`).
  - Use `multiprocessing.Pool.imap` with a chunksize, which keeps order.
  - Assert `sample_id` uniqueness when building.
  - Make the reader **tolerant of older cache formats**: a column added later
    (`truth_train`) broke loading caches from an earlier cluster run. Treat new arrays as
    optional on read (`z["x"] if "x" in z.files else None`).
- **features.py** *(optional)*: when a reference model depends on upstream preprocessing,
  vendor it **verbatim**, including its quirks, with a header naming the upstream file
  and commit. Any fix (axess fills NaN precision for one exemplar architecture from the
  global config) must be a separate, switchable step, so the equivalence test can check
  the unmodified path.
- **stats.py** *(optional)*: rebuilds shipped preprocessing artifacts from the training
  split, for provenance only. The pipeline reads the shipped file.
- **models/<model>.py**: vendored model class (load the checkpoint with `strict=True`) or
  a thin wrapper around a pip-installed package. Include the post-processing that's part
  of the published inference procedure: inverse transform, clamps, caps.
- **train.py** *(optional)*: see "Score-only vs includes training".
- **predict.py**: `--model M --split S` (or `--cache`) `--out predictions_M.csv`, plus
  `--device`. Writes a row for **every** sample. A sample the model can't handle gets NaN
  and is counted, not silently dropped.
- **truth.py**: writes the truth CSV for scored samples only. Its `truth_frame()` is the
  **single truth function** that `score`, `submission` and `codabench/build_bundle.py`
  all import, so they can't diverge.
- **score.py**: metrics per target, overall and per group, plus coverage, written to
  `metrics.json` and `METRICS.md` and plotted. Reject NaN/inf predictions for scored
  samples rather than skipping them. Adapt the metric functions from `scripts/metrics.py`
  only when they fit the motif (SKILL.md element C).
- **report.py**: collects every `metrics.json` into `LEADERBOARD.md`. Has an
  `AUXILIARY = {...}` set whose rows render in italics with "(auxiliary)". Adapt
  `assets/repo/report.py`.
- **submission.py**: packages each model's predictions as an upload-ready Codabench zip,
  with exactly the scored samples, at the zip root, applying the same checks as the
  scoring program. Refuses (exit 1, no zip) on incomplete or non-finite predictions.
  Adapt `assets/repo/submission.py`.

### scripts/

- **fetch_data.py**: downloads the dataset and **records the exact revision** (HF commit
  hash, DOI version, file checksums) into the data directory, so a run's dataset version
  is recoverable.
- **fetch_weights.py**: downloads every file in `weights/MANIFEST.json`, verifies sha256,
  copies the small derived artifacts, and exits non-zero on any mismatch. Supports
  `--from-local DIR` for air-gapped machines. Adapt `assets/repo/fetch_weights.py`.
- **score_all.sh**: truth → score every `predictions_*.csv` → leaderboard → submission
  zips. Runs unchanged on a laptop and as the last Slurm job. Adapt
  `assets/repo/score_all.sh`.

### <hpc>/ *(optional)*

Generated from `assets/hpc/slurm/` and tuned per machine. See `references/hpc.md`.

### codabench/ *(optional)*

`bundle_src/` (hand-written, versioned) plus `build_bundle.py`, which generates the
hidden truth, scored-ID lists, `solution/`, `sample_submission.zip` and a weak-baseline
zip from the **same truth function** as the benchmark. `build/` is git-ignored. See
`references/codabench.md` § "Building the bundle from the benchmark".

### tests/

- **test_score.py**: metric edge cases (ε handling at all-zero, zero-variance R² → NaN,
  sign convention of any signed error, NaN predictions rejected, coverage counts, group
  assignment).
- **test_pipeline.py**: the **golden-output test** (pattern in
  `assets/repo/tests/test_pipeline.py`):
  - featurize the fixture samples, run each reference model, and compare against
    `fixtures/golden_<split>_<model>.csv` recorded from the validated run;
  - skips cleanly when the weights aren't present;
  - `<P>_TEST_DEVICE=cuda` runs it on a GPU and also checks GPU vs CPU agreement.

  Run it on every new machine **before** submitting jobs. It's the portable form of the
  per-sample verification in docs/VALIDATION.md.
- **test_features_equivalence.py** *(optional)*: bit-equivalence of vendored
  preprocessing vs the upstream code, given a checkout path in an env var; skipped
  otherwise.
- **test_submission.py**: the zip has exactly the scored IDs in order, and incomplete
  predictions produce no zip and a non-zero exit.
- **fixtures/**: a few dozen **real** samples per split and per subset, including edge
  cases (missing ground truth, the subset with the ID fallback, every exemplar group),
  plus the golden CSVs.

## When the optional pieces apply

| Piece | Include when |
|---|---|
| `features.py` + `test_features_equivalence.py` | a reference model depends on upstream preprocessing you vendor |
| `stats.py`, `weights/<stats>.json` | checkpoints need normalization stats/caps that aren't stored in them |
| `train.py` + training jobs | the benchmark evaluates or reproduces training (next section) |
| `<hpc>/`, `docs/<MACHINE>.md` | the full run needs a cluster, or the user names target machines |
| `codabench/` | the user wants a Codabench competition |
| multiple `requirements*.txt` | reference models need conflicting stacks |
| auxiliary column/rows | comparison models that aren't reference solutions are run |

## Score-only vs includes training

Ask; don't assume (SKILL.md element D). The answer shapes the repo:

- **Score-only** (axess's choice, made by its user on 2026-09-29):
  - no `train.py`;
  - weights come from `weights/MANIFEST.json`;
  - derived preprocessing artifacts are shipped files;
  - training code is linked upstream for provenance;
  - the rubric's "code complete" evidence says the benchmark is score-only by design.
- **Includes training**:
  - generate `src/<pkg>/train.py`, with the same `--split`/`--cache` conventions, writing
    checkpoints plus their derived artifacts to `<P>_WEIGHTS`;
  - add training Slurm jobs, which are GPU-heavy and possibly multi-node;
  - add a seed policy;
  - add a training validation section to docs/VALIDATION.md: does retraining reproduce
    the reference numbers within a stated tolerance, over how many seeds?
  - `MANIFEST.json` still records the reference checkpoints, so scoring doesn't require
    retraining.

Either way, `predict → score_all.sh` and the file conventions are identical, so scoring
and submissions don't depend on the choice.

## Conventions

- **Auxiliary vs reference models.** A comparison model that isn't a reference solution
  is still run and scored, but marked auxiliary:
  - italic "(auxiliary)" rows in `LEADERBOARD.md` (`report.AUXILIARY`);
  - its own column in `reference_solution/README.md`, with a "why auxiliary" paragraph;
  - listed separately in `MANIFEST.json` and the README results table.

  axess: rule4ml's GIN GNN, which is a different architecture from the paper's GATv2 GNN.
- **Coverage everywhere.** Every `metrics.json` and `METRICS.md` carries n_truth,
  n_scored, n_truth_without_prediction, n_predictions_without_truth.
- **Citations.** `CITATION.cff`'s top level describes **the software**: its title, its
  authors, its own code `license`, and `repository-code`. The paper goes in
  `preferred-citation`. Don't put the paper's title or the **dataset's** license (axess:
  CC-BY-NC-4.0 data, Apache-2.0 code) at the top level.
  - Prefer the published DOI over the preprint once one exists. Fetch its metadata from
    `https://doi.org/<doi>` with `Accept: application/x-bibtex` (or
    `application/vnd.citationstyles.csl+json`) rather than typing it in.
  - Validate with `cffconvert --validate`.
  - When citing sections and equations, check the numbering against the published
    version, not the preprint.
