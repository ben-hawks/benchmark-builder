---
name: benchmark-builder
description: Walks a user through designing, structuring, documenting, and self-scoring a scientific ML benchmark that conforms to the MLCommons Science Benchmarks Ontology (five-element benchmark definition, six-category/27-point rating rubric, arXiv:2511.05614) and, once built, packaging it as a Codabench competition bundle with a validated example submission. Use whenever the user wants to build, formalize, publish, or clean up a benchmark, dataset+task+metric suite, or reproducibility package -- even if they never say "MLCommons," "ontology," or "Codabench" explicitly. Trigger on requests like "turn my model comparison into a proper benchmark," "structure this repo so others can reproduce our results," "grade how good our benchmark documentation is," or "make this a Codabench competition." Also use it to self-score an EXISTING benchmark, validate an existing Codabench bundle, generate an MLCommons corpus entry YAML for a benchmark that already exists, or produce a DOE GEAR Model/Agent/Dataset card for a benchmark's reference solution or dataset.
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

**Before doing anything else, read `references/ontology.md` in full.** It has the exact
wording of all five definitional elements and all six rubric categories -- you need the
precise wording, not a paraphrase, both to interview well and to score correctly later.
If the user's project resembles hls4ml/FPGA resource estimation, HEP, or another
regression-heavy scientific ML surrogate-modeling task, also skim
`references/wa-hls4ml-example.md` -- it's a real benchmark scored against this exact
rubric, and shows what a complete answer to each element actually looks like in practice
(down to how they handled a SMAPE division-by-zero edge case). Even outside that domain,
its "required / strongly recommended / suggested" submission-guidelines pattern and its
closing point about documenting known limitations rather than hiding them are worth
reusing directly.

Once the standalone benchmark and its rubric score exist, also generate an MLCommons
corpus entry (a separate, single-YAML-file deliverable for the real public corpus at
https://mlcommons-science.github.io/benchmark/) -- see "Generate an MLCommons corpus
entry" below and read `references/mlcommons-corpus-format.md` in full before touching it.

If the user is working under a DOE/Genesis Mission RFA, or the reference solution is a
model or agentic system, also offer a DOE GEAR Model/Agent/Dataset card -- a separate,
optional deliverable from the corpus entry above -- see "Generate DOE GEAR xCards" below
and read `references/doe-gear-cards.md` in full before touching it; that doc explains why
its templates must be fetched live rather than reused from a cached description.

If the user wants the benchmark packaged for Codabench (upload-ready, participants can
submit against it), that's a separate, later phase -- see "Adapt into a Codabench
Competition Bundle" near the end of this file, and read `references/codabench.md` in
full before touching any Codabench-specific file. Don't jump to it before the standalone
benchmark (the five elements above) actually exists; a Codabench bundle without a real
dataset/metrics/reference-solution behind it is just an empty shell.

## Gather artifacts before interviewing

Don't open with a blank interview -- most of the five elements are usually already
answered somewhere: a paper, a repo, a dataset sample, a README, a training script.
Asking questions the materials already answer wastes the user's time and risks getting a
worse answer than what's actually written down (`references/wa-hls4ml-example.md` was
built entirely this way -- by reading the paper and repo, not by interviewing anyone).
Do this, in order, before asking a single interview question:

1. **Check what's already in front of you first.** Look at files already attached to the
   conversation or already read this session, and the working directory/repo itself -- a
   quick `Glob`/`ls` for likely candidates (PDFs, READMEs, notebooks, a `data/` or `src/`
   directory, existing dataset files, prior benchmark writeups) costs nothing and often
   finds most of what's needed without asking anyone. If the user's request names or
   paths to a repo, paper, or dataset, go read it before asking them anything about its
   contents.
