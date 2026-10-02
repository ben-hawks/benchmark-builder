# LLM benchmarks

How this skill builds a benchmark whose task evaluates language models: question answering,
reasoning, extraction or generation over text, scored on the model's answers. The five
elements, the rubric and the repository layout don't change. What changes:

- **The task is an lm-evaluation-harness task.** It's built with the genesis
  lm-eval-harness skills.
- **Predicting means running models through lm-eval.** Its output is kept as the canonical
  record of each run.
- **The pipeline contract is unchanged.** A per-sample prediction CSV is exported from that
  record, so scoring, the leaderboard and Codabench submissions work as for any other
  benchmark.
- **Model cards come from the genesis `card-eval-updater` skill.**

The aim is compatibility with Genesis Mission evaluation tooling. lm-eval's output is what
`card-eval-updater` reads, and the same task runs locally, on a cluster, or against any
OpenAI-compatible endpoint. Load the genesis skills as `references/genesis-skills.md`
describes. Its notes on the lm-eval chain and on `card-eval-updater` list the problems
already found.

Everything below was run end to end on 2026-10-02 with lm-eval 0.4.13 on CPU, using
EleutherAI/pythia-14m on the 24-question `beamline_qa` task from the genesis catalog's
`card-eval-updater` example. The steps:
1. `scripts/predict_lm_eval.sh` ran the model;
2. `lm_eval_export.py` reproduced lm-eval's `acc` and `acc_norm` on every sample;
3. `card-eval-updater` parsed the run and validated the card it wrote.

## How the elements change

**A. Problem specification.** The prompt is part of the problem: template, instructions,
few-shot count and source split, chat template on or off, and the answer format the model
is asked for. Fix them in the task YAML and the documented protocol, so every model is
run the same way. System constraints include the context length and any token or cost
budget.

**B. Dataset.** On top of the usual FAIR and split questions:
- **Sample IDs.** Each item needs a stable ID field in the data itself.
  lm-eval's `doc_id` is only a position after `process_docs` and must not become the
  `sample_id`.
- **Contamination.** Is the test set public, and could it be in the reference models'
  training data? Options:
  - a private held-out split (kept hidden in a Codabench bundle's reference data);
  - a canary string;
  - items created after the models' training cutoffs.

  Record what's known in the dataset section, and as a limitation if nothing can be done.
- **Answer-format artifacts.** The genesis `data-exploration` skill found that the gold
  answer was the longest option in 16 of 24 items of `beamline_qa` (25% expected by chance).
  Look for length, position and wording artifacts that let a model score without the
  knowledge being tested.

**C. Metrics.** They're defined in the task YAML (`metric_list`, filters for answer
extraction) and re-implemented in the benchmark's `score.py` on the exported answers. State:
- the extraction rule (regex/filter) and the normalization (case, whitespace, punctuation,
  number formats);
- for multiple choice, whether the headline is `acc` (raw loglikelihood) or `acc_norm`
  (length-normalized). They pick different answers.

LLM-judged metrics are part of the metric definition. The definition then includes the
judge model and its revision, the judge prompt and its decoding settings. Such a metric is
non-deterministic, so report it with that caveat. `card-eval-updater` labels such results.

**Statistical power.** lm-eval reports a standard error. With N items and accuracy p it's
about sqrt(p(1-p)/N): ±0.09 at N = 24. Say what difference the benchmark can resolve, and
don't rank models whose gap is inside it.

**D. Reference solutions.** Named models run through the fixed protocol. At least one should
be **open-weights at a pinned revision** (`pretrained=org/model,revision=<commit sha>`, not
`main`). An API-only model can be a comparison, but nobody can re-run it later on the same
weights, so mark it auxiliary unless the user decides otherwise. See "Verifying LLM
reference solutions" below.

**E. Documentation.** The protocol is the reproduction recipe:
- lm-eval version and install extras;
- the exact `lm_eval` command per model (model type, `model_args`, few-shot count, chat
  template, seeds, batch size);
- hardware and wall time.

