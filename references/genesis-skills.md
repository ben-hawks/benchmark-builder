# Using Genesis Mission skills from benchmark-builder

Several steps of this skill are done better by an existing skill in the Genesis Mission
catalog, [AI-ModCon/genesis-skills](https://github.com/AI-ModCon/genesis-skills)
(read-only mirror: `gitlab.osti.gov/genesis/genesis-skills`). benchmark-builder
**loads those skills on demand and follows their workflows**. It doesn't copy them, and it
doesn't paraphrase them as its own instructions. This file says which skill to load at
which step, what to hand it, what comes back into the benchmark repo, and the problems
already found when chaining them.

**Pinned commit:** `b7e8434f3cd15a0c8cb6cb0313942cd4b1d06cee` (2026-09-25). Everything
below was checked against that commit.

## How to load a genesis skill

Try these in order, and stop at the first that works:

1. **It's already installed.** The client lists it by name (e.g. `slurm`,
   `card-eval-updater`), or it's in the user's skills directory. Use it. If its
   instructions differ from what this file expects, follow the installed skill and tell the
   user about the difference.
2. **`skill-search` is installed.** Run its search (`python scripts/skill_search.py --query
   "<what you need>"`), then load the matching `SKILL.md`.
3. **Neither.** Fetch the catalog into a cache outside the benchmark repo and read the
   skill from there:
   ```bash
   GS=${GENESIS_SKILLS_DIR:-$HOME/.cache/genesis-skills}
   [ -d "$GS/.git" ] || git clone --filter=blob:none https://github.com/AI-ModCon/genesis-skills "$GS"
   git -C "$GS" fetch --quiet origin
   git -C "$GS" checkout --quiet <ref>     # ref: see "Which ref" below
   ```
   Then read `$GS/<path>/SKILL.md` in full (paths are in the table below). Its own relative
   paths (`scripts/...`, `references/...`) resolve against that skill's directory. Run
   its scripts from there, never from a copy.
   Installing the catalog into the user's skills directory (`./unpack.sh <domain> --target
   <dir> --mode symlink`) changes their setup, so ask first.
4. **No network and no copy.** Say so. Continue with this skill's own fallback for that
   step (each section below names one), and mark whatever it produces as not checked by the
   genesis skill.

**Which ref:**

| Kind of skill | Ref | Why |
|---|---|---|
| HPC site and scheduler skills (`perlmutter`, `frontier`, `aurora`, `slurm`, `pbs`) | `origin/main` | They hold site facts (queues, limits, modules, filesystems) that change. Load the latest whenever the user says they run on that machine. |
| Workflow skills whose scripts or output formats this skill depends on (all the others) | the pinned commit | Their scripts and file formats were checked against it. A newer commit may still work, but check before relying on it. |

Record what you actually used in the benchmark repo: the skill name and the commit
(`git -C "$GS" rev-parse --short HEAD`). It goes in `docs/<MACHINE>.md` for site facts, and
in the "Tools used" list of `docs/VALIDATION.md` for everything else.

**Name clashes.** Some genesis skill names are generic (`data-exploration`,
`skill-creator`), and a client may have an unrelated skill with the same name. Confirm by
path or content: genesis `data-exploration` writes to `tasks/<benchmark>/scratch/` and
updates `plan.md`.

### `amsc-mlflow`: loaded the same way, from its own repository for now

`amsc-mlflow` (American Science Cloud / Genesis Mission MLflow: tracking, benchmark-result
logging, model registry) follows the genesis-skills format, but until it's merged into the
catalog it lives in [ben-hawks/genesis-mlflow](https://github.com/ben-hawks/genesis-mlflow)
at `skills/amsc-skills/amsc-mlflow`. Load it like any other genesis skill (installed copy
first, then `skill-search`, then a clone), with this repository and ref:

```bash
GM=${GENESIS_MLFLOW_DIR:-$HOME/.cache/genesis-mlflow}
[ -d "$GM/.git" ] || git clone --filter=blob:none https://github.com/ben-hawks/genesis-mlflow "$GM"
git -C "$GM" fetch --quiet origin
git -C "$GM" checkout --quiet c008d94527ec47449f42609cbc8ea1ce4e44522b   # pinned
# the skill: $GM/skills/amsc-skills/amsc-mlflow/SKILL.md
```

Once it's in genesis-skills, load it from there at the catalog's pinned commit instead.

## Rules when delegating

- **Read the delegated `SKILL.md` in full and follow its workflow**, including its own
  checkpoints and refusals. Where its guardrails are stricter than this skill's (e.g.
  `card-eval-updater` refuses sample-limited runs, and `datacard-generator` requires live
  identifier checks), they win.
- **Tell it where to write.** Its outputs land in the benchmark repo, at the paths given
  below, not wherever its defaults point.
- **Don't vendor its scripts into the benchmark repo.** A benchmark's runtime code (truth,
  score, submission, Codabench scoring program) stays the benchmark's own. If the benchmark
  really needs a genesis script at runtime, copy that file with its Apache-2.0 header and
  attribution, and say so in the README.
- **Keep both perspectives.** A genesis skill does its job (an lm-eval task, a datacard,
  job scripts), and this skill still checks it against the benchmark: the five elements, the
  pipeline contract and the rubric evidence.

## Integration map

Paths are relative to the genesis-skills root.

| benchmark-builder step | Genesis skill (path) | When | Hand it | Take back |
|---|---|---|---|---|
| Gather artifacts; element C (what similar benchmarks measure); element E (related work) | `literature-search` (`skills/literature-search`) | The user has no paper or prior-work list, or the motif table in `references/ontology.md` doesn't cover the task | the task, domain and motif | prior benchmarks + their metrics; citations, then re-fetched from doi.org (see below) |
| Element B: dataset card | `datacard-generator` (`skills/basedata-skills/datacard-generator`) | DOE/Genesis work, or the dataset needs a data card | the dataset directory; answers already gathered for element B | `genesis_datacard_<name>.md`, validated with `linkml-validate` |
| Element B: Croissant metadata | `croissant-validator` (`skills/basedata-skills/croissant-validator`) | the dataset has no `croissant.json`, or one exists to validate | data files (its generator reads CSV), name, license URL, creator, URL | `data/croissant.json` (or the dataset host's), validated |
| Element C: independent metric check | `uq-metrics-evaluator` (`skills/basesafe-skills/uq-metrics-evaluator`) | regression or classification benchmarks | `predictions_<ref>.csv` and `truth.csv` for one split | metrics recomputed independently; agreement recorded in `docs/VALIDATION.md` |
| Element C/D: uncertainty | `uq-metrics-evaluator`, `uncertainty-quantification` (`skills/basesafe-skills/...`) | a reference model outputs uncertainties or probabilities, or the task's predictions gate decisions | the same CSVs plus the uncertainty/probability columns; the reference model's code | calibration metrics to consider for the benchmark; an uncertainty audit for the rubric's Metric Quality evidence |
| LLM benchmarks: build the task | `configuration-creator` → `configuration-planner` → `data-exploration` → `configuration-implementor` → `configuration-tester` (`skills/baseeval-skills/lm-eval-harness-skills/...`) | the motif is text, QA or reasoning evaluated on language models | the dataset and the element A/C answers | `tasks/<task>/` (`plan.md`, `<task>.yaml`, `utils.py`) |
| LLM benchmarks: model card | `card-eval-updater` (`skills/baseeval-skills/card-eval-updater`) | a reference or participant model is documented in a Genesis/BPSW model card | one full lm-eval (or Eval Factory / NeMo-Skills) run directory | the card's evaluation sections and `metrics:` frontmatter, validated |
| LLM benchmarks on Perlmutter, API-served models | `perlmutter-nemo-eval` / `perlmutter-nemo-generate` (`skills/baseeval-skills/perlmutter-ns-skills/...`) | the user runs NeMo-Skills on Perlmutter against an OpenAI-compatible endpoint | an env file, a benchmark registered in their NeMo-Skills checkout, a model | `metrics.json` + `output*.jsonl` |
| Track results in AmSC MLflow (optional; user opts in) | `amsc-mlflow` (`skills/amsc-skills/amsc-mlflow` in ben-hawks/genesis-mlflow) | after `score_all.sh`, when the user wants runs in the AmSC / Genesis MLflow service | `--results reference_results` (or a `card-eval-updater` `bundle.json`), `--repo`, `--auxiliary` models | a parent run plus one run per (split, model); its run ID goes in `docs/VALIDATION.md` |
| Register reference weights in the AmSC Model Registry (optional) | `amsc-mlflow` | the user wants reference models loadable as `models:/<name>@production` | `weights/MANIFEST.json`, the weights dir, a loader in the benchmark package | registered versions with sha256 tags; `staging`, then `production` after verification |
| Training runs on a cluster, tracked in MLflow | `amsc-mlflow` (`assets/train_with_mlflow.py`, `assets/mlflow_job_env.sh`) | the benchmark includes training, and the user wants it tracked | the training code, the target site | rank-0 logging, site proxy settings, token-file handling |
| HPC: any Slurm cluster | `slurm` (`skills/hpc-skills/slurm`) | the benchmark runs on a Slurm cluster; submitting, monitoring or debugging jobs | — | scheduler syntax, `sacct`/`scontrol` troubleshooting |
| HPC: any PBS cluster | `pbs` (`skills/hpc-skills/pbs`) | the benchmark runs on a PBS cluster | — | `select`/`depend` syntax, `qstat` troubleshooting |
| HPC: a named site | `perlmutter`, `frontier`, `aurora` (`skills/hpc-skills/<site>`) | **whenever the user says they run on that machine** | — | site facts for the machine profile (queues, limits, GPUs, filesystems, modules) |

## Per-skill notes

### HPC skills (`slurm`, `pbs`, `perlmutter`, `frontier`, `aurora`)

Load from `origin/main` as soon as the user names the machine, and use the site skill to
pre-fill the machine profile before asking the user anything (`references/hpc.md`, "What
to ask per machine"). The site skill provides facts; the user still provides their
account, the benchmark's stack, and measured job sizes. When a site skill and a site's own
docs disagree, the site's docs win, and you tell the user. For job monitoring and failed
jobs, use the scheduler skill's command references (`references/job-control.md`)
instead of improvising.

Fallback without the skill: the questions in `references/hpc.md` plus the site's public
docs, with the source of each value written into `docs/<MACHINE>.md`.

### `datacard-generator`

The DOE FAIR page links the older standalone repo `AI-ModCon/BaseData_Skills`. The same
skill now lives in genesis-skills (the Genesis Datacard v1.2 template, vendored from
`gitlab.osti.gov/genesis/data-cards` at `7226c2c`). Use the genesis copy. Hand it what
element B already settled (splits, license, FAIR answers) so it confirms rather than
asks again. Its live ORCID/ROR/DOI/OSTI checks aren't optional.

`examples/wa-hls4ml/genesis_datacard_wa_hls4ml.md` was built with the same workflow
(from `BaseData_Skills@7ef7694`).

Fallback: `references/doe-gear-cards.md` ("If the workflow can't be run").

### `croissant-validator`

- `scripts/generate_croissant_from_csv.py` only reads CSV. For other formats (JSON, HDF5,
  Parquet, images), write `croissant.json` by hand from `data/SCHEMA.md` and then run its
  validator.
- What a generated file still needs (checked on a CSV at the pinned commit; it passed both
  the script checks and `mlcroissant` parsing):
  - `contentUrl` is the local file name. Replace it with the dataset's real download URL
    (the one `scripts/fetch_data.py` uses) before publishing.
  - Without `--cite-as`, `mlcroissant` warns that `citeAs` is missing. Pass the dataset's
    BibTeX.
  - `mlcroissant` also warns that the `@context` isn't standard (an extra
    `equivalentProperty` key). That's a warning only.
  - Run the validator with `mlcroissant` installed (temporary venv or `uv run --with
    mlcroissant`). Without it, only the required-field checks run, and the script still
    prints OK.
- Its rules: install packages only in a temporary venv, and never run a global
  `pip install`.
- A `croissant.json` with per-file `sha256`, field-level `recordSet`s and an SPDX license
  URL is concrete evidence for the rubric's Dataset FAIR items (Findable, Interoperable)
  and for the MLCommons corpus entry. Record where it lives in `rubric.yaml`.
- If the dataset is on Hugging Face, the Hub already serves Croissant metadata. Validate
  that instead of writing a second one.

### `uq-metrics-evaluator`

- Its role here is as a **second, independent implementation** of the standard regression
  and classification metrics. The benchmark's `score.py` stays the source of truth: it has
  to ship inside the Codabench scoring program.
- Run it on the reference model's predictions for one split. Record any disagreement in
  `docs/VALIDATION.md` and explain it. A known source of disagreement: it drops rows with a
  missing value in the prediction or truth column, while a benchmark may score those as
  failures.
- The CSVs need one row per sample in the same order. Join `predictions_<model>.csv` with
  `truth.csv` on `sample_id` first, and pass the joined file as both inputs.
- It runs with `uv run --with ...`. If `uv` isn't available, use a temporary venv with the
  same packages.
- It reads at most 500,000 rows without warning, and it refuses inputs outside the current
  directory (`--allowed-root`) and symlinks.
- It writes its artifacts next to its input files.
- See `references/metrics-and-uq.md` for which outputs to compare and when calibration
  metrics belong in the benchmark itself.

### `uncertainty-quantification`

This is an audit skill. Use it when the benchmark's reference model emits confidence
scores that downstream users will act on, or when the user asks how the benchmark treats
uncertainty. Its report (implemented / partial / missing per UQ control) is evidence for
the rubric's Metric Quality judgement. It doesn't add metrics by itself.

### lm-eval-harness chain (`configuration-*`, `data-exploration`)

Start with `configuration-creator`; it calls the others in order. Its own path convention
is `tasks/{benchmark_name}/`, which this skill keeps at the benchmark repo root. Known
problems, all from the catalog's own worked example
(`skills/baseeval-skills/card-eval-updater/examples/skill-chain/README.md`):

- **`configuration-tester` can't test a custom model class.** Its `test_config.sh` runs
  bare `lm_eval`, which registers custom tasks (`--include_path`) but not custom models.
  Import the model first, e.g. a `sitecustomize.py` on `PYTHONPATH`, or a small
  `run_eval.py`.
- **An empty `model_args` silently becomes the script's default.** `test_config.sh` uses
  `${4:-default}`. lm-eval then records a model that never ran (`model_name` derived from
  `model_args.pretrained`). Always pass `model_args` explicitly, and check
  `config.model` against `model_name` in `results_*.json`.
- **The tester defaults to `--limit 5`.** That's a smoke test, not a result. The
  benchmark's reference numbers come from a full run.
- **Version triangle for `hf` models.** lm-eval 0.4.10 passes `dtype=` to
  `from_pretrained`, which needs transformers ≥ 4.56, which needs torch ≥ 2.6. Pin the set
  that works in the benchmark's `requirements*.txt`.
- **Data paths.** The skill writes absolute `data_files` paths into the task YAML. Make them
  relative to the repo, or resolve them from `<P>_DATA` in `utils.py`, before committing.
- **lm-eval 0.4.13 needs its backend extras.** `pip install lm_eval` alone fails at
  `--model hf` with `No module named 'accelerate'`; install `lm_eval[hf]` (or `[vllm]`, ...).

See `references/llm-benchmarks.md` for how the task plugs into the pipeline contract.

### `card-eval-updater`

- Parses one run directory into a canonical eval bundle, then writes the evaluation sections
  of a Genesis/BPSW model card under the visible heading `### Automated benchmark results`,
  plus `<benchmark>/<metric>` entries in the `metrics:` frontmatter.
