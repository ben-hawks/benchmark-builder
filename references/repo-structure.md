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
benchmark. The small reusable snippets in `assets/repo/`, `assets/hpc/` and
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

**Generic structure, benchmark-specific content.** The layout, the pipeline contract and
the conventions below apply to every benchmark. What goes *inside* the files doesn't, and
must be decided per benchmark while running the skill:
- data formats and how to read them;
- how missing ground truth is handled;
- the output format and metrics;
- preprocessing, caching and post-processing;
- software stacks and the workarounds they need;
- tolerances and resource sizes.

axess-benchmark's answers appear in this file only as labelled examples ("axess: ...").
When a benchmark needs a fix or a workaround, put it in that benchmark's own code and
document it in its `docs/VALIDATION.md` or `docs/<MACHINE>.md`, with the evidence for it.
Never fold it back into the skill's templates as a default.

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
├── requirements*.txt          one per environment that must stay separate (only if stacks conflict)
├── .gitattributes             `* text=auto eol=lf` plus binary types
├── data/SCHEMA.md             per-field schema: which field is ground truth, which fields are NOT valid inputs
├── data/croissant.json        (optional) Croissant metadata, generated or validated with the genesis croissant-validator skill
├── docs/
│   ├── VALIDATION.md          how the reference solutions were verified (numbers, dates, hardware)
│   └── <MACHINE>.md           (optional) running on a target cluster: paths, setup, jobs, troubleshooting
├── reference_solution/README.md   per-model table (documentation only, no code)
├── reference_results/         committed outputs of a full run
│   ├── LEADERBOARD.md
│   └── <split>/<model>/{METRICS.md, metrics.json, <plot>.png}
├── weights/
│   ├── MANIFEST.json          per file: URL, sha256, bytes, provenance
│   └── <artifacts>            (optional) small files the weights need but don't contain
├── src/<pkg>/
│   ├── data.py                load the dataset, sample_id rule, output columns, ground-truth extraction
│   ├── cache.py               (optional) preprocess once into a cache, when preprocessing is expensive
│   ├── features.py            (optional) vendored upstream preprocessing, kept bit-identical
│   ├── stats.py               (optional) one-time rebuild of preprocessing artifacts (provenance only)
│   ├── models/<model>.py      vendored or wrapped model definitions + loaders
│   ├── train.py               (optional) only when the benchmark includes training
│   ├── predict.py             CLI: model × split → predictions file (all samples)
│   ├── truth.py               CLI: split → truth file (scored samples only); the single truth function
│   ├── score.py               CLI: metrics overall + per group → METRICS.md, metrics.json, plots
│   ├── report.py              all metrics.json → LEADERBOARD.md (auxiliary models marked)
│   └── submission.py          predictions → upload-ready Codabench zip per model
├── scripts/
│   ├── fetch_data.py          download + record the exact dataset revision
│   ├── fetch_weights.py       download + verify sha256 from weights/MANIFEST.json
│   └── score_all.sh           truth → score every predictions_*.csv → leaderboard → submission zips
├── <hpc>/                     (optional) env.sh, stack.sh, setup.sh, submit.sh, jobs/*.sbatch|*.pbs, profiles/
├── codabench/                 (optional)
│   ├── README.md              mode, phases, ranking, validation record, pre-upload checklist
│   ├── build_bundle.py        bundle_src + generated truth/solution/ids → build/competition_bundle.zip
│   └── bundle_src/            competition.yaml, logo.png, pages/, scoring_program/ (vendored metrics), starting_kit/
└── tests/
    ├── test_score.py          edge cases of this benchmark's metrics
    ├── test_pipeline.py       golden predictions on real fixture samples (CPU, and each accelerator via <P>_TEST_DEVICE)
    ├── test_features_equivalence.py   (optional) bit-equivalence vs upstream preprocessing
    ├── test_submission.py     packaging + refusal of incomplete predictions
    └── fixtures/              a few dozen real samples per split/subset + golden files
```

The old layout this replaces (`reference_solution/` holding code, a standalone
`metrics/score.py`, one environment file) broke down in practice:

- Code in `reference_solution/` mixed documentation with code that several commands
  share, such as data loading, featurization and scoring.
- A standalone scorer couldn't do truth extraction, per-group breakdowns, a leaderboard
  and submission packaging off the same loader and sample IDs.
- One environment file can't hold reference models with conflicting stacks (axess: a
  TensorFlow baseline next to a site PyTorch module).

## The pipeline contract

Every benchmark's run is the same steps, with the same file conventions. Steps in
brackets exist only when the benchmark needs them:

```
fetch_data → [cache] → [train] → predict (per model, per split) → score_all.sh
                                    ↑                              (truth, score, leaderboard, submissions)
              [fetch_weights (sha256-checked)] or weights from train
```

Add a `cache` step only when preprocessing is expensive enough to do once; its format is
the benchmark's choice. Every CLI takes `--split` plus a data or cache directory, so the
storage format stays inside the package.

| File | Written by | Contents |
|---|---|---|
| `<results>/<split>/predictions_<model>.<ext>` | `predict` (or a participant) | the model's outputs for **every** sample of the split, keyed by `sample_id` |
| `<results>/<split>/truth.<ext>` | `truth` | the ground truth for the **scored samples only**, plus any grouping column(s) |
| `<results>/<split>/<model>/metrics.json`, `METRICS.md`, plots | `score` | metrics overall and per group, plus a coverage block |
| `<results>/LEADERBOARD.md` | `report` | one table per split, every model, auxiliary rows marked |
| `<results>/codabench/<model>_submission.zip` | `submission` | upload-ready Codabench results submission |

For a per-sample task (regression, classification, detection, ...), the default
prediction file is a CSV with `sample_id` plus one column per output (`data.OUTPUT_COLUMNS`);
the snippets assume this. Tasks whose outputs aren't per-sample (generated samples, a
control policy, a ranking) define their own prediction artifact. They keep the same rules:
one file or directory per model and split, everything a scorer needs, and nothing
hand-edited.

A participant's model plugs in by writing its predictions for each split and re-running
`score_all.sh`; nothing else changes. Say exactly this in the README and in
`SUBMISSION.md`.

Paths come from environment variables with a benchmark-specific prefix (axess: `WA_`; the
snippets use `BENCH_`, so rename them): `<P>_DATA`, `<P>_CACHE`, `<P>_WEIGHTS`,
`<P>_RESULTS`, `<P>_SPLITS`. The same commands then work on a laptop and in batch jobs (Slurm or PBS).

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
  write their predictions file(s) and run `score_all.sh`, which also produces the
  Codabench zip.
- **CITATION.cff**: shape in `assets/repo/CITATION.cff`, rules in "Citations" below.
- **rubric.yaml / SCORE_REPORT.md**: from `assets/rubric_template.yaml`. Keep its `notes:`
  block dated and current (see SKILL.md § Iterate).
- **pyproject.toml**: an installable package (`src/` layout) with the core dependencies
  scoring needs, and **optional extras per model family**, so a user installs only what
  the models they run need (axess: `torch`, `mlp`, `fetch`, `test`).
- **requirements*.txt**: one per environment that has to stay separate, and only as many
  as the reference models' stacks actually require. Pin the versions the reference run
  used. (axess needed two: a PyTorch stack, and TensorFlow plus rule4ml, which brings its
  own torch.)
- **.gitattributes**: `assets/repo/.gitattributes`. Shell and sbatch files authored on
  Windows otherwise check out with CRLF and fail on the cluster with `$'\r': command not
  found`.

### data/SCHEMA.md

Every field of a sample, with its type and meaning. State explicitly:

- which field is the ground truth;
- which fields are **not valid model inputs**, because they're labels or are derived from
  them. axess's dataset carries `hls_resource_report` next to the ground truth
  `resource_report`, and a model fed one to predict the other would be cheating;
- the `sample_id` rule and any fallbacks (axess: `meta_data.uuid`, but the `2_20` subset
  only has `meta_data.model_id`). The rule must be unique per split, and the loader
  enforces it;
- how missing or invalid ground truth is represented, and what the benchmark does with
  those samples (see `data.py` below).

### docs/VALIDATION.md

How the reference solutions were verified, with actual numbers, dates, hardware and
software versions. This is what turns "we ran it" into evidence. Sections, as applicable:

1. Preprocessing equivalence with upstream, if preprocessing is vendored.
2. Rebuilt derived artifacts vs the shipped originals, if any were rebuilt.
3. Per-sample agreement with upstream predictions when those exist (axess: "max
   |ours − theirs| / (|theirs| + 1) = 2.8e-4 over 92,933 samples").
4. Reproduction of published table cells, and which metric variant reproduces them
   (SKILL.md element C).
5. The training-label audit: which label each reference model was trained on, proven
   on data (SKILL.md element D).
6. Gaps found in the data or preprocessing, and how this benchmark handles them.
7. Runs on each target machine: job IDs, exit codes, and agreement with
   `reference_results/`.
8. Independent metric recomputation: the reference model's metrics recomputed with a
   second implementation (the genesis `uq-metrics-evaluator` skill for standard
   regression/classification metrics), and any disagreement explained
   (`references/metrics-and-uq.md`).
9. Tools used: every external skill or tool that produced or checked something here
   (e.g. `datacard-generator`, `croissant-validator`, `uq-metrics-evaluator`, the
   lm-eval-harness skills), with its commit, so the checks can be re-run.

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
- output post-processing, if any (e.g. inverse transforms, clamps; axess: a cap at the
  training maximum);
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
- **Small derived artifacts** the checkpoints need but don't contain (e.g. normalization
  statistics, vocabularies, thresholds) go here as versioned files, if there are any.
  `scripts/fetch_weights.py` copies them next to the downloaded checkpoints.

### src/<pkg>/

- **data.py**: dataset loading, the split list, the output columns
  (`OUTPUT_COLUMNS`, used by every prediction and truth file), `sample_id()`, the grouping
  used for per-group metrics, and one ground-truth function per truth definition.
  Decide each of these per benchmark, from its data:
  - **How to read the data.** Use whatever the format and size require. If files don't fit
    in memory, stream them (axess streams 1.9 GB JSON arrays with `ijson`).
  - **Missing or invalid ground truth.** Decide with the user whether such samples are
    excluded, imputed, or scored as failures, and document the choice in `data/SCHEMA.md`.
    (axess excludes them.) Whatever the choice, report coverage (n_truth, n_scored,
    n_truth_without_prediction, n_predictions_without_truth) everywhere metrics are
    reported.
  - **Training filter vs scoring filter.** If anything reproduces upstream training (e.g.
    rebuilding normalization statistics), check whether upstream selected training
    samples differently from the benchmark's scoring filter. If it did, keep both as
    separate functions. (axess: the upstream converter kept samples with a missing latency
    report, 433,676 vs 433,674, which changes the statistics.)
- **cache.py** *(optional)*: only when preprocessing is expensive enough to do once.
  The format and the parallelism are the benchmark's choice (axess: one `.npz` per split,
  built with `multiprocessing.Pool.imap`). Two rules apply whatever the format:
  - assert `sample_id` uniqueness when building;
  - make the reader tolerant of caches written by earlier versions of the code, so a
    rerun doesn't fail on old files (axess: a column added later broke loading earlier
    caches).
- **features.py** *(optional)*: when a reference model depends on upstream preprocessing,
  vendor it **verbatim**, including its quirks, with a header naming the upstream file
  and commit. Any fix this benchmark needs (axess: a fallback for one exemplar
  architecture's missing precision values) must be a separate, switchable step, so the
  equivalence test can check the unmodified path.
- **stats.py** *(optional)*: rebuilds shipped derived artifacts from the training split,
  for provenance only. The pipeline reads the shipped file.
- **models/<model>.py**: vendored model class, loaded with the framework's strict
  weight matching so a wrong architecture fails loudly (e.g. PyTorch `strict=True`), or a
  thin wrapper around a pip-installed package. Include any post-processing that's part of
  the published inference procedure.
- **train.py** *(optional)*: see "Score-only vs includes training".
- **predict.py**: `--model M --split S` (plus a data or cache directory)
  `--out predictions_M.<ext>`, plus `--device`. Writes a prediction for **every** sample.
  A sample the model can't handle is marked missing and counted, not silently dropped.
- **truth.py**: writes the truth file for scored samples only. Its `truth_frame(cache_dir,
  split)` and `scored_ids(cache_dir, split)` are the **single truth function** that
  `score`, `submission` and `codabench/build_bundle.py` all import, so they can't diverge.
- **score.py**: this benchmark's metrics, overall and per group, plus coverage, written to
  `metrics.json` and `METRICS.md`, with plots if the benchmark defines any. Reject invalid
  predictions for scored samples rather than skipping them. Reuse functions from
  `scripts/metrics.py` only when they fit the motif (SKILL.md element C).
- **report.py**: collects every `metrics.json` into `LEADERBOARD.md`. Has an
  `AUXILIARY = {...}` set whose rows render in italics with "(auxiliary)". Adapt
  `assets/repo/report.py`.
- **submission.py**: packages each model's predictions as an upload-ready Codabench zip,
  with exactly the scored samples, at the zip root, applying the same checks as the
  scoring program. Refuses (exit 1, no zip) on incomplete or invalid predictions; what
  counts as invalid depends on the task. Adapt `assets/repo/submission.py`.

### scripts/

- **fetch_data.py**: downloads the dataset and **records the exact revision** (HF commit
  hash, DOI version, file checksums) into the data directory, so a run's dataset version
  is recoverable.
- **fetch_weights.py**: downloads every file in `weights/MANIFEST.json`, verifies sha256,
  copies the small derived artifacts, and exits non-zero on any mismatch. Supports
  `--from-local DIR` for air-gapped machines. Adapt `assets/repo/fetch_weights.py`.
- **score_all.sh**: truth → score every `predictions_*.csv` → leaderboard → submission
  zips. Runs unchanged on a laptop and as the last batch job. Adapt
  `assets/repo/score_all.sh`.

### <hpc>/ *(optional)*

Generated from `assets/hpc/common/` plus `assets/hpc/slurm/` or `assets/hpc/pbs/`: a
machine profile per cluster, pre-filled from the genesis site skill, plus `stack.sh` for
the benchmark's own software-stack settings and fixes. See `references/hpc.md`.

### codabench/ *(optional)*

`bundle_src/` (hand-written, versioned) plus `build_bundle.py`, which generates the
hidden truth, scored-ID lists, `solution/`, `sample_submission.zip`, and a weak-baseline
zip chosen for the task, all from the **same truth function** as the benchmark. `build/` is git-ignored. See
`references/codabench.md` § "Building the bundle from the benchmark".

### tests/

- **test_score.py**: edge cases of this benchmark's own metrics, plus coverage counts,
  group assignment, and rejection of invalid predictions. (axess: SMAPE's ε at all-zero,
  R² → NaN at zero variance, the sign convention of a signed error.)
- **test_pipeline.py**: the **golden-output test** (pattern in
  `assets/repo/tests/test_pipeline.py`):
  - preprocess the fixture samples if the benchmark has a cache step, run each reference
    model, and compare against golden outputs recorded from the validated run;
  - use tolerances measured for this benchmark across the hardware it runs on, not
    copied from another benchmark;
  - skips cleanly when the weights aren't present;
  - `<P>_TEST_DEVICE=<device>` runs it on an accelerator, which also checks
    accelerator vs CPU agreement.

  Run it on every new machine **before** submitting jobs. It's the portable form of the
  per-sample verification in docs/VALIDATION.md.
- **test_features_equivalence.py** *(optional)*: bit-equivalence of vendored
  preprocessing vs the upstream code, given a checkout path in an env var; skipped
  otherwise.
- **test_submission.py**: the zip has exactly the scored IDs in order, and incomplete
  predictions produce no zip and a non-zero exit.
- **fixtures/**: a few dozen **real** samples per split and per subset, covering the edge
  cases this benchmark actually has (axess: samples without ground truth, the subset with
  the ID fallback, every exemplar group), plus the golden files.

## When the optional pieces apply

| Piece | Include when |
|---|---|
| `features.py` + `test_features_equivalence.py` | a reference model depends on upstream preprocessing you vendor |
| `cache.py` + a featurize job | preprocessing is expensive enough to do once |
| `stats.py`, `weights/<artifacts>` | checkpoints need derived artifacts that aren't stored in them |
| `train.py` + training jobs | the benchmark evaluates or reproduces training (next section) |
| `<hpc>/`, `docs/<MACHINE>.md` | the full run needs a cluster, or the user names target machines |
| `codabench/` | the user wants a Codabench competition |
| `data/croissant.json` | the dataset has no Croissant metadata where it's hosted (Hugging Face serves its own) |
| `tasks/<task>/` | an LLM benchmark (`references/llm-benchmarks.md`) |
| multiple `requirements*.txt` | reference models need conflicting stacks |
| `<hpc>/stack.sh` hooks | the benchmark's stack needs environment settings or fixes on a machine (documented in `docs/<MACHINE>.md`) |
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
  - generate `src/<pkg>/train.py`, with the same `--split`/directory conventions, writing
    checkpoints plus their derived artifacts to `<P>_WEIGHTS`;
  - add training batch jobs, sized from this benchmark's training cost (possibly
    multi-node);
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