2. **Ask for what's missing, once, before the interview starts.** Report what you found
   (briefly -- a list, not an essay) and ask for anything relevant you don't already
   have: a paper or writeup, the code (repo path, or pasted snippets if there's no full
   repo), a dataset sample, prior results it should be compared against. Be specific
   about what would close which element ("a link to the training code would answer the
   Reference Solution and Software Environment questions") rather than a generic "send
   me everything" -- a targeted ask gets a faster, more complete answer.
3. **Extract a draft answer for each of the five elements from what you have.** Read the
   paper/code/data the way `references/wa-hls4ml-example.md` does, and write down --
   with evidence (file, section, line) -- what you can determine for Problem
   Specification, Dataset, Performance Metrics, Reference Solution, and Documentation.
   Don't guess past what the material actually supports; an element the source material
   genuinely doesn't address is a real gap to interview for, not something to infer
   generously just because it would complete the picture.
4. **Carry the draft into the interview and treat it as confirmation, not a cold
   start.** Show the user what you found per element ("here's what I found for the
   dataset splits -- still current?") and ask real questions only for what the material
   left undetermined or ambiguous. This is almost always faster than a full interview,
   and the confirmation step catches stale material (a README describing a dataset
   version that's since changed) before it propagates into the benchmark card.

If the user genuinely has nothing yet -- an idea with no code or data behind it -- step 3
will come up empty and the interview below becomes the full original interview. That's
fine; the point of this pass isn't to force extraction, it's to never ask for something
that's already sitting in front of you.

## Figure out which mode you're in

By the time artifacts are gathered, you'll usually already know which of these the user
wants -- confirm rather than asking cold:

1. **New benchmark from scratch.** Little or nothing existed before this conversation;
   the artifact pass came up mostly empty. The interview below runs close to its full,
   original form.
2. **Formalize an existing project.** Code/data/results already exist, just not
   organized or documented as a benchmark. The artifact pass should already have mapped
   most of the five elements -- confirm the draft, interview only real gaps.
3. **Score/audit an existing benchmark.** They want to know how it rates, not build
   anything new yet. Skip to "Score against the rubric" once the artifact pass has given
   you enough evidence per rubric item -- an un-evidenced score is worse than no score,
   because it's false confidence.

Modes 2 and 3 often turn into mode 1 output (fill the gaps, write the missing pieces)
once the gaps are visible -- treat this as one continuous workflow, not three separate
ones.

## Interview (confirm the draft, fill the gaps)

Work through the five elements in order; each maps directly to one or more rubric
categories, so getting them right here is what makes the later score legitimate rather
than generous. Where the artifact pass above drafted an answer for an element, lead with
it ("looks like the dataset is already split 80/10/10 by X -- still right?") instead of
asking the underlying question cold; ask the full question only where nothing was
extracted. Don't dump all five as a giant questionnaire regardless -- work through them
conversationally, and use what you learn in one to inform the next (e.g. the task
description in "Problem Specification" should directly determine what a valid metric in
"Performance Metrics" even means).

**A. Problem Specification and Constraints.** What's the input (representation: image,
time-series, graph, text, tabular, point cloud...)? What's the output (the
transformation: regression, classification, generation, anomaly flag, control action)?
What system constraints exist -- fixed bounds like target hardware, power, latency
ceiling, software version -- that are *not* being optimized? If genuinely none, that's a
valid answer; don't invent constraints to fill the section.

**B. Dataset.** Does it already exist, or does it need to be built/collected? Push on
each FAIR principle concretely rather than accepting "yes, it's fine": *Findable* --
is every instance uniquely identified? *Accessible* -- hosted where, under what
license, through what protocol? *Interoperable* -- what format, and does it follow a
community standard for this kind of data? *Reusable* -- is it versioned, and is the
code that generated/preprocessed it also public? Then nail down the split: sizes,
construction method (random / stratified / held out by construction), and confirm
non-overlap. If there's room for a held-out generalization set distinct from the main
test set (wa-hls4ml's "exemplar" set is a good model for this), ask if one makes sense.

**C. Performance Metric(s).** What's actually being measured, and does it capture what
matters, not just what's easy to compute? This is the rubric category with the most
nuance (two sub-scales, not a flat checklist -- see `references/ontology.md`), so push
past "we'll use accuracy" to: exact formula, how ties/edge-cases are handled (division
by zero, empty predictions), whether it's computed per-class/per-target or aggregated,
and whether one metric is enough or this is really a multi-dimensional/Pareto benchmark
(e.g. accuracy under a latency bound).

**Metric choice must follow from the benchmark's own AI/ML motif -- there is no default
metric suite to reach for.** Before suggesting anything, check the motif you tagged in
element B against the "What metrics do comparable existing benchmarks actually use?"
table in `references/ontology.md` Part 3, and anchor the conversation in what similar
real benchmarks measure for that motif (e.g. stability loss + control-latency for RL,
log-P/docking scores for molecule generation, ROC-AUC + precision/recall for anomaly
detection) -- then check whether that actually fits this benchmark's specific question
rather than adopting it wholesale. `scripts/metrics.py` only implements two families:
regression (r_squared, smape, rmse, mae, relative_l2_error, relative_percent_error +
plot_rpe_boxplot) and classification/anomaly detection (classification_report, roc_auc).
Offer those *only* when the task is genuinely regression or classification, pick the
specific function that fits (mae and relative_l2_error are real alternatives to rmse, not
lesser options -- see their docstrings for when each is more appropriate), and for every
other motif -- generative, RL/control, multimodal reasoning, and anything else the table
doesn't cover with a ready-made function -- say plainly that this needs bespoke metric
code, and write it fresh rather than forcing a mismatched metric onto the task. A
benchmark whose metric doesn't fit its task loses Metric Quality credit no matter how
well-implemented the metric is.

**D. Reference Solution.** Is there already a working method, or does one need to be
built/chosen as the baseline? It needs: public code, full documentation (architecture,
hyperparameters, training procedure for a model), listed hardware/software
requirements, and every metric from element C actually evaluated and reported for it.
More than one reference solution (a simple baseline plus a stronger one, as in
wa-hls4ml's MLP/GNN/Transformer trio) strengthens the benchmark but isn't required.

**E. Documentation and Reproducible Protocol.** Can someone outside the team actually
reproduce the reference solution's numbers from a clean environment? This means
numbered reproduction steps, a pinned/containerized environment, and prose explaining
motivation and scientific background -- not just API docs. If there's no paper yet,
say so; that's one specific, nameable gap (Documentation category, "an academic paper
about the benchmark exists") rather than a vague documentation weakness.

Also ask about **motif tagging** while you're here (see `references/ontology.md` Part
3) -- scientific domain(s) and exactly one AI/ML motif. It's not rubric-scored, but it's
what makes the benchmark findable in the ontology's own terms, and it's a five-second
question now versus an afterthought later.

## Build the artifacts

As the interview answers each element, generate the real files -- don't wait until the
end to write everything at once, since later answers often reveal earlier files need a
revision. A minimal, complete layout:

```
<benchmark-name>/
├── README.md                    # from assets/benchmark_card_template.md
├── data/                        # or a documented pointer to externally-hosted data
│   └── SCHEMA.md                # per-field documentation of a sample
├── reference_solution/
│   ├── README.md                # architecture/method, hyperparameters, requirements
│   └── ...                      # actual code
├── metrics/
│   └── score.py                 # adapted from scripts/metrics.py for this benchmark's targets
├── environment.yml / requirements.txt / Dockerfile
└── SUBMISSION.md                # from assets/submission_report_template.md
```

Adapt this to what the artifact pass found rather than forcing a rewrite -- when
substantial code/data already existed, prefer adding the missing pieces (a schema doc, a
metrics script, a benchmark card) over restructuring code that already works. A benchmark
that scores well without a disruptive reorg is a better outcome than one that scores well
after breaking everyone's existing workflows.

## Score against the rubric

1. Copy `assets/rubric_template.yaml` into the benchmark's own directory (e.g.
   `rubric.yaml`) so it lives alongside what it's scoring and can be re-run later.
2. Fill in every item with `met: true` or `met: false` plus a one-line `evidence:`
   pointing at the specific file/section that justifies it. For genuinely ambiguous
   judgment calls ("well documented," "task is clear"), make the call but say why in the
   evidence field -- and when you're really unsure, ask the user rather than defaulting
   to a generous score. An inflated self-score is a disservice to anyone who later relies
   on it, including the user if they submit for actual MLCommons endorsement.
3. For **Performance Metrics**, set `definition_level` (0-3) and `quality_level` (0-2)
   per the level descriptions in `references/ontology.md` -- this category doesn't use
   a flat checklist, so don't try to force it into one.
4. Run the scorer:
   ```bash
   python scripts/score_benchmark.py path/to/rubric.yaml --out SCORE_REPORT.md
   ```
   It refuses to score any category with unanswered items rather than silently treating
   a blank as false -- if it errors, that's telling you exactly which items still need
   an answer, not a bug to work around.
5. Present the report to the user: overall score, whether it clears the 4.5 endorsement
   threshold, and the gap list. Prioritize suggesting fixes for the categories closest to
   their next whole point, or for whichever single unmet item is cheapest to actually
   close -- a missing environment.yml is usually faster to fix than "write an academic
   paper about the benchmark."

## Iterate

After presenting the score, ask whether to act on any of the gaps now. Re-run the
scorer after each fix so the user sees the number move -- that feedback loop is more
convincing than a wall of remaining TODOs. Stop when the user is satisfied with the
score (they may not need or want 5/5 or endorsement-level on every category -- that's
their call, not a target to impose).

## Generate an MLCommons corpus entry

Once the standalone benchmark and its rubric score both exist, also generate
a corpus entry — a single YAML file meant to be appended to the real
MLCommons Science Benchmarks corpus (https://mlcommons-science.github.io/benchmark/),
not part of the benchmark package's own structure. Read
`references/mlcommons-corpus-format.md` in full first; it has the exact
field-by-field mapping from what you already built onto this separate schema,
including two real ambiguities in the source schema itself and one real
schema-vs-practice mismatch found by testing this skill's validator against
an actual cataloged entry (don't rediscover these by guessing — they're
documented).

1. **Start from `assets/mlcommons_corpus_entry_template.yaml`.** Most fields
   map directly from work already done — the reference doc's table says
   exactly where each one comes from (rubric.yaml's six scores map 1:1 onto
   `ratings`, no rescaling needed). A few fields (`keywords`,
   `ai_capability_measured`, `ml_task`) aren't collected anywhere else in this
   skill's workflow — synthesize them from what you already know rather than
   leaving them blank, but say plainly that they're a synthesis, not a fact
   pulled from a source.
2. **Pick `name` with its downstream URL in mind.** The published corpus
   derives each entry's page URL from `name` automatically — there's no
   separate `id`/`slug` field to set. The exact derivation lives in the
   upstream repo's own code and can change, so per "How `name` becomes the
   entry's published URL" in `references/mlcommons-corpus-format.md`, fetch
   it fresh rather than trusting a paraphrase before finalizing `name`.
3. **Ask about `url` and `contact` rather than assuming.** If this is a
   formalized existing benchmark (not built from scratch), the reference
   doc's "The url decision" section explains why this is a real, unresolved
   choice between the upstream project and the newly-formalized package --
   ask the user. Similarly, never default to listing the user's own contact
   info without asking first.
4. **Only set `valid: true` / `fair.reproducible: true` / `fair.benchmark_ready: true`
   if actually verified**, the same bar this skill already applies everywhere
   else -- these are booleans per the documented schema (a real cataloged
   entry using strings instead is a known, documented mismatch to not repeat).
5. **Validate before calling it done**:
   ```bash
   python scripts/validate_corpus_entry.py <entry.yaml>
   ```
   Fix everything it flags as an error; warnings (e.g. the deprecated
   `solutions` field, or `ml_motif` diverging from `task_types`) are judgment
   calls to consider, not blockers.
6. **If the entry is actually headed upstream as a PR**, fetch and follow the
   upstream repo's own `CONTRIBUTING.md` and `docs/benchmark-format.md`
   live rather than relying on any paraphrase of them — see
   `references/mlcommons-corpus-format.md`'s "If this entry is headed
   upstream" section for exactly which files and why this is a live
   dependency, not baked-in fact.

## Generate DOE GEAR xCards (optional)

A separate, optional deliverable from the MLCommons corpus entry above: DOE's
GEAR platform (Genesis Mission) defines its own short-form Model Card, Agent
Card, and Dataset/Data Card conventions. Offer these when the reference
solution is a model or agentic system, or the user is working under a
DOE/Genesis Mission RFA that expects them. Read `references/doe-gear-cards.md`
in full first.

1. **Ask which card(s) apply** — Model Card (element D is a trained model),
   Agent Card (element D, or the benchmark's own task, is an agentic system),
   and/or Dataset/Data Card (element B) — rather than assuming all three.
2. **Fetch the current landing page and its linked template/examples live**
   for each card that applies, per `references/doe-gear-cards.md`'s table —
   these are DOE-maintained pages this skill has no schema for and no way to
   keep in sync, so never draft a card from memory of a prior fetch in this
   same conversation if meaningful time has passed, and never from this
   skill's own paraphrase of what the template contains.
3. **Map from what this skill already built**, per "How this fits what this
   skill already built" in the reference doc — element D for Model/Agent
   Card, element B for Dataset/Data Card — rather than re-running the
   interview. Match the live template's actual section headers; don't impose
   a structure of your own.
4. **Save each as its own file** (e.g. `MODEL_CARD.md`, `AGENT_CARD.md`,
   `DATA_CARD.md`) alongside the benchmark card, and mention the
   data-card-generator/tool-card tooling the FAIR page links to if the user
   wants automated generation instead.

## Adapt into a Codabench Competition Bundle

Only start this once the standalone benchmark exists (dataset, metrics, reference
solution, docs) -- this phase reuses that work, it doesn't replace it. Read
`references/codabench.md` in full first; it's grounded in a real, verified Codabench
example bundle (not just the docs prose, which turned out to have gaps against actual
behavior), and has the exact directory/file contracts this step depends on. Skim
`assets/codabench/example_bundle/` alongside it -- a complete, self-tested worked
example to pattern-match against, the Codabench equivalent of
`references/wa-hls4ml-example.md`.

1. **Decide code submission vs. results submission** (see `references/codabench.md`'s
   "big design decision" section) -- ask the user rather than assuming. This changes
   whether an `ingestion_program/` exists at all, so it has to be settled before
   generating anything.
2. **Derive what's already known** from the standalone benchmark -- don't ask for any
   of this again: dataset splits (→ per-phase `input_data`/`reference_data`), metrics
   (→ `scoring_program/scoring.py`, adapted from whatever `scripts/metrics.py`-derived
   code the standalone benchmark already uses, plus leaderboard columns), the reference
   solution (→ `solution/`), and the benchmark card content (→ `pages/*.md`).
3. **Ask for what only the user can supply**, sorted by `references/codabench.md`'s
   "Required vs. optional" list -- title/logo/terms/phase-dates/submission-mode are
   real blockers, worth asking together in one pass; most of what's left has sane
   defaults, offer them and move on unless the user cares. **Never author real
   participation terms** -- generate an obviously-marked placeholder (see
   `assets/codabench/example_bundle/pages/terms_and_conditions.md` for the exact
   pattern) and say plainly that it must be replaced before the competition goes live.
4. **Decide the Docker image** using `references/codabench.md`'s "Docker image"
   section: check the reference solution's real dependency file against the stock-image
   table first -- most benchmarks need nothing custom. Only if a stock image doesn't
   cover it, write one from `assets/codabench/Dockerfile.template` (CPU) or
   `Dockerfile.gpu.template` (GPU) and save it as `Dockerfile` at the bundle root; the
   validator's tier 4 then builds and tests it automatically (all local and reversible,
   no confirmation needed -- see the next section). Get **explicit confirmation before
   `docker push`** -- publishing an image to a public registry is a publish action, not
   a default-and-forget step, and that confirmation is per-instance even if the user
   approved a push earlier in this same conversation. The validator never pushes.
5. **Generate the bundle** following the directory layout in `references/codabench.md`,
   vendoring any shared metric code into `scoring_program/` (and `ingestion_program/` if
   it needs any) rather than importing from outside the bundle -- both directories get
   zipped and uploaded independently, so anything they need must live inside them.
   Write `ingestion.py`/`scoring.py` using the `CODABENCH_ROOT` environment-variable
   convention (default `/app`, override for local testing) rather than hardcoding
   `/app` the way Codabench's own raw examples do -- this is what makes the next section
   possible without needing Docker.

## Build and validate an example submission bundle

Every Codabench competition bundle needs a submission a participant can look at and
run, and this doubles as the fastest way to prove the bundle actually works end to end.

1. **Reuse the reference solution as the example submission** -- zip it (root files
   only, no wrapping folder: `zipfile.ZipFile(...).write(path, arcname=filename)`, not a
   recursive directory zip) into `starting_kit/sample_submission.zip`, exactly like
   `assets/codabench/example_bundle/solution/model.py` becomes
   `starting_kit/sample_submission.zip`. If a weaker, more obviously-a-starting-point
   baseline would help participants more than handing them the full reference solution
   immediately, put that in `starting_kit/model.py` instead and keep the reference
   solution's zip as a separate "here's a working example" download -- both patterns
   are demonstrated in the example bundle.
2. **Validate with `scripts/validate_codabench_bundle.py`**:
   ```bash
   python scripts/validate_codabench_bundle.py <bundle_dir> --submission <sample_submission.zip> --task-index 0
   ```
   Read its own docstring for what each of its four tiers checks. Tiers 1-3 need no
   Docker and should always be run before calling a bundle finished. Fix whatever it
   flags -- a leaderboard column key that doesn't match `scores.json` is the single most
   common break, and tier 3 catches it by actually producing `scores.json` and diffing
   its keys against every configured column, not by guessing.

   **If Docker is available on this machine, run tier 4 as well** -- add `--docker`:
   ```bash
   python scripts/validate_codabench_bundle.py <bundle_dir> --submission <sample_submission.zip> --docker
   ```
   It builds the bundle's `Dockerfile` if it has one (otherwise uses/pulls
   `competition.yaml`'s `docker_image`), then runs the real ingestion and scoring
   programs inside the container against Codabench's actual `/app/...` layout. That's
   the only tier that catches "works on my machine, missing a dependency in the declared
   image" -- a class of failure tiers 1-3 structurally cannot see, since they run
   against the host's own Python. Check for Docker rather than assuming: the tier
   self-skips with the reason when the daemon isn't reachable, so just run it and read
   the output. Everything it does is local and reversible (build, pull, run, and
   `--rm-built-image` to clean up an image it built); it never pushes.
3. **Report the actual scores**, not just "validation passed" -- show the user the
   `scores.json` values the example submission produced, the same way the standalone
   benchmark's scoring step reports real numbers rather than a pass/fail flag. If the
   reference solution and a deliberately-weak baseline produce meaningfully different
   scores, that's good evidence the metric actually discriminates quality; if they don't,
   flag it as being worth checking before calling the bundle done.