## Building the task: the lm-eval-harness skills

Load `configuration-creator` and follow it. It runs `configuration-planner`,
`data-exploration`, `configuration-implementor` and `configuration-tester` in order, with a
checkpoint after each. Hand it what elements A-C already settled, so the planner confirms
rather than asks again.

Its outputs go in the benchmark repo:

```
tasks/<task>/
├── plan.md               the chain's plan + decision logs (keep: it documents the design)
├── _template_yaml        (if several splits) shared task settings
├── <task>_<split>.yaml   one lm-eval task per benchmark split, each `include:`-ing the template
├── utils.py              (if needed) process_docs, doc_to_text, answer extraction
└── scratch/              the chain's analysis scripts (keep the ones that found something)
```

Adjustments for a benchmark repo:

- **One lm-eval task per benchmark split.** Name it `<task>_<split>`, sharing settings
  through `_template_yaml` (the pattern in the chain's `assets/examples/pisa/`). The
  pipeline then runs and scores each split separately, like any other benchmark.
- **Pin the data.** For a Hugging Face dataset, set `dataset_kwargs: {revision: <commit>}`.
  For local files, write `data_files` relative to the repo root; `predict_lm_eval.sh`
  always runs from there. The chain writes absolute paths, which break on any other
  machine.
- **Test the extraction.** `configuration-tester` runs with `--limit 5`. That validates the
  config, not the benchmark. Reference numbers come from full runs.

## Pipeline mapping

```
fetch_data → predict_lm_eval.sh (per model, per split) → score_all.sh (truth, score, leaderboard, submissions)
                │
                ├── <results>/lm_eval/<model>/<split>/<model_name>/results_*.json, samples_<task>_*.jsonl   (canonical record)
                └── <results>/<split>/predictions_<model>.csv (+ .meta.json)                                (pipeline contract)
```

- **`scripts/predict_lm_eval.sh`** (adapt `assets/repo/predict_lm_eval.sh`): runs `lm_eval`
  with `--log_samples` and the benchmark's fixed protocol flags into its own run
  directory. Then it calls the exporter. It refuses to reuse a run directory, so each
  holds exactly one run.
- **`src/<pkg>/lm_eval_export.py`** (adapt `assets/repo/lm_eval_export.py`): writes
  `predictions_<model>.csv` with `sample_id`, `answer` (and `answer_norm` for multiple
  choice), plus lm-eval's own per-sample metric values as `lm_eval_<metric>` columns. A
  `.meta.json` sidecar records model identity, `model_args`, task hash, n-shot, chat
  template and lm-eval version. It refuses:
  - sample-limited runs;
  - missing or duplicate IDs;
  - more than one run in the directory;
  - a run with no verifiable model identity, unless `--model-id` is given.

  It warns when the model type is a custom class, whose `model_name` may not be what ran.
- **`truth.py`** reads the answer key from the dataset by the same `sample_id` rule.
  **`score.py`** computes the benchmark's metrics from `answer`/`answer_norm` vs truth, with
  the same extraction and normalization as the task. It ignores the `lm_eval_*` columns
  except in the agreement check below.
- **Participants who don't use lm-eval** plug in by writing the same CSV (`sample_id`,
  `answer`, plus `answer_norm` if the benchmark scores it). Say this in `SUBMISSION.md`.

