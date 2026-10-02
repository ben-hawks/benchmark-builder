# {{BENCHMARK_NAME}}

> One or two sentences: what does this benchmark measure, and why does it exist? A reader
> who has never heard of this task should know what they're looking at after this sentence.

**Scientific Motif(s):** {{e.g. High-Energy Physics}}
**AI/ML Motif:** {{e.g. Regression}}
**Computing Motif(s) (optional):** {{e.g. Latency Bound}}

This benchmark card follows the structure defined by the MLCommons Science Benchmarks
Ontology (arXiv:2511.05614) — see `references/ontology.md` in the benchmark-builder skill
for the full definition of each section below.

## Quick start

Copy-pasteable commands from a clean checkout to a leaderboard, for each supported
environment (local, and each cluster in `docs/<MACHINE>.md`). Follow the pipeline
contract (`references/repo-structure.md`):

```bash
# setup: envs, dataset (revision recorded), weights (sha256-checked)
# python -m pytest tests          # golden outputs before any full run
# featurize -> [train] -> predict -> bash scripts/score_all.sh
```

To score your own model, write `<results>/<split>/predictions_<name>.csv` (`sample_id` +
one column per target, every sample) for each split, then run `scripts/score_all.sh`. It
also writes your Codabench submission zip.

---

## 1. Problem Specification and Constraints

**Task.** What transformation is being asked for? State it as: given `<input
representation>`, produce `<output>`. Be concrete about representation (image / time-series
/ point cloud / graph / text / tabular / …) and about what "output" means (a label, a
regression target, a generated sample, a policy action, …).

**Inputs.** Exact format, shape, and any preprocessing assumed to already be applied.

**Outputs.** Exact format and shape of what a submission must produce.

**System constraints.** Fixed bounds a valid solution must satisfy that are *not* being
optimized (e.g. target hardware, power budget, latency ceiling, memory ceiling, software
version pins). If there are none, say so explicitly rather than leaving this blank —
"no constraints" is a valid but different answer from "unspecified."

---

## 2. Dataset

**Summary.** Size, source/provenance, and how it was generated or collected.

**Splits.** State the exact split sizes/counts and how they were constructed (random,
stratified, held-out-by-construction, etc.), and confirm they're non-overlapping.

| Split | Size | Purpose |
|---|---|---|
| Train | | |
| Validation | | |
| Test | | |
| (optional) Held-out generalization set | | |

**Schema.** Document every field/column in a sample, not just a link to "the data." If
samples are structured records (JSON/Parquet/etc.), list each top-level field and what it
contains.

**Access.** Where the dataset is hosted, under what license, and how it's versioned.

**FAIR checklist** (see `references/ontology.md` Part 2, Category 3):
- [ ] Findable — instances uniquely identified and documented
- [ ] Accessible — persistent, open access protocol
- [ ] Interoperable — community-standard formats/metadata
- [ ] Reusable — versioned, with the generation/preprocessing code public

**Bounded-ness.** State whether augmentation/enrichment of the dataset is permitted for
submissions (default: no, per the ontology's definition of a stable comparison target).

---

## 3. Performance Metric(s)

List every metric, fully defined (formula, not just a name), including how edge cases
(division by zero, empty predictions, ties, etc.) are handled. If there are multiple
targets, state whether metrics are computed per-target, aggregated, or both.

| Metric | Formula / definition | What it captures | Computed on |
|---|---|---|---|
| | | | |

If this is a multi-dimensional (Pareto) benchmark — e.g. accuracy under a fixed latency
bound — say so explicitly and explain how the dimensions relate (which are metrics being
optimized vs. constraints being satisfied).

---

## 4. Reference Solution

**Summary.** What is the reference solution (model/method), and where does its code live?

**Architecture / method.** Enough detail that someone could reimplement it without reading
the code — for a model, this typically means layer structure, hyperparameters, training
procedure, and compute used to train it.

**Results.** The reference solution's own scores on every metric defined above, on every
split they're computed on. This is what a new submission gets compared against. Copy the
table from the committed `reference_results/LEADERBOARD.md`, and state the run's date
and hardware. Mark auxiliary comparison models (not reference solutions) in italics with
"(auxiliary)". Follow it with a short "how to read this" paragraph.

**Verification.** One line per reference model on how its inference path was verified
(per-sample agreement with upstream, golden tests), linking `docs/VALIDATION.md`.

**Requirements.** Hardware and software needed to run the reference solution.

---

## 5. Documentation and Reproducible Protocol

**Reproduction steps.** Numbered, copy-pasteable steps from a clean environment to
reproducing the reference solution's reported numbers.

**Environment.** Containerized (link the image/Dockerfile) or an explicit, versioned
dependency list plus setup instructions.

**Motivation.** Why does this benchmark need to exist — what gap does it fill, and who
is it for?

**Background.** The scientific/domain context a non-specialist needs to understand why the
task matters.

**Known limitations.** Name them: distribution gaps, missing ground truth and its
coverage, inputs the task leaves out, published results that don't reproduce and why,
documented fallbacks. A named limitation is worth more than silence about it.

**Citation.** How to cite this benchmark (paper, if one exists; otherwise a preferred
citation for the dataset/code). Point to `CITATION.cff`. Use the published DOI once it
exists, with metadata fetched from doi.org.

**License.** State the code license and the dataset license separately; they usually
differ.

---

## Submission Guidelines

> See `assets/submission_report_template.md` for the report format a new submission to this
> benchmark should follow.
