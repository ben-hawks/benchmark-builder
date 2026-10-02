---
name: benchmark-builder
description: Helps a user design, structure, document, and self-score a scientific ML benchmark that conforms to the MLCommons Science Benchmarks Ontology (five-element definition, six-category rubric, arXiv:2511.05614), generating a reproducible repo, verifying reference solutions, and packaging a validated Codabench competition. Use whenever the user wants to build, formalize, publish, or audit a benchmark, dataset+task+metric suite, or reproducibility package, including LLM evaluation benchmarks, even if they never say "MLCommons," "ontology," or "Codabench." Trigger on "turn my model comparison into a proper benchmark," "structure this repo so others can reproduce our results," "grade our benchmark documentation," or "make this a Codabench competition." Also self-scores an existing benchmark, writes an MLCommons corpus entry or DOE GEAR/Genesis cards, and runs benchmarks on Slurm or PBS clusters, loading Genesis Mission skills for HPC sites, lm-eval tasks, data/model cards and AmSC MLflow tracking.
---

# Building an MLCommons-ontology-conformant benchmark

A benchmark, per this ontology, is "a carefully defined standardized version of a
scientific application used for making quantifiable comparisons of solutions." The
ontology exists because most things called "benchmarks" in scientific ML are actually
partial: a dataset with no defined task, a task with undefined metrics, code that only
the original author can run. This skill's job is to help a user avoid each of those
failure modes concretely, by walking through five required elements, producing real
files (not just advice), and then scoring the result honestly against the same rubric
MLCommons uses.

## Read first

- **`references/ontology.md`, in full, before anything else.** It has the exact wording of
  all five definitional elements and all six rubric categories. You need the precise
  wording, not a paraphrase, both to interview well and to score correctly later.