- It accepts only lm-evaluation-harness, Eval Factory and NeMo-Skills output. For other
  benchmarks, `scripts/render_card_results.py` in this skill writes the same heading from
  `metrics.json` (`references/doe-gear-cards.md`).
- Its refusals are correct:
  - sample-limited runs: re-run without `--limit`;
  - no verifiable model identity: ask the user, and pass `--model-id`;
  - two runs under one directory: point it at one.
- **With lm-eval 0.4.13 it records `sample_len` as a metric.** That version adds
  `sample_len` (and `name`) to each task's results. The parser (at the pinned commit)
  turns `sample_len` into a result and a `<task>/sample_len` entry in the card's `metrics:`
  frontmatter. Its validator still passes. Remove the frontmatter entry by hand (its own
  docs say `metrics:` entries may be pruned by hand). Its validator then reports one
  `METRICS_MISMATCH` warning, not an error. Leave the generated table rows: hand edits
  there fail its validator as `UNTRACED`. Alternatively, run the lm-eval version the
  skill was verified with (0.4.10). Re-check at the latest commit.
- Its template path (`modcon-bpsw/cards/templates/model-card.md`) is in a separate repo.
  If the user doesn't have it, start from the live GEAR Model Card template
  (`references/doe-gear-cards.md`). Both share the same section headings
  (`## Evaluation data`, `## Evaluation Procedure`, `## Uncertainty Quantification`,
  `## Evaluation results`).

