# Codabench Competition Bundles

Source: [Codabench docs](https://docs.codabench.org/latest/Organizers/Benchmark_Creation/Competition-Bundle-Structure/)
(Bundle Structure, YAML Structure, and Leaderboard Functionality pages) plus the
**real, executable** `wheat_seeds` example bundle from Codabench's own
[competition-examples](https://github.com/codalab/competition-examples/tree/master/codabench/wheat_seeds)
repo, downloaded and unzipped to verify every path and file convention below against
actual working code — the docs pages are thin on some details (especially the exact
`/app/...` directory contracts), so where they're silent, this file defers to what the
real example bundle actually does.

This is the target format for turning a standalone benchmark (built per
`references/ontology.md`) into something a participant can browse, understand, and
submit to on codabench.org — a **separate, later step**, not a replacement for the
standalone benchmark. Read this file in full before generating any Codabench bundle
files. Two complete, runnable, self-tested worked examples to pattern-match against:

- `assets/codabench/example_bundle/`, a code submission;
- `assets/codabench/results_example/`, a results submission built from versioned
  `bundle_src/` by `build_bundle.py`, the way axess-benchmark does it (see "Building the
  bundle from the benchmark" below).

The real-world reference is axess-benchmark's `codabench/` directory
(`references/wa-hls4ml-example.md`).

## The big design decision: code submission vs. results submission

Before generating anything, this must be decided — it changes the bundle's shape
entirely, so ask the user rather than assuming:

- **Code submission**: the participant submits *code* (e.g. a model implementing a
  fixed `fit`/`predict` interface). An **ingestion program** (organizer-provided) runs
  that code against the task's input data to produce predictions, which are then
  scored. This is the right choice when part of what's being evaluated is the
  method/training procedure itself, or when re-running training per submission matters
  (closer to what a "Reference Solution" in the ontology usually looks like).
- **Results submission**: the participant runs their model *themselves*, offline, and
  uploads only the resulting predictions file. No ingestion program is needed — the
  scoring program reads the uploaded predictions directly. Simpler, avoids running
  arbitrary participant code on the compute worker, but can't verify how the
  predictions were produced.

A competition can offer both (an `ingestion_only_during_scoring`-style setup or
per-phase differences exist for advanced cases), but pick one as the default and only
reach for more complexity if the user specifically needs it.

**Derive the recommendation from the benchmark's scope and data visibility, then
confirm it with the user:**

| Benchmark | Natural fit | Why |
|---|---|---|
| Score-only (pretrained or offline models), ground truth public | results submission | nothing to hide, and a code submission would only add compute workers and an image to maintain. axess chose this: code submission couldn't hide the answers either, and its models need GPU workers plus a custom image (PyTorch Geometric) |
| Evaluates training or a method, or a constraint must be measured on the platform (latency, cost) | code submission | the thing being evaluated has to run under controlled conditions |
| Hidden test inputs (not just hidden labels) | code submission | participants must not see the inputs |

Write the scoring program so it works for either mode. It does if a code submission's
ingestion program writes the same prediction files a results submission would upload.

## Building the bundle from the benchmark

Pattern from axess-benchmark; a runnable miniature is
`assets/codabench/results_example/`, and the template is
`assets/codabench/build_bundle.py`.

```
codabench/
├── README.md              mode, phases, ranking, validation record, pre-upload checklist
├── build_bundle.py        bundle_src/ + generated files → build/
├── bundle_src/            hand-written, versioned
│   ├── competition.yaml, logo.png, pages/
│   ├── scoring_program/   scoring.py, vendored metrics, metadata.yaml
│   └── starting_kit/      README.md (+ helper scripts)
└── build/                 generated, git-ignored
    ├── bundle/            validate this
    ├── competition_bundle.zip   upload this
    └── extra/baseline_submission.zip   weak baseline for the discrimination check
```

- **One truth function.** `build_bundle.py` imports the benchmark package's truth
  function (`truth.truth_frame`), the same one `score.py` and `submission.py` use. From
  it, it generates:
  - the hidden `reference_data/truth_<split>.csv`;
  - `starting_kit/<split>_sample_ids.csv`;
  - `solution/` (the reference model's predictions restricted to scored samples);
  - `starting_kit/sample_submission.zip`;
  - a weak baseline chosen for the task, implemented in `weak_baseline()` (e.g. the
    training mean for regression, which axess used; the majority class for
    classification; a random policy for control).

  Hand-copying any of these into the bundle is how a bundle drifts from its benchmark.
- **The benchmark pipeline emits submissions.** `src/<pkg>/submission.py`, the last step
  of `scripts/score_all.sh`, writes `<results>/codabench/<model>_submission.zip` for every
  model (`assets/repo/submission.py`). Each zip has exactly the scored samples, sits at
  the zip root, and gets the scoring program's own checks. A model with incomplete or
  invalid predictions gets no zip and a non-zero exit. Validate these zips against the
  built bundle; their Codabench scores must equal the benchmark's `metrics.json`.
- **Validate `build/bundle/`**, not `bundle_src/`, since the generated directories only
  exist in the build.

## Scoring program contract

What every generated `scoring.py` must do. axess's
`codabench/bundle_src/scoring_program/scoring.py` and
`assets/codabench/results_example/bundle_src/scoring_program/scoring.py` both implement
it for per-sample numeric predictions. Translate each rule to this benchmark's output
type:

- **Declare the submission contract** as a module-level constant the validator can read
  without importing the program:
  ```python
  SUBMISSION_FILES = ["predictions_test.csv", "predictions_holdout.csv"]
  ```
- **Build each expected path as a literal** `os.path.join(prediction_dir, "<name>")`. The
  validator's regex fallback only detects that form.
- **Tolerate one wrapping folder** (search `prediction_dir` for the expected name if it
  isn't at the root), but document root-level files as the format.
- **Fail with a message naming the problem**, on stderr with exit 1, for each of these:
  - a missing file or column;
  - a duplicate `sample_id`;
  - a missing scored sample (say how many and give examples);
  - a value that's invalid for this task (e.g. non-numeric or NaN/inf for a numeric
    output, a label outside the class set for classification).
- **Ignore extra rows** if predictions may legitimately cover samples that aren't scored
  (axess: test samples without ground truth). Otherwise, decide whether extra rows are an
  error.
- **Write NaN as `null`** in `scores.json` (JSON has no NaN). Print the full per-group
  tables to stdout for the detailed-results panel.

## Ranking and discrimination

- **Rank on a bounded metric of the primary split.** Leaderboard column `index: 0` is
  the ranking key.
  - Don't rank on a metric that's unbounded below on some split (axess: R² on its
    out-of-distribution exemplar split, where the training-mean baseline scored −2651).
  - Show such metrics as extra columns, and break ties with a second primary-split
    metric.
- **Discrimination check, every time the bundle is built:** score the reference solution
  and the task's weak baseline, and report both (axess: test mean R² 0.809 vs 0.000,
  SMAPE 10.3% vs 114%). If they don't clearly separate, the metric or the bundle is
  wrong.

## Bundle directory structure

```
competition_bundle.zip
├── competition.yaml              (required — everything else is referenced from here)
├── <logo>.png/.jpg               (referenced by competition.yaml's `image`)
├── pages/
│   ├── terms.md                  (referenced by `terms` — required)
│   ├── overview.md                )
│   ├── evaluation.md              )  referenced by `pages` — optional but expected
│   └── data.md                    )
├── <phase_name>/
│   ├── input_data/                 (code submission only — what the ingestion program reads)
│   └── reference_data/             (ground truth — scoring program only ever sees this)
├── public_data/                  (optional — mirrors dev-phase data for participants to explore locally)
├── ingestion_program/            (code submission only)
│   ├── ingestion.py
│   └── metadata.yaml
├── scoring_program/              (always required)
│   ├── scoring.py
│   ├── <vendored helper modules>   -- see "Vendor shared code" below
│   └── metadata.yaml
├── solution/                     (organizer's reference implementation --
│   └── model.py                     doubles as the participant-facing example submission)
└── starting_kit/                 (what a participant downloads to get started)
    ├── README.md
    ├── model.py                  (a naive baseline participants build on)
    └── sample_submission.zip     (a zipped, ready-to-upload example -- usually solution/ re-zipped)
```

"Files can be under a directory, they just have to be referenced by their full path in
`competition.yaml`" — the layout above is convention (and what the real example uses),
not a hard requirement, but stick to it unless there's a specific reason not to.

## `competition.yaml` schema

### Required top-level keys
- **`version`**: must be `2`.
- **`title`**: competition name.
- **`image`**: logo file path, relative to `competition.yaml`.
- **`terms`**: path to a markdown/HTML file with participation terms.

### Optional top-level keys (with defaults where noted)
`description`, `registration_auto_approve` (default False), `docker_image` (default
`codalab/codalab-legacy:py3` — **check this default has what the reference solution
actually needs**; the real example overrides it to `codalab/codalab-legacy:py312`
purely for a newer Python), `make_programs_available`, `make_input_data_available`,
`queue`, `enable_detailed_results`, `show_detailed_results_in_submission_panel`
(default True), `show_detailed_results_in_leaderboard` (default True),
`contact_email`, `reward`, `auto_run_submissions` (default True),
`can_participants_make_submissions_public` (default True), `forum_enabled` (default
True).

### `pages` (optional but expected)
```yaml
pages:
  - title: Welcome
    file: pages/overview.md
```
Each entry needs `title` and `file`.

### `tasks` (required — at least one)
Either define a new task or reference an existing one by `key` (a database task UUID,
which ignores every other field). To define a new task:
- **Required**: `index`, `name`, `scoring_program` (path to a dir or `.zip`).
- **Optional**: `description`, `input_data` (code submission only), `reference_data`,
  `ingestion_program` (code submission only), `ingestion_only_during_scoring`.

### `phases` (required — at least one)
- **Required**: `name`, `start` (datetime), `tasks` (array of task indices). `end` may
  be omitted only for the final phase (it just never closes).
- **Optional**: `index`, `max_submissions`, `max_submissions_per_day`,
  `auto_migrate_to_this_phase`, `execution_time_limit` (seconds, default 600),
  `hide_output`, `hide_prediction_output`, `hide_score_output`, `starting_kit`
  (folder path), `public_data` (folder path), `accepts_only_result_submissions`.

The real example uses exactly two phases — **Development** (many submissions allowed,
tune freely) and **Final/Testing** (usually `max_submissions: 1`, fresh unseen data) —
which maps directly onto this skill's existing Dataset guidance about a held-out
generalization set distinct from the main test set. Reuse that two-phase pattern by
default rather than inventing a different one.

### `solutions` (optional)
- **Required**: `index`, `tasks` (array of task indices it applies to), `path`.

### `leaderboards` (required — at least one)
- **Required**: `title`, `key` (used internally, e.g. `main`), `columns`.
- **Optional**: `submission_rule` (`Add`, `Add_And_Delete`,
  `Add_And_Delete_Multiple`, `Force_Last`, `Force_Latest_Multiple`, `Force_Best`),
  `hidden`.

Each **column**:
- **Required**: `title`, `key` (**must exactly match a key in the scoring program's
  `scores.json` output** — this is the single most common place a bundle breaks),
  `index` (also sets ranking priority — index 0 is the primary sort key, ties broken
  left-to-right by increasing index, then by earliest submission time).
- **Optional**: `sorting` (`desc` = larger is better, `asc` = smaller is better),
  `computation` (`sum`/`avg`/`min`/`max`/`avg_rank`, applied over
  `computation_indexes`), `precision` (default 2 decimals), `hidden`.

### `fact_sheet` (optional)
Metadata questions asked at submission time (e.g. "which framework did you use?").
Each entry has `key`, `type` (`checkbox`/`text`/`select`), `title`, `selection`
(choices, or `""` for free text), `is_required`, `is_on_leaderboard` (all as strings
`"true"`/`"false"` per the real schema, not YAML booleans).

## Ingestion and scoring programs

Both are a directory containing the program's code plus a **`metadata.yaml`** with
exactly one key confirmed in every real example inspected:
```yaml
command: python3 ingestion.py    # or: python3 scoring.py
```
No other `metadata.yaml` keys were found in any of the three real bundle variants
checked (code submission, results submission, ingestion-during-scoring) — if a
generated bundle needs more (GPU access, extra env vars), verify against current
Codabench docs/support rather than assuming a key exists.

**Exact directory contract** (verified from real, executable `ingestion.py`/`scoring.py`
— the ground truth for this skill's own templates, which use the same paths):

Ingestion program (code submission only) sees, inside its container:
- `/app/input_data/` — the task's `input_data` (never the reference/ground truth)
- `/app/output/` — where it writes `prediction` and (optionally) `metadata.json`
  (e.g. `{"duration": ...}`, which the real example threads through to the leaderboard)
- `/app/program` — its own code (add to `sys.path`)
- `/app/ingested_program` — the participant's submitted code, extracted here (add to
  `sys.path`, then `from model import Model` or whatever the fixed interface is)

Scoring program sees, inside its container:
- `/app/input/ref` — the task's `reference_data` (ground truth)
- `/app/input/res` — the ingestion program's `/app/output/` from the previous stage
  (or, for a results-only submission, the participant's uploaded file directly)
- `/app/output/` — where it writes **`scores.json`**, keys matching leaderboard columns
- `/app/program` — its own code

**This skill's templates use an override, not the hardcoded path.** The real Codabench
examples hardcode `/app/...` directly, which only works inside the actual container —
making local testing without Docker impossible. This skill's generated
`ingestion.py`/`scoring.py` instead read the root from an environment variable:
```python
ROOT = os.environ.get("CODABENCH_ROOT", "/app")
```
and build every path under `ROOT`. Inside the real Codabench container the variable is
unset, so `ROOT` is `/app` and behavior is identical to the hardcoded original.
Locally, `scripts/validate_codabench_bundle.py` sets `CODABENCH_ROOT` to a temp
directory to dry-run the exact same code without touching the real filesystem root or
needing Docker. Keep this convention in every generated ingestion/scoring script —
don't hardcode `/app` the way the raw Codabench example does.

## Docker image: what's available, and when to build a custom one

Source for this section: Codabench's
[Docker Image docs](https://docs.codabench.org/latest/Organizers/Benchmark_Creation/Competition-docker-image/)
plus the actual base Dockerfiles from
[codalab/codalab-dockers](https://github.com/codalab/codalab-dockers/tree/master/Dockerfiles),
fetched and read directly rather than assumed — the docs page itself says nothing about
what's preinstalled, so treat the table below (built from the real Dockerfile contents)
as the source of truth over guessing.

### Ask first: does a stock base image already cover the reference solution's dependencies?

| `docker_image` value | Base | Preinstalled (confirmed from the real Dockerfile) | Notes |
|---|---|---|---|
| `codalab/codalab-legacy:py37` | Anaconda 3-2019.07 | theano, Cython, numpy, scipy, scikit-learn, pandas, pyyaml, imutils, tensorflow | Run scripts with `python3`, not `python` |
| `codalab/codalab-legacy:py39` | Anaconda 3-2022.05 | same list as py37 | Run scripts with `python3`, not `python` |
| `codalab/codalab-legacy:py312` (this skill's default — see `assets/codabench/example_bundle/competition.yaml`) | `python:3.12-slim-bookworm` | Cython, numpy 1.26, scipy, scikit-learn 1.5, pandas, pyyaml, imutils, numba, matplotlib, psutil | No R/Anaconda cruft; `python3` works (confirmed — this is the official Python image, not a from-scratch build) |
| `codalab/codalab-legacy:gpu` | `tensorflow/tensorflow:latest-gpu-py3` | TensorFlow + common libs | CPU images above have **no torch/tensorflow** except py37/py39's tensorflow — check the actual version pinned is compatible |
| `codalab/codalab-legacy:gpu310` | `nvidia/cuda:12.4.1-cudnn-runtime-ubuntu20.04`, Python 3.10 | numpy, scipy, scikit-learn, pandas, pyyaml, opencv-python, **torch 2.3.1**, **tensorflow 2.16.1**, tqdm, h5py, jupyter | The only stock image with PyTorch. Directly relevant if the reference solution is a GNN/Transformer-style model trained on GPU (see `references/wa-hls4ml-example.md`) |

If the reference solution's actual dependencies (check its real `requirements.txt`/
`environment.yml`, don't guess) are a subset of one of these rows, use that image and
stop — building a custom one is unnecessary extra maintenance. `wa-hls4ml`'s GNN/
Transformer models are PyTorch + PyTorch Geometric, trained on an A10/A100 GPU per the
paper — `gpu310` covers the PyTorch base but **not** PyTorch Geometric, which needs a
separate, torch-version-matched install; that's a concrete case where a custom image
is actually needed, not just a hypothetical.

**A GPU `docker_image` alone does not grant GPU execution.** The competition also needs
a GPU-capable compute worker attached to its `queue` (see "Organizers > Running
Benchmarks > Compute Worker Setup" in the Codabench docs) — that's the organizer's
infrastructure to set up separately, out of scope for this skill, but say so explicitly
rather than letting the user assume specifying `gpu310` is sufficient by itself.

### Building a custom image (when a stock one doesn't cover it)

Two methods; use the **Dockerfile method**, not the interactive `docker commit` one —
this skill's whole premise is reproducibility (`references/ontology.md`'s Documentation
and Reproducible Protocol element applies here too: an image nobody can rebuild from
source is exactly the kind of unreproducible artifact this skill exists to avoid).

1. Start from `assets/codabench/Dockerfile.template` (CPU) or
   `assets/codabench/Dockerfile.gpu.template` (GPU) — both are direct extensions of the
   real `Dockerfile-py312`/`Dockerfile-gpu310` shown above, not written from scratch.
   Add exactly the packages the reference solution's own dependency file lists; don't
   copy in unrelated packages "just in case." Save it into the bundle root as
   `Dockerfile` (or `Dockerfile.gpu`) so the validator finds it automatically.
2. **Build and test it in one step** — `scripts/validate_codabench_bundle.py`'s tier 4
   does the build for you when the bundle has a Dockerfile at its root, tags it under an
   obviously-local `benchmark-builder-local/<slug>:validate` namespace, and then runs the
   real ingestion/scoring programs inside it:
   ```bash
   python scripts/validate_codabench_bundle.py <bundle_dir> --submission <sample_submission.zip> --docker
   ```
   Everything here is local and reversible — build, pull, run, and optionally
   `--rm-built-image` to delete the image it built afterwards. Useful flags:
   `--dockerfile PATH` (non-standard location), `--no-build` (skip building, just
   use/pull `competition.yaml`'s `docker_image`), `--gpus` (pass `--gpus all`),
   `--timeout SECONDS` (defaults to the phase's own `execution_time_limit`, or
   600s if unset — raise this for a benchmark with real training cost; the toy
   example trains near-instantly, but a benchmark like Jet Classification needs
   minutes, not the tool's old hardcoded 120s default).
   The local build tag is deliberately *not* the published image name, so a test build
   can never be mistaken for — or accidentally pushed as — the real one. Tier 4 warns
   when it validated a locally-built image while `competition.yaml` declares a different
   `docker_image`, since Codabench will pull the declared one, not your local build.
   If the bundle has no Dockerfile, tier 4 just uses `docker_image`, pulling it if it
   isn't already present locally.
3. **Publishing the image is a public action — always get explicit user confirmation
   before running `docker push`, every time, not just once per project.** Pushing to
   DockerHub makes the image publicly pullable (unless the user has a private repo set
   up, which has its own cost/auth implications to flag). The validator deliberately
   never pushes; that step is manual and confirmed:
   ```bash
   docker login
   docker push <dockerhub-username>/<image-name>:<tag>
   ```
   (Tag the tested image for the real name first:
   `docker tag benchmark-builder-local/<slug>:validate <dockerhub-username>/<image-name>:<tag>`.)
4. Set `docker_image: <dockerhub-username>/<image-name>:<tag>` in `competition.yaml` to
   match exactly what was pushed, then re-run tier 4 with `--no-build` to confirm the
   *published* image (not just your local build) actually works.

Codabench's docs don't state whether private registries or auth-gated images are
supported at all — don't assume either way; if the user needs this, tell them to verify
against current Codabench docs/support rather than relying on this file.

## Vendor shared code into each program directory

`ingestion_program/` and `scoring_program/` are zipped and uploaded **independently** —
neither can import from this skill's `scripts/metrics.py` (or from each other, or from
anywhere outside its own directory) at runtime on Codabench's servers. If the scoring
program needs `r_squared`/`smape`/whatever, copy the specific functions it needs into a
small module inside `scoring_program/` itself (see
`assets/codabench/example_bundle/scoring_program/metrics.py` for exactly this — a
trimmed, self-contained copy, not a reference back to the skill). Same rule for any
other shared helper code.

## What a participant's submission zip must contain

This is **not a fixed format** — it's whatever the ingestion program (code submission)
or scoring program (results submission) actually reads, so it must be verified against
those specific files, not assumed:
- **Code submission**: whatever file(s) the ingestion program imports, at the
  **root of the zip** (no wrapping folder) — e.g. if `ingestion.py` does
  `from model import Model`, the zip must contain `model.py` at its root, defining a
  `Model` class with the methods the ingestion program calls on it.
- **Results submission**: whatever filename(s) the scoring program reads from
  `res` (its input directory) — e.g. if `scoring.py` does
  `np.genfromtxt(os.path.join(prediction_dir, 'prediction'))`, the zip must contain a
  file literally named `prediction` at its root.

`scripts/validate_codabench_bundle.py` checks this automatically. If the ingestion
(code) or scoring (results) program declares a module-level
`SUBMISSION_FILES = [...]`, it uses that: the file is parsed with `ast`, never imported.
Otherwise it falls back to a regex over the program source (`from X import Y` for code
submissions, a literal `os.path.join(<res/prediction dir>, "<name>")` for results). It
warns if the declared list misses a name the source appears to read. Declare the
constant in every program you generate; the regex is a fallback for bundles you didn't
write.

## Required vs. optional — what to ask the user for

**Must ask (no sensible default exists):**
- Competition title, and which submission mode (code vs. results) fits the benchmark.
- A logo image — if none exists yet, note the bundle is missing one rather than
  fabricating a placeholder graphic.
- Terms and conditions text. **Never author real legal/participation terms yourself.**
  Draft an obviously-marked placeholder (`assets/codabench/example_bundle` doesn't even
  attempt real terms; see its `pages/terms_and_conditions.md`), and tell the user
  explicitly that it must be reviewed or replaced before the competition goes live.
  Uploading with the placeholder is acceptable only to a dev instance, and only when the
  user confirms that's the purpose.
- Phase start dates (and end date, except optionally the final phase).
- Contact email, if they want one listed.

**Ask, but a sensible default exists — offer it and move on if they don't care:**
- Docker image (default `codalab/codalab-legacy:py3`) — check the reference solution's
  actual dependency file against the "Docker image" section above; if a stock image
  covers it, use that and move on, don't build anything. If not, that section has the
  base-image table, the Dockerfile templates to start from, and the build/test/publish
  steps (publishing is a confirm-every-time action, not a default-and-forget one).
- Max submissions / submissions per day / execution time limit.
- `registration_auto_approve`, `forum_enabled`, `can_participants_make_submissions_public`.

**Don't ask — derive from the standalone benchmark already built:**
- Task input/output shape and the dataset split → task `input_data`/`reference_data`.
- Metrics and their formulas → `scoring_program/scoring.py` + leaderboard columns.
- The reference solution → `solution/`.
- Benchmark card content (motivation, background, task description) → `pages/*.md`.

## Mapping the five ontology elements onto the bundle

| Ontology element | Codabench bundle location |
|---|---|
| Problem Specification and Constraints | `pages/overview.md`, `pages/data.md`; task `description` |
| Dataset (splits) | `dev_phase/`/`final_phase/` `input_data`+`reference_data`; `public_data/` |
| Performance Metric(s) | `scoring_program/scoring.py`; leaderboard `columns` |
| Reference Solution | `solution/` (also becomes the example submission) |
| Documentation and Reproducible Protocol | `pages/*.md`, `starting_kit/README.md`, `terms` |

## Validate before calling it done

Run `scripts/validate_codabench_bundle.py <bundle_dir> --submission <zip>` (see the
script's own docstring). It runs, in order: YAML/structure checks (paths exist, every
leaderboard column key is internally consistent, `metadata.yaml` files are present and
parse), a submission-contract check (does the submission zip actually contain what the
ingestion/scoring program expects), a local functional dry run (no Docker needed, for
bundles using the `CODABENCH_ROOT` convention above), and, if Docker is available and
requested, a fully faithful run inside the declared `docker_image`. Don't hand a bundle
to the user as finished without running at least the first two tiers.

### Tier 3 troubleshooting: host missing dependency

Tier 3 runs the programs with the **host's** Python. If the host lacks a package the
image provides (numpy, pandas, ...), the validator reports "tier 3 not verified: host
Python is missing dependency X" as a warning. That's a host problem, not a scoring
failure. Install the package on the host and re-run, or rely on tier 4.

If the missing module is one the program meant to vendor (e.g. `metrics`), it's an
error: add the file to the program directory.

### Tier 4 troubleshooting: "docker daemon not reachable"

"Not reachable" often means the client-to-engine bridge is broken while the engine is
fine. Seen with Rancher Desktop on Windows: the client reported "timed out dialing
Hyper-V socket" while dockerd inside the VM was healthy. Tier 4 for axess-benchmark
passed by running the validator from WSL Ubuntu against a working engine. Options:

- `--docker-host URL` (or `DOCKER_HOST`) points every docker call at a specific engine,
  e.g. `unix:///var/run/docker.sock` inside WSL, or `tcp://host:2375`;
- run the validator from WSL/Linux, where the engine's socket is local. The host Python
  there may lack numpy/pandas, which only affects tier 3 (see above);
- the validator only needs *some* engine that can pull and run the declared image.
