# Codabench competition bundles

How to package a finished benchmark as a [Codabench](https://www.codabench.org/)
competition, and the formats that depends on. Read this file in full before generating any
Codabench file. `SKILL.md` ("Package for Codabench") says when to start: only once the
standalone benchmark exists (dataset, metrics, reference solution, docs). This phase reuses
that work; it doesn't replace it.

Sources: the [Codabench docs](https://docs.codabench.org/latest/Organizers/Benchmark_Creation/Competition-Bundle-Structure/)
(Bundle Structure, YAML Structure, Leaderboard Functionality, Docker Image) plus the real,
executable `wheat_seeds` bundle from Codabench's
[competition-examples](https://github.com/codalab/competition-examples/tree/master/codabench/wheat_seeds)
and the base Dockerfiles in [codalab/codalab-dockers](https://github.com/codalab/codalab-dockers/tree/master/Dockerfiles).
These were downloaded and checked. Where the docs are silent (especially the exact
`/app/...` directory contracts), this file follows what the real bundle does.

Worked examples to pattern-match against:
- `assets/codabench/results_example/`: a **results submission** built the axess-benchmark
  way, with hand-written `bundle_src/` plus `build_bundle.py`;
- `assets/codabench/example_bundle/`: a **code submission**;
- axess-benchmark's own `codabench/` directory (`references/wa-hls4ml-example.md`), the
  real-world reference.

For an LLM benchmark, also read `references/llm-benchmarks.md` ("Codabench").

## Workflow

1. **Decide code submission vs results submission.** Derive a recommendation from the
   benchmark's scope and data visibility, then ask the user. It decides whether an
   `ingestion_program/` exists at all, so settle it first. See "Code submission vs results
   submission".
2. **Make the benchmark pipeline emit submissions.** The last step of `score_all.sh` writes
   an upload-ready zip per model (`assets/repo/submission.py`). See "Building the bundle
   from the benchmark".
3. **Build the bundle with `codabench/build_bundle.py`** (from
   `assets/codabench/build_bundle.py`), generating every data file from the benchmark's
   own truth function. Never hand-copy data into the bundle. Same section.
4. **Derive what's already known, and ask for only what only the user can supply.** Ask for
   the blockers (title, logo, terms, phase dates, mode) together in one pass. See "What to
   ask the user" and "Mapping the five ontology elements".
5. **Choose the ranking metric.** It must be bounded, on the primary split. See "Ranking
   and discrimination".
6. **Write the scoring program (and the ingestion program, for code submissions)** to the
   contract. See:
   - "Scoring program contract";
   - "Ingestion and scoring programs" (the `/app` layout and the `CODABENCH_ROOT`
     override);
   - "Vendor shared code into each program directory".
7. **Pick the Docker image.** A stock image covers most benchmarks. Build a custom one only
   if needed, and get **explicit confirmation before every `docker push`**. See "Docker
   image".
8. **Make the example submission** from the reference solution. See "Example submission".
9. **Validate**: the sample submission, every pipeline zip, and deliberately malformed
   zips. Tiers 1-3 always; tier 4 when Docker is available. See "Validation".
10. **Report real scores and the discrimination check, and record it all** in
    `codabench/README.md`: the mode, the phases, the ranking, a tier-by-tier result table
    with the date, the discrimination numbers, and a pre-upload checklist (terms, logo,
    image). See "Validation".

## Code submission vs results submission

- **Code submission.** The participant submits *code* (e.g. a model implementing a fixed
  `fit`/`predict` interface). An organizer-provided **ingestion program** runs it against
  the task's input data to produce predictions, which are then scored. Use it when the
  method or training procedure itself is what's evaluated.
- **Results submission.** The participant runs their model offline and uploads only the
  predictions. There's no ingestion program; the scoring program reads the upload
  directly. It's simpler and runs no participant code, but can't verify how the
  predictions were made.

| Benchmark | Natural fit | Why |
|---|---|---|
| Score-only (pretrained or offline models), ground truth public | results submission | nothing to hide, and a code submission would only add compute workers and an image to maintain. axess chose this: its models need GPU workers plus a custom image (PyTorch Geometric) |
| Evaluates training or a method, or a constraint must be measured on the platform (latency, cost) | code submission | what's evaluated has to run under controlled conditions |
| Hidden test inputs (not just hidden labels) | code submission | participants must not see the inputs |

Revisit element D's answer (score-only vs includes training) here. A competition can offer
both modes in advanced setups (e.g. per-phase differences), but pick one as the default.

Write the scoring program so it works for either mode. It does if a code submission's
ingestion program writes the same prediction files a results submission would upload.

## Building the bundle from the benchmark

The pattern comes from axess-benchmark. `assets/codabench/results_example/` is a runnable
miniature, and `assets/codabench/build_bundle.py` is the template.

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

- **One truth function.** `build_bundle.py` imports the benchmark package's truth function
  (`truth.truth_frame`), the same one `score.py` and `submission.py` use. From it, it
  generates:
  - the hidden `reference_data/truth_<split>.csv`;
  - `starting_kit/<split>_sample_ids.csv`;
  - `solution/` (the reference model's predictions restricted to scored samples);
  - `starting_kit/sample_submission.zip`;
  - a weak baseline chosen for the task, in `weak_baseline()`. For example: the training
    mean for regression (axess), the majority class for classification, a random policy
    for control.

  Hand-copying any of these into the bundle is how a bundle drifts from its benchmark.
- **The benchmark pipeline emits submissions.** `src/<pkg>/submission.py`, the last step of
  `scripts/score_all.sh`, writes `<results>/codabench/<model>_submission.zip` for every
  model. Each zip:
  - holds exactly the scored samples, at the zip root;
  - gets the scoring program's own checks;
  - isn't written for a model with incomplete or invalid predictions, which exits non-zero.

  A participant who ran the standalone benchmark already has their upload.
- **Validate `build/bundle/`**, not `bundle_src/`, since the generated directories only
  exist in the build.

## Scoring program contract

What every generated `scoring.py` must do. axess's
`codabench/bundle_src/scoring_program/scoring.py` and
`assets/codabench/results_example/bundle_src/scoring_program/scoring.py` both implement it
for per-sample numeric predictions. Translate each rule to this benchmark's output type:

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

- **Rank on a bounded metric of the primary split.** Leaderboard column `index: 0` is the
  ranking key.
  - Don't rank on a metric that's unbounded below on some split. axess: R² on its
    out-of-distribution exemplar split, where the training-mean baseline scored −2651.
  - Show such metrics as extra columns, and break ties with a second primary-split metric.
- **Discrimination check, every time the bundle is built.** Score the reference solution
  and the task's weak baseline, and report both. axess: test mean R² 0.809 vs 0.000, SMAPE
  10.3% vs 114%. If they don't clearly separate, the metric or the bundle is wrong.

## Bundle directory structure

```
competition_bundle.zip
├── competition.yaml              (required; everything else is referenced from here)
├── <logo>.png/.jpg               (referenced by competition.yaml's `image`)
├── pages/
│   ├── terms.md                  (referenced by `terms`; required)
│   ├── overview.md                )
│   ├── evaluation.md              )  referenced by `pages`; optional but expected
│   └── data.md                    )
├── <phase_name>/
│   ├── input_data/                 (code submission only: what the ingestion program reads)
│   └── reference_data/             (ground truth: only the scoring program sees this)
├── public_data/                  (optional: mirrors dev-phase data for participants to explore)
├── ingestion_program/            (code submission only)
│   ├── ingestion.py
│   └── metadata.yaml
├── scoring_program/              (always required)
│   ├── scoring.py
│   ├── <vendored helper modules>   (see "Vendor shared code")
│   └── metadata.yaml
├── solution/                     (organizer's reference implementation;
│   └── model.py                     doubles as the participant-facing example submission)
└── starting_kit/                 (what a participant downloads to get started)
    ├── README.md
    ├── model.py                  (a naive baseline participants build on)
    └── sample_submission.zip     (a zipped, ready-to-upload example; usually solution/ re-zipped)
```

The docs say files "can be under a directory, they just have to be referenced by their full
path in `competition.yaml`". The layout above is convention (and what the real example
uses), not a hard requirement, but stick to it unless there's a specific reason not to.

## `competition.yaml` schema

### Required top-level keys
- **`version`**: must be `2`.
- **`title`**: competition name.
- **`image`**: logo file path, relative to `competition.yaml`.
- **`terms`**: path to a markdown/HTML file with participation terms.

### Optional top-level keys (with defaults where noted)
- `description`;
- `registration_auto_approve` (default False);
- `docker_image`: Codabench's default when unset is `codalab/codalab-legacy:py3`. This
  skill's bundles set `codalab/codalab-legacy:py312`. Either way, check it has what the
  scoring program needs (see "Docker image");
- `make_programs_available`, `make_input_data_available`, `queue`,
  `enable_detailed_results`;
- `show_detailed_results_in_submission_panel` and `show_detailed_results_in_leaderboard`
  (default True);
- `contact_email`, `reward`;
- `auto_run_submissions`, `can_participants_make_submissions_public` and `forum_enabled`
  (default True).

### `pages` (optional but expected)
```yaml
pages:
  - title: Welcome
    file: pages/overview.md
```
Each entry needs `title` and `file`.

### `tasks` (required, at least one)
Either define a new task, or reference an existing one by `key` (a database task UUID, which
ignores every other field). To define a new task:
- **Required**: `index`, `name`, `scoring_program` (path to a dir or `.zip`).
- **Optional**: `description`, `input_data` (code submission only), `reference_data`,
  `ingestion_program` (code submission only), `ingestion_only_during_scoring`.

### `phases` (required, at least one)
- **Required**: `name`, `start` (datetime), `tasks` (array of task indices). `end` may be
  omitted only for the final phase (it then never closes).
- **Optional**: `index`, `max_submissions`, `max_submissions_per_day`,
  `auto_migrate_to_this_phase`, `execution_time_limit` (seconds, default 600),
  `hide_output`, `hide_prediction_output`, `hide_score_output`, `starting_kit` (folder
  path), `public_data` (folder path), `accepts_only_result_submissions`.

The real example uses exactly two phases:
- **Development**: many submissions allowed, tune freely;
- **Final/Testing**: usually `max_submissions: 1`, fresh unseen data.

That maps onto element B's held-out generalization set. Reuse the two-phase pattern by
default.

### `solutions` (optional)
- **Required**: `index`, `tasks` (array of task indices it applies to), `path`.

### `leaderboards` (required, at least one)
- **Required**: `title`, `key` (used internally, e.g. `main`), `columns`.
- **Optional**: `submission_rule` (`Add`, `Add_And_Delete`, `Add_And_Delete_Multiple`,
  `Force_Last`, `Force_Latest_Multiple`, `Force_Best`), `hidden`.

Each **column**:
- **Required**:
  - `title`;
  - `key`, which **must exactly match a key in the scoring program's `scores.json`**.
    This is the most common place a bundle breaks;
  - `index`, which also sets ranking priority. Index 0 is the primary sort key; ties are
    broken left to right by increasing index, then by earliest submission.
- **Optional**: `sorting` (`desc` = larger is better, `asc` = smaller is better),
  `computation` (`sum`/`avg`/`min`/`max`/`avg_rank`, over `computation_indexes`),
  `precision` (default 2 decimals), `hidden`.

### `fact_sheet` (optional)
Metadata questions asked at submission time (e.g. "which framework did you use?"). Each
entry has `key`, `type` (`checkbox`/`text`/`select`), `title`, `selection` (choices, or `""`
for free text), `is_required` and `is_on_leaderboard`. Write these as the strings
`"true"`/`"false"`, as the real schema does, not YAML booleans.

## Ingestion and scoring programs

Both are a directory containing the program's code plus a **`metadata.yaml`** with exactly
one key, confirmed in every real example inspected:
```yaml
command: python3 ingestion.py    # or: python3 scoring.py
```
No other `metadata.yaml` keys appeared in the three real bundle variants checked (code
submission, results submission, ingestion during scoring). If a bundle needs more (GPU
access, extra environment variables), verify against current Codabench docs rather than
assuming a key exists.

**The directory contract** (verified from real, executable `ingestion.py`/`scoring.py`).

The ingestion program (code submission only) sees, inside its container:
- `/app/input_data/`: the task's `input_data` (never the ground truth);
- `/app/output/`: where it writes `prediction` and, optionally, `metadata.json` (e.g.
  `{"duration": ...}`, which the real example passes through to the leaderboard);
- `/app/program`: its own code (add to `sys.path`);
- `/app/ingested_program`: the participant's submitted code, extracted (add to
  `sys.path`, then `from model import Model` or whatever the fixed interface is).

The scoring program sees:
- `/app/input/ref`: the task's `reference_data` (ground truth);
- `/app/input/res`: the ingestion program's `/app/output/` (or, for a results submission,
  the participant's upload);
- `/app/output/`: where it writes **`scores.json`**, with keys matching the leaderboard
  columns;
- `/app/program`: its own code.

**Use the `CODABENCH_ROOT` override, not the hardcoded path.** The real examples hardcode
`/app/...`, which only works inside the container and makes testing without Docker
impossible. This skill's programs read the root from an environment variable:
```python
ROOT = os.environ.get("CODABENCH_ROOT", "/app")
```
and build every path under `ROOT`. Inside Codabench the variable is unset, so behavior is
identical. Locally, `scripts/validate_codabench_bundle.py` sets it to a temp directory to
dry-run the same code without Docker. Keep this convention in every generated program.

## Vendor shared code into each program directory

`ingestion_program/` and `scoring_program/` are zipped and uploaded **independently**.
Neither can import from this skill's `scripts/metrics.py`, from each other, or from
anywhere outside its own directory at runtime. Copy the specific functions a program needs
(`r_squared`, `smape`, ...) into a small module inside that program's directory.
`assets/codabench/example_bundle/scoring_program/metrics.py` is exactly this: a trimmed,
self-contained copy, not a reference back to the skill.

## What a participant's submission zip must contain

There's **no fixed format**. It's whatever the ingestion program (code submission) or
scoring program (results submission) actually reads, so verify it against those files:
- **Code submission**: whatever file(s) the ingestion program imports, at the **root of the
  zip** (no wrapping folder). If `ingestion.py` does `from model import Model`, the zip
  needs `model.py` at its root, defining a `Model` class with the methods the ingestion
  program calls.
- **Results submission**: whatever filename(s) the scoring program reads from `res`. If
  `scoring.py` reads `os.path.join(prediction_dir, 'prediction')`, the zip needs a file
  literally named `prediction` at its root.

`scripts/validate_codabench_bundle.py` checks this. If the program declares a module-level
`SUBMISSION_FILES = [...]`, it reads that, parsing the file with `ast` and never importing
it. Otherwise it falls back to a regex over the program source (`from X import Y` for code
submissions, a literal `os.path.join(<res/prediction dir>, "<name>")` for results). It warns
if the declared list misses a name the source appears to read. Declare the constant in
every program you generate; the regex is a fallback for bundles you didn't write.

## What to ask the user

**Must ask (no sensible default exists).** Ask these together, in one pass:
- the competition title, and which submission mode fits the benchmark;
- a logo image. If none exists yet, note the bundle is missing one rather than fabricating
  a placeholder graphic;
- terms and conditions. **Never author real participation terms.** Generate an
  obviously-marked placeholder (pattern: `assets/codabench/example_bundle/pages/terms_and_conditions.md`),
  and say plainly that it must be replaced before the competition goes live. Uploading with
  the placeholder is acceptable only to a dev instance, and only when the user confirms
  that's the purpose;
- phase start dates (and end dates, except optionally for the final phase);
- a contact email, if they want one listed.

**Ask, but offer the default and move on if they don't care:**
- the Docker image (see "Docker image");
- max submissions, submissions per day, execution time limit;
- `registration_auto_approve`, `forum_enabled`, `can_participants_make_submissions_public`.

**Don't ask; derive from the standalone benchmark:** see the next section.

## Mapping the five ontology elements onto the bundle

| Ontology element | Bundle location | Comes from |
|---|---|---|
| Problem Specification and Constraints | `pages/overview.md`, `pages/data.md`; task `description` | the benchmark card |
| Dataset (splits) | per-phase `reference_data` (+ `input_data` for code submission); `public_data/` | the splits, via `build_bundle.py` |
| Performance Metric(s) | `scoring_program/scoring.py`; leaderboard `columns` | `src/<pkg>/score.py`, vendored |
| Reference Solution | `solution/` (also the example submission) | the reference model's predictions or code |
| Documentation and Reproducible Protocol | `pages/*.md`, `starting_kit/README.md`, `terms` | the benchmark card, `SUBMISSION.md` |

## Docker image

The Codabench docs say nothing about what's preinstalled. The table below comes from the
real base Dockerfiles; treat it as the source of truth over guessing.

| `docker_image` | Base | Preinstalled (from the real Dockerfile) | Notes |
|---|---|---|---|
| `codalab/codalab-legacy:py37` | Anaconda 3-2019.07 | theano, Cython, numpy, scipy, scikit-learn, pandas, pyyaml, imutils, tensorflow | run scripts with `python3`, not `python` |
| `codalab/codalab-legacy:py39` | Anaconda 3-2022.05 | same as py37 | run scripts with `python3`, not `python` |
| `codalab/codalab-legacy:py312` (what this skill's example bundles set) | `python:3.12-slim-bookworm` | Cython, numpy 1.26, scipy, scikit-learn 1.5, pandas, pyyaml, imutils, numba, matplotlib, psutil | no Anaconda; `python3` works |
| `codalab/codalab-legacy:gpu` | `tensorflow/tensorflow:latest-gpu-py3` | TensorFlow + common libs | the CPU images have **no torch**, and only py37/py39 have tensorflow |
| `codalab/codalab-legacy:gpu310` | `nvidia/cuda:12.4.1-cudnn-runtime-ubuntu20.04`, Python 3.10 | numpy, scipy, scikit-learn, pandas, pyyaml, opencv-python, **torch 2.3.1**, **tensorflow 2.16.1**, tqdm, h5py, jupyter | the only stock image with PyTorch |

**Check the programs' real dependency file against this table first** (don't guess). If
it's a subset of one row, use that image and stop. Most benchmarks need nothing custom: a
results-submission scoring program usually needs only numpy and pandas. A code submission
running the reference solution may not be covered. wa-hls4ml's models need PyTorch
Geometric, which `gpu310` lacks, so they'd need a custom image.

**A GPU `docker_image` alone doesn't grant GPU execution.** The competition also needs a
GPU-capable compute worker attached to its `queue` (Codabench docs: "Organizers > Running
Benchmarks > Compute Worker Setup"). That's the organizer's infrastructure, out of scope
here, but say so rather than letting the user assume `gpu310` is enough.

### Building a custom image

Use the **Dockerfile method**, not an interactive `docker commit`: an image nobody can
rebuild from source is exactly the kind of unreproducible artifact this skill exists to
avoid.

1. **Start from a template.** Use `assets/codabench/Dockerfile.template` (CPU) or
   `Dockerfile.gpu.template` (GPU), which extend the real `Dockerfile-py312`/`Dockerfile-gpu310`.
   Add exactly the packages the programs' own dependency file lists, and nothing "just in
   case". Save it at the bundle root as `Dockerfile` (or `Dockerfile.gpu`) so the validator
   finds it.
2. **Build and test in one step** with the validator's tier 4 (`--docker`, see
   "Validation"). It builds the Dockerfile under an obviously local tag,
   `benchmark-builder-local/<slug>:validate`, and runs the real programs inside it. That tag
   can never be mistaken for, or pushed as, the published image. Tier 4 warns when it
   validated a local build while `competition.yaml` declares a different `docker_image`,
   since Codabench pulls the declared one.
3. **Publishing is a public action: get explicit confirmation before every `docker push`**,
   even if the user approved one earlier in the conversation. Pushing to Docker Hub makes
   the image publicly pullable (a private repository has its own cost and auth
   implications to flag). The validator never pushes:
   ```bash
   docker tag benchmark-builder-local/<slug>:validate <dockerhub-username>/<image-name>:<tag>
   docker login
   docker push <dockerhub-username>/<image-name>:<tag>
   ```
4. **Point the bundle at it.** Set `docker_image: <dockerhub-username>/<image-name>:<tag>`
   in `competition.yaml`, then re-run tier 4 with `--no-build` to confirm the *published*
   image works.

Codabench's docs don't say whether private registries or auth-gated images are supported.
If the user needs one, tell them to check with Codabench rather than assuming either way.

## Example submission

Every bundle needs a submission a participant can look at and run. It's also the fastest
way to prove the bundle works end to end.

1. **Reuse the reference solution.** Zip it flat (root files only, no wrapping folder:
   `zipfile.ZipFile(...).write(path, arcname=filename)`, not a recursive directory zip)
   into `starting_kit/sample_submission.zip`.
   - **Results submission:** `build_bundle.py` does this from the reference model's
     predictions.
   - **Code submission:** `solution/model.py` becomes the zip, as in
     `assets/codabench/example_bundle/`.
2. **Optionally add a weaker starting point.** If an obviously-a-starting-point baseline
   would help participants more than the full reference solution, put it in
   `starting_kit/model.py`, and keep the reference solution's zip as a separate "working
   example". The example bundle shows both patterns.

## Validation

```bash
python scripts/validate_codabench_bundle.py <bundle_dir> --submission <sample_submission.zip> --task-index 0
```

The script's docstring describes its four tiers:
1. structure: YAML and paths, leaderboard column keys, `metadata.yaml` present and parseable;
2. the submission contract: does the zip contain what the program reads (`SUBMISSION_FILES`,
   else the source regex);
3. a local functional dry run, without Docker (for bundles using `CODABENCH_ROOT`). It
   produces a real `scores.json` and diffs its keys against every leaderboard column,
   which catches the most common break;
4. with `--docker`, a faithful run inside the image.

**Never hand over a bundle without running tiers 1-3.** Then:

- **Validate the pipeline's zips.** For a results submission, validate every
  `<results>/codabench/*_submission.zip`. Their Codabench scores must equal the
  benchmark's own `metrics.json`.
- **Validate deliberately malformed zips:** a missing sample, a NaN, a missing file, a
  wrapping folder. Each must fail with a message naming the problem, except the wrapping
  folder, which the scoring program must tolerate.
- **Run tier 4 if Docker is available on this machine.** Check rather than assume: the tier
  skips itself and says why when the daemon isn't reachable.
  ```bash
  python scripts/validate_codabench_bundle.py <bundle_dir> --submission <sample_submission.zip> --docker
  ```
  - It builds the bundle's `Dockerfile` if there is one (otherwise it uses or pulls
    `competition.yaml`'s `docker_image`), then runs the real programs against Codabench's
    actual `/app/...` layout.
  - It's the only tier that catches "works on my machine, but the declared image is
    missing a dependency", since tiers 1-3 use the host's Python.
  - Everything it does is local and reversible (build, pull, run; `--rm-built-image`
    removes an image it built). It never pushes.
  - Useful flags:
    - `--dockerfile PATH`: a Dockerfile in a non-standard location;
    - `--no-build`: use or pull the declared image only;
    - `--gpus`: pass `--gpus all`;
    - `--docker-host URL`;
    - `--timeout SECONDS`: defaults to the phase's `execution_time_limit`, else 600 s.
      Raise it for programs with real training cost.
- **Report the actual scores**, not just "validation passed". Show the `scores.json` values
  the sample submission produced.
- **Run the discrimination check** ("Ranking and discrimination"): score the reference
  solution and the weak-baseline zip from `build_bundle.py`, and report both. If they don't
  separate clearly, flag it before calling the bundle done.
- **Record it all in `codabench/README.md`** (workflow step 10).

### Tier 3 troubleshooting: host missing dependency

Tier 3 runs the programs with the **host's** Python. If the host lacks a package the image
provides (numpy, pandas, ...), the validator reports "tier 3 not verified: host Python is
missing dependency X" as a warning. That's a host problem, not a scoring failure: install
the package on the host and re-run, or rely on tier 4. If the missing module is one the
program should vendor (e.g. `metrics`), it's an error: add the file to the program's
directory.

### Tier 4 troubleshooting: "docker daemon not reachable"

"Not reachable" often means the client-to-engine bridge is broken while the engine is fine.
This happened with Rancher Desktop on Windows: the client reported "timed out dialing
Hyper-V socket" while dockerd inside the VM was healthy. Tier 4 for axess-benchmark passed
by running the validator from WSL Ubuntu against a working engine. Options:
- `--docker-host URL` (or `DOCKER_HOST`) points every docker call at a specific engine,
  e.g. `unix:///var/run/docker.sock` inside WSL, or `tcp://host:2375`;
- run the validator from WSL/Linux, where the engine's socket is local. The host Python
  there may lack numpy/pandas, which only affects tier 3;
- the validator only needs *some* engine that can pull and run the declared image.