- **`references/wa-hls4ml-example.md`**, skimmed, whatever the domain. It covers
  [axess-benchmark](https://github.com/ben-hawks/axess-benchmark), a real benchmark built
  with this skill. It scores 5.00/5, is a validated Codabench bundle, reproduced its
  reference results on NERSC Perlmutter, and lists the concrete mistakes found while
  building it (a wrong reference model, a label mismatch, a metric formula that didn't
  reproduce the paper). Those mistakes are the reason for the verification steps below.
- **`references/repo-structure.md`, in full, before generating any benchmark files.** It
  specifies the recommended layout and the pipeline contract every benchmark follows.
- **`references/genesis-skills.md` before the first step that uses a Genesis Mission
  skill.** Several steps load a skill from
  [AI-ModCon/genesis-skills](https://github.com/AI-ModCon/genesis-skills) on demand:
  - the HPC site and scheduler skills;
  - the lm-eval-harness chain and `card-eval-updater` for LLM benchmarks;
  - `datacard-generator` and `croissant-validator` for the dataset;
  - `uq-metrics-evaluator` for metric checks;
  - `literature-search`;
  - `amsc-mlflow` (AmSC / Genesis Mission MLflow), from its own repository until it joins
    the catalog.

  That file says how to find or fetch each one (pinned commit, or latest for HPC sites),
  what to hand it, and what comes back. Follow the loaded skill's own workflow; don't
  paraphrase it from memory.

Later deliverables each have their own reference, read in full before starting them:

| Deliverable | When | Read |
|---|---|---|
| MLCommons corpus entry | once the benchmark and its score exist | `references/mlcommons-corpus-format.md` |
| DOE GEAR / Genesis Model, Agent, Data cards | DOE/Genesis work, or the reference solution is a model or agent | `references/doe-gear-cards.md` |
| Codabench competition bundle | the user wants participants to submit | `references/codabench-workflow.md`, `references/codabench.md` |
| Cluster runs | the benchmark runs on Slurm or PBS | `references/hpc.md` |
| LLM benchmark | the task evaluates language models | `references/llm-benchmarks.md` |
| AmSC MLflow tracking and model registry | the user opts in (Genesis/AmSC work, or wants experiment tracking) | the `amsc-mlflow` notes in `references/genesis-skills.md`, then that skill's `SKILL.md` |

## Gather artifacts before interviewing

Don't open with a blank interview. Most of the five elements are usually already
answered somewhere: a paper, a repo, a dataset sample, a README, a training script.
Asking questions the materials already answer wastes the user's time and risks getting a
worse answer than what's actually written down. The first pass at wa-hls4ml was built
entirely by reading the paper and repo, not by interviewing anyone. But reading isn't
verifying: the paper's prose turned out to be wrong about which label its checkpoints
were trained on. Treat extracted claims about the reference solution as drafts until
element D's checks confirm them.

Do this, in order, before asking a single interview question:

1. **Check what's already in front of you.** Look at files attached to the conversation or
   already read this session, and the working directory itself: a quick `Glob`/`ls` for
   PDFs, READMEs, notebooks, `data/` or `src/` directories, dataset files and prior
   writeups. If the request names a repo, paper or dataset, read it before asking anything
   about its contents.
2. **Ask for what's missing, once.** Report what you found (a list, not an essay) and ask
   for anything relevant you don't have: a paper or writeup, the code, a dataset sample,
   prior results. Be specific about what would close which element ("a link to the
   training code would answer the Reference Solution and Software Environment
   questions"). If the user has no related-work list and it matters (element C's
   comparable benchmarks, element E's background), offer to run the `literature-search`
   skill.
3. **Extract a draft answer for each of the five elements**, with evidence (file, section,
   line). Don't guess past what the material supports; an element the material doesn't
   address is a real gap to interview for.
4. **Carry the draft into the interview as confirmation, not a cold start.** Show what you
   found per element ("here's what I found for the dataset splits -- still current?") and
   ask real questions only for what the material left open. The confirmation step catches
   stale material before it propagates into the benchmark card.

If the user genuinely has nothing yet, step 3 comes up empty and the interview below runs
in full. The point is never to ask for something that's already sitting in front of you.

## Figure out which mode you're in

By the time artifacts are gathered, you'll usually know which of these applies. Confirm
rather than asking cold:

1. **New benchmark from scratch.** The artifact pass came up mostly empty; the interview
   runs close to its full form.
2. **Formalize an existing project.** Code, data and results exist but aren't organized or
   documented as a benchmark. Confirm the draft, interview only real gaps, and propose
   moving the code into the recommended structure, saying what that buys. Whether to
   reorganize or only add the missing pieces is the user's call.
3. **Score/audit an existing benchmark.** Skip to "Score against the rubric" once the
   artifact pass gives you evidence per rubric item. An un-evidenced score is worse than
   no score, because it's false confidence.

Modes 2 and 3 often turn into mode 1 output once the gaps are visible. Treat this as one
continuous workflow.

**Is it an LLM benchmark?** If the task evaluates language models (QA, reasoning,
extraction or generation over text, scored on the model's answers), read
`references/llm-benchmarks.md` now. The five elements and the rubric are the same. What
changes: the task is built as an lm-evaluation-harness task with the genesis
lm-eval-harness skills, the reference solutions are named models run through it, and its
model cards come from `card-eval-updater`. Note the answer as you go; elements A-E below
point to where the LLM track differs.

## Interview (confirm the draft, fill the gaps)

Work through the five elements in order; each maps onto one or more rubric categories,
so getting them right here is what makes the later score legitimate rather than generous.
Lead with the draft where there is one ("looks like the dataset is already split 80/10/10
by X -- still right?"). Don't dump all five as a questionnaire; work through them
conversationally, and use what you learn in one to inform the next.

**A. Problem Specification and Constraints.** What's the input (image, time-series,
graph, text, tabular, point cloud...)? What's the output (regression, classification,
generation, anomaly flag, control action)? What system constraints exist -- fixed bounds
like target hardware, power, latency ceiling, software version -- that are *not* being
optimized? If genuinely none, that's a valid answer; don't invent constraints. For an LLM
benchmark, the prompt format, few-shot count and answer format are part of the problem
specification (`references/llm-benchmarks.md`).

**B. Dataset.** Does it already exist, or does it need to be built? Push on each FAIR
principle concretely rather than accepting "yes, it's fine":
- *Findable*: is every instance uniquely identified?
- *Accessible*: hosted where, under what license, through what protocol?
- *Interoperable*: what format, and does it follow a community standard for this data?
- *Reusable*: is it versioned, and is the code that generated or preprocessed it public?

Then nail down the split: sizes, construction method (random / stratified / held out by
construction), and confirm non-overlap. If there's room for a held-out generalization set
distinct from the main test set (wa-hls4ml's "exemplar" set), ask if one makes sense.

Settle what `data.py` and `data/SCHEMA.md` will need. Answer these from **this** dataset,
not from defaults (details in `references/repo-structure.md`):
- **Sample IDs.** What uniquely identifies a sample within a split, and are there
  fallbacks? (axess: one subset had `model_id` instead of `uuid`.)
- **Ground truth and forbidden inputs.** Which field is the ground truth, and which fields
  are **not valid inputs** because they're labels or derived from them.
- **Missing or invalid ground truth.** Ask whether such samples are excluded, imputed, or
  scored as failures, and document the choice. Whatever the choice, report coverage.
- **Training filter vs scoring filter.** If anything reproduces upstream training, did
  upstream select training samples differently from how the benchmark scores? If so,
  keep both filters. (axess: 433,676 vs 433,674 train samples.)
- **Size and format.** Does the data fit in memory? Is preprocessing expensive enough to
  cache?

Two Genesis skills turn the FAIR answers into checkable artifacts
(`references/genesis-skills.md`):
- **Croissant metadata.** `croissant-validator` generates or validates `croissant.json`.
  If the dataset is on Hugging Face, validate the Hub's Croissant metadata rather than
  writing a second one.
- **Data card.** For DOE/Genesis work, `datacard-generator` writes the Genesis data card
  (see "Additional deliverables").

**C. Performance Metric(s).** What's actually being measured, and does it capture what
matters, not just what's easy to compute? This category has two sub-scales, not a flat
checklist (`references/ontology.md`). Push past "we'll use accuracy" to:
- the exact formula;
- edge cases (division by zero, empty predictions, unparseable answers);
- per-class/per-target vs aggregated;
- whether one metric is enough, or this is a multi-dimensional/Pareto benchmark (e.g.
  accuracy under a latency bound).

**Check that published numbers reproduce with the *stated* formula.** When a paper or
README reports results:
1. Recompute at least one published table cell from raw predictions, using the formula
   exactly as documented.
2. If it doesn't match, find the variant that does, then ask the user which one the
   benchmark defines. Document the discrepancy either way.
3. Look for internal-consistency failures visible without code: a value that contradicts
   another column, or an aggregate row that can't be reconciled with its subgroups.

axess's paper states SMAPE with ε = 1, but its numbers only reproduce with ε = 1e-8. Its
dense DSP R² is printed as −0.74 while its own RMSE implies −111.74. The benchmark
implements the stated ε = 1 and documents all three findings in its `docs/VALIDATION.md`.

**Metric choice must follow from the benchmark's own AI/ML motif; there is no default
suite.** Check the motif against the "What metrics do comparable existing benchmarks
actually use?" table in `references/ontology.md` Part 3. Anchor the conversation in what
similar real benchmarks measure (stability loss + control latency for RL, log-P/docking
scores for molecule generation, ROC-AUC + precision/recall for anomaly detection), then
check whether that fits this benchmark's specific question. `scripts/metrics.py` covers
two families only:
- regression: `r_squared`, `smape`, `rmse`, `mae`, `relative_l2_error`,
  `relative_percent_error`, `plot_rpe_boxplot`;
- classification and anomaly detection: `classification_report`, `roc_auc`.

Offer those only when the task genuinely is regression or classification, and pick the
function that fits (their docstrings say when). For every other motif, say plainly that it
needs bespoke metric code, and write it fresh. LLM benchmarks get their metrics from the
lm-eval task (`references/llm-benchmarks.md`). A metric that doesn't fit its task loses
Metric Quality credit however well it's implemented.

Two more checks, both detailed in `references/metrics-and-uq.md`:
- **Independent recomputation.** For regression or classification, recompute the
  reference model's metrics with the `uq-metrics-evaluator` skill as a second
  implementation of `score.py`, and record agreement in `docs/VALIDATION.md`.
- **Uncertainty.** If a reference model outputs uncertainties or class probabilities, ask
  whether calibration belongs in the benchmark's metrics (ECE, Brier, NLL, miscalibration
  area). If its confidence drives decisions, offer the `uncertainty-quantification` audit.

**D. Reference Solution.** Is there already a working method, or does one need to be
built or chosen as the baseline? It needs public code, full documentation (architecture,
hyperparameters, training procedure), listed hardware/software requirements, and every
metric from element C actually evaluated and reported for it. More than one reference
solution (a simple baseline plus a stronger one, as in wa-hls4ml's MLP/GNN/Transformer
trio) strengthens the benchmark but isn't required.

**Ask: "Does the benchmark evaluate only predictions from given or pretrained models, or
does it also train or reproduce training?"** Don't assume either way. Score-only was
axess-benchmark's choice, not a rule. The answer shapes the repo
(`references/repo-structure.md`, "Score-only vs includes training"): score-only has no
`train.py` and takes weights from `weights/MANIFEST.json`; including training adds
`train.py`, training jobs and training-reproduction checks. It also feeds the Codabench
mode decision later. The `predict → score_all.sh` contract is the same either way.

**Verify the reference solution before building anything on it.** Read
`references/reference-solution-checks.md` and run every check. Results go in
`docs/VALIDATION.md`. In short:
1. identity and weights (strict loading, sha256, where the weights really live);
2. training label vs scored label, checked on data;
3. the whole inference procedure (preprocessing, derived statistics, post-processing);
4. per-sample agreement with upstream, then golden outputs on fixtures;
5. reference vs auxiliary models.

For an LLM benchmark, these take the form in `references/llm-benchmarks.md`: model
identity and revision, the answer key, the whole prompt-to-answer procedure, a full
(not sample-limited) run, and a weak control model.

**E. Documentation and Reproducible Protocol.** Can someone outside the team reproduce the
reference solution's numbers from a clean environment? This means numbered reproduction
steps, a pinned or containerized environment, and prose explaining motivation and
scientific background -- not just API docs. If there's no paper yet, say so; that's one
specific gap (Documentation, "an academic paper about the benchmark exists"), not a vague
weakness.

**Ask which machine(s) the benchmark will run on**: a laptop, a workstation, or which
cluster(s). Don't assume Perlmutter or any other site. **As soon as the user names a
cluster, load its genesis HPC skill** (`perlmutter`, `frontier` or `aurora`, plus `slurm`
or `pbs` for the scheduler; latest version, `references/genesis-skills.md`). Use it to
pre-fill the machine profile, then ask only what it doesn't answer
(`references/hpc.md`, "What to ask per machine"). Generate the generic Slurm or PBS
templates, with one machine profile each.

For citations:
- Prefer the published DOI over the preprint once one exists.
- Fetch the metadata from `https://doi.org/<doi>` with `Accept: application/x-bibtex`
  rather than typing it in.
- When citing sections and equations, check the numbering against the published version.

Also ask about **motif tagging** while you're here (`references/ontology.md` Part 3):
scientific domain(s) and exactly one AI/ML motif. It's not rubric-scored, but it's what
makes the benchmark findable in the ontology's terms.

## Build the artifacts

As the interview answers each element, generate the real files. Don't wait until the end
to write everything at once, since later answers often reveal that earlier files need
revising.

**Propose the recommended repository structure by default, and explain why.** It's
specified piece by piece in `references/repo-structure.md`, generalized from
axess-benchmark. In summary:

```
<repo>/
├── README.md, SUBMISSION.md, CITATION.cff, LICENSE, rubric.yaml, SCORE_REPORT.md
├── pyproject.toml, requirements*.txt (one per stack that must stay separate), .gitattributes
├── data/SCHEMA.md, [data/croissant.json]
├── docs/VALIDATION.md, docs/<MACHINE>.md
├── reference_solution/README.md          documentation only
├── reference_results/                    committed LEADERBOARD.md + <split>/<model>/metrics
├── weights/MANIFEST.json (+ small derived artifacts)
├── src/<pkg>/  data, cache, [features, stats], models/, [train], predict, truth, score, report, submission
├── scripts/    fetch_data.py, fetch_weights.py, score_all.sh
├── [tasks/<task>/]                       LLM benchmarks: the lm-eval task
├── <hpc>/      (optional) generic Slurm or PBS, tuned per machine
├── codabench/  (optional) README, build_bundle.py, bundle_src/
└── tests/      score, golden pipeline, [features equivalence], submission, fixtures/
```

Every benchmark's run follows the same **pipeline contract**:

```
fetch_data → [cache] → [train] → predict (per model, per split) → score_all.sh (truth, score, leaderboard, submissions)
```

The conventions:
- `<results>/<split>/predictions_<model>.<ext>` (all samples);
- `truth.<ext>` (scored samples only);
- `<model>/metrics.json` and `LEADERBOARD.md`;
- `codabench/<model>_submission.zip`.

For per-sample tasks the default prediction file is a CSV of `sample_id` plus one column
per output. For LLM benchmarks, `predict` is a full lm-eval run whose per-sample answers
are exported to that same CSV (`references/llm-benchmarks.md`). Tasks with other outputs
define their own artifact (`references/repo-structure.md`). A participant's model plugs
in by writing its prediction files; nothing else changes. Tell the user that in those
words.

**Decide the contents per benchmark.** The structure is generic; the code inside it isn't.
Data reading, missing-truth handling, metrics, preprocessing, stack workarounds, test
tolerances and job sizes all come from this benchmark's interview answers and
measurements. axess's choices appear in the references only as labelled examples. A fix
found while building a benchmark goes into that benchmark's code and docs (e.g.
`<hpc>/stack.sh`, `docs/VALIDATION.md`), never into this skill's templates.

**Generate the tree; don't copy a skeleton.** Which optional pieces exist, which models,
splits and targets there are, whether there's training, and which machines and submission
mode apply all vary per benchmark. Build each file from its contract in
`references/repo-structure.md`, adapting the snippets in `assets/repo/`, `assets/hpc/`
and `assets/codabench/` where they fit.

**The structure is recommended strongly, but it's not required.** When you propose it,
explain what it buys:
- one uniform pipeline for every model;
- participants plug in by writing their prediction files;
- golden tests make a new machine verifiable before any job runs;
- Codabench submissions and the bundle come out of the same truth function, so they can't
  drift from the benchmark.

If the user wants a different layout, or existing working code makes a reorganization
cost more than it buys, deviate. Keep the pipeline contract even then, and note the
deviation in the README.

## Score against the rubric

1. Copy `assets/rubric_template.yaml` into the benchmark's own directory (e.g.
   `rubric.yaml`) so it lives alongside what it's scoring and can be re-run later.
2. Fill in every item with `met: true` or `met: false` plus a one-line `evidence:`
   pointing at the specific file/section that justifies it. For genuinely ambiguous
   judgment calls ("well documented," "task is clear"), make the call but say why in the
   evidence field -- and when you're really unsure, ask the user rather than defaulting to
   a generous score. An inflated self-score is a disservice to anyone who later relies on
   it, including the user if they submit for actual MLCommons endorsement.
3. For **Performance Metrics**, set `definition_level` (0-3) and `quality_level` (0-2) per
   the level descriptions in `references/ontology.md`. This category doesn't use a flat
   checklist, so don't force it into one.
4. Run the scorer:
   ```bash
   python scripts/score_benchmark.py path/to/rubric.yaml --out SCORE_REPORT.md
   ```
   It refuses to score any category with unanswered items rather than silently treating a
   blank as false. If it errors, it's telling you which items still need an answer.
5. Present the report: overall score, whether it clears the 4.5 endorsement threshold, and
   the gap list. Prioritize fixes for the categories closest to their next whole point, or
   whichever single unmet item is cheapest to close -- a missing environment.yml is
   usually faster to fix than "write an academic paper about the benchmark."

## Iterate

After presenting the score, ask whether to act on any of the gaps now. Re-run the scorer
after each fix so the user sees the number move. Stop when the user is satisfied; they
may not need or want 5/5 on every category. That's their call, not a target to impose.

**Keep the self-score honest over time.** Whenever a verified fact changes, re-read
**every** `evidence:` string in `rubric.yaml`, not just the item you were working on:
- a dataset gets published;
- a cluster run completes;
- a reference model is replaced;
- a published table turns out not to reproduce.

In axess, "HF repo pending", "not yet on Perlmutter" and "paper Table 4 reproduced" all
went stale this way without the score changing. Keep the `notes:` block as dated caveats
("re-scored 2026-10-02 after ..."). `scripts/score_benchmark.py` lists any evidence using
provisional wording ("pending", "not yet", "TODO", "will be") under "Evidence to re-check".
Resolve each one, or confirm it's still true.

## Additional deliverables

Each is separate from the benchmark package and optional unless the user needs it. Read
its reference in full first; the steps are there.

- **MLCommons corpus entry** (`references/mlcommons-corpus-format.md`, "Step by step").
  Generate it once the benchmark and its rubric score exist: a single YAML entry for the
  public corpus at https://mlcommons-science.github.io/benchmark/. Start from
  `assets/mlcommons_corpus_entry_template.yaml`, ask about `url` and `contact` rather than
  assuming, set `valid`/`reproducible`/`benchmark_ready` only if verified, and validate
  with `python scripts/validate_corpus_entry.py <entry.yaml>`.
- **DOE GEAR / Genesis cards** (`references/doe-gear-cards.md`). Offer these when the
  reference solution is a model or agentic system, or the user works under a
  DOE/Genesis Mission RFA. Ask which cards apply. Model and Agent Card templates are
  fetched live. The Data Card comes from the `datacard-generator` skill. A Model Card's
  evaluation results are written by script, never retyped:
  - `card-eval-updater` for LLM benchmarks;
  - `scripts/render_card_results.py` from `metrics.json` for everything else.

- **AmSC MLflow tracking** (optional; the `amsc-mlflow` skill, `references/genesis-skills.md`).
  Offer it to Genesis/AmSC users:
  - log `reference_results/` with its `log_benchmark_results.py` (dry run first) and record
    the run ID in `docs/VALIDATION.md`;
  - register reference weights from `weights/MANIFEST.json` as `staging`, and move
    `production` only after verification, with the user's go-ahead;
  - track training runs from cluster jobs with rank-0 logging.

  The user sets their MyAmSC token themselves. Never ask for it.

## Package for Codabench

If the user wants participants to submit against the benchmark, package it as a Codabench
competition bundle. This is a separate, later phase. Only start once the standalone
benchmark exists (dataset, metrics, reference solution, docs); a bundle without those
behind it is an empty shell. Read `references/codabench-workflow.md` (the steps) and
`references/codabench.md` (the formats) in full first. The decisions that shape it:

1. **Code submission vs results submission.** Ask; it decides whether an
   `ingestion_program/` exists. Score-only with public ground truth points to a results
   submission (axess's choice). A benchmark that evaluates training or a method, or has
   hidden data, points to a code submission. LLM benchmarks are usually results
   submissions of per-sample answers.
2. **Build the bundle from the benchmark, never by hand.** `codabench/build_bundle.py`
   generates hidden truth, scored IDs, the solution and sample submissions from **the same
   truth function the benchmark uses**. `score_all.sh` already writes an upload-ready
   `<model>_submission.zip` for every model.
3. **Rank on a bounded, primary-split metric** (leaderboard column 0). Never on a metric
   unbounded below, such as R² on an out-of-distribution split.
4. **Never author real participation terms.** Generate an obviously-marked placeholder and
   say it must be replaced before going live.
5. **Get explicit confirmation before any `docker push`**, every time.
6. **Validate and report real numbers.** Run `scripts/validate_codabench_bundle.py` (tiers
   1-3 always; tier 4 with `--docker` when Docker is available) on the sample submission,
   every pipeline zip and deliberately malformed zips. Then report the reference vs
   weak-baseline scores (the discrimination check) and record everything in
   `codabench/README.md`.