### `perlmutter-nemo-eval` / `perlmutter-nemo-generate`

- Use these for API-served models on Perlmutter (`ns eval` / `ns generate`, podman-hpc,
  sshproxy MFA).
- `ns eval` evaluates benchmarks registered in the user's NeMo-Skills checkout
  (`nemo_skills/dataset/<benchmark>/`). A new benchmark has to be added there first, so for
  a new benchmark, `perlmutter-nemo-generate` (raw generations from `input.jsonl` +
  `prompt.yaml`) followed by the benchmark's own `score_all.sh` is usually the shorter
  path.
- Both skills refuse models outside their `config/supported_models.txt`.
- `card-eval-updater` reads NeMo-Skills `metrics.json`, but it needs `--model-id`, since
  NeMo-Skills records no model identity, and NeMo-Skills scores are percentages.

### `amsc-mlflow`

- **Opt-in.** Logging to AmSC MLflow is never a required step of a benchmark. Offer it when
  the user works under the Genesis Mission or AmSC, or asks for experiment tracking or a
  model registry.
- **The token is the user's.** They set `MLFLOW_TRACKING_TOKEN` (a MyAmSC Access Token)
  themselves. Never ask for it in the conversation. Run its `check_connection.py` first.
- **Dry run first.** Show `log_benchmark_results.py --dry-run` before logging. It needs no
  token, and its output is what the user approves.