Install lm-eval with the extras its backends need. 0.4.13's `hf` backend fails without
`lm_eval[hf]` (`No module named 'accelerate'`). Pin the lm-eval, transformers and torch
versions that worked in `requirements.txt` (`references/genesis-skills.md`, "Version
triangle").

**Where models run:**

| Model | `lm_eval --model` | Where |
|---|---|---|
| open weights, small | `hf` | laptop/CPU, or the `infer_cpu` job |
| open weights, GPU | `hf` or `vllm` | the `infer_gpu` job (Slurm or PBS templates), batch size measured per machine |
| served by an OpenAI-compatible endpoint (a vLLM server, a NIM, an institutional LLM API such as AmSC i2) | `local-chat-completions` / `local-completions` with `base_url` | anywhere that can reach the endpoint. On a cluster, check compute-node network access (`references/hpc.md`) |
| on Perlmutter via NeMo-Skills | the genesis `perlmutter-nemo-generate` / `-eval` skills | see below |

**NeMo-Skills on Perlmutter.** `perlmutter-nemo-eval` (`ns eval`) only evaluates
benchmarks registered in the user's NeMo-Skills checkout. For a new benchmark, use
`perlmutter-nemo-generate` on an `input.jsonl` built from the task's prompts (one line per
`sample_id`). Then convert its `output*.jsonl` generations into `predictions_<model>.csv`
with the task's extraction rule, and score with `score_all.sh`. Keep the NeMo-Skills
output directory as that run's canonical record. `card-eval-updater` reads NeMo-Skills
`metrics.json` (with `--model-id`) once the benchmark is registered there.

## Verifying LLM reference solutions

These are the five checks from `references/reference-solution-checks.md`, adapted. Results
go in `docs/VALIDATION.md`.

1. **Identity and revision.** In each run's `results_*.json`, check that `config.model`,
   `config.model_args` and `model_name` all name the model you meant. A custom model class
   with a `pretrained=` it ignores still gets that name: the genesis example recorded
   `mistralai/Mistral-7B-Instruct-v0.3` for a model that never ran. Pin `revision=<commit
   sha>` and record it in `reference_solution/README.md`. The export's `.meta.json` keeps
   this per run.
2. **The answer key.** Confirm on data that `doc_to_target` produces the field the benchmark
   scores (an index vs a letter vs the choice text; 0- vs 1-based). Recompute a few items
   by hand.
3. **The whole procedure.** Check that every model ran with the same protocol: few-shot
   count and seed, chat template, system prompt, decoding settings (`gen_kwargs`), answer
   filters, max length. A model run without its chat template, or with a different few-shot
   count, isn't comparable. lm-eval records these in `results_*.json`; compare them across
   models.
4. **Per-sample agreement.** For every reference run, `score.py`'s per-sample correctness
   must equal lm-eval's own per-sample metric (the `lm_eval_<metric>` columns), and the
   aggregates must match `results_*.json`. Put this in `tests/` on a committed fixture run,
   as the golden test. A full run is required: the export refuses a `--limit` run.
5. **Reference vs auxiliary, and a control.** Mark API-only and comparison models
   auxiliary. Also run a **weak control** that any real model must beat: random choice,
   the majority answer position, or a lexical-overlap model like the one in the genesis
   example. Report the separation in standard errors. If the reference doesn't clearly beat
   the control, the benchmark (or the reference) isn't measuring what it claims.

## Model cards: `card-eval-updater`

For each reference model with a Genesis/BPSW (GEAR) model card, point
`card-eval-updater` at one run directory
(`<results>/lm_eval/<model>/<split>/<model_name>/`) and follow its workflow: parse,
dry-run, write, validate. Its guardrails line up with the export's: it refuses partial runs
and unverifiable identities. Store each card next to the benchmark card
(`references/doe-gear-cards.md`). With lm-eval 0.4.13 it also records lm-eval's
`sample_len` field as a metric; remove that `metrics:` entry by hand
(`references/genesis-skills.md`).

## Codabench

Use a **results submission**: participants upload `predictions_<split>.csv` files
(`sample_id`, `answer`[, `answer_norm`]), and the scoring program applies the benchmark's
extraction-free comparison against hidden truth. A code submission would need GPU workers
and model weights in the container, which is rarely practical.

Scoring-program checks, on top of `references/codabench.md`'s contract:
- an `answer` that isn't a valid choice index (multiple choice) fails with a message;
- for generation, an empty answer is scored as wrong, not rejected;
- the rule that turns raw text into `answer` is documented in the starting kit, since
  participants apply it themselves.

Rank on the headline metric of the primary split. If the test answers are public, say on
the competition page that the leaderboard can't detect training on the test set.