- **Log after the job.** Results logging only reads the scored files, so prefer running it
  from a login node after the cluster job, not from inside it (no token waiting in the
  queue).
- **Traceability.** Every child run carries the sha256 of the `metrics.json` it came from,
  and re-running skips what's already logged. Record the parent run ID, the experiment and
  the server in `docs/VALIDATION.md` ("Tools used").
- **Registering reference weights** (`register_model.py files`) needs a loader function in
  the benchmark's package (`<pkg>.mlflow_loader:load`), which takes the manifest's files and
  returns a predictor. Register as `staging`. Move `production` only after the golden tests
  and a run reproducing `reference_results/` pass, and ask first.
- **Compute-node access.** On Frontier and ALCF systems, compute nodes reach the server
  only through the site proxy. Its `references/hpc.md` lists the settings (Frontier and
  ALCF unverified as of the pinned commit). Perlmutter needs none.
- **Server.** The default is `https://mlflow-staging.american-science-cloud.org` (the AmSC
  integration guide's staging server). Set `MLFLOW_TRACKING_URI` explicitly in anything
  long-lived.

### `literature-search`

- Use it to find comparable benchmarks for the motif, and the metrics they report, when
  `references/ontology.md` Part 3 doesn't cover the task. Use it also when the user has no
  related-work list.
- It returns candidates, not verified citations. Fetch each one's metadata from
  `https://doi.org/<doi>` (`Accept: application/x-bibtex`) before it goes in the README or
  `CITATION.cff`, as elsewhere in this skill.
