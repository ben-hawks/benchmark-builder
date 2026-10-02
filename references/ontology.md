# The MLCommons Science Benchmarks Ontology

Source: Hawks et al., "An MLCommons Scientific Benchmarks Ontology," arXiv:2511.05614
(companion effort to the MLCommons Science Working Group, https://mlcommons-science.github.io/benchmark/)

This is the condensed, load-bearing content of that paper: the definition of what a
benchmark *is* (Section II) and the rubric used to score how good one *is* (Section III),
plus the domain/task taxonomy (Section IV) used to classify a benchmark. Read this file
in full before interviewing a user or scoring a benchmark — the rubric wording matters,
because the scoring script and the user both depend on you applying it consistently.

## Why this exists

Scientific ML benchmarking is fragmented: siloed efforts, datasets without concrete tasks,
non-reproducible code, undefined metrics. The ontology's job is to give every benchmark a
common skeleton (five elements) and a common yardstick (six rated categories) so that
different stakeholders — ML practitioners, domain scientists, hardware vendors — can find
and trust benchmarks outside their own subfield. A benchmark that nails all five elements
and scores well on the rubric is legible to *all three* of those audiences at once; that's
the actual goal, not rubric-maximizing for its own sake.

## Part 1 — The five definitional elements of a benchmark

A benchmark is "a carefully defined standardized version of a scientific application that
is used for making quantifiable comparisons of solutions." It has five required parts:

### A. Problem Specification and Constraints
A succinct statement of the benchmark **task**: what the input data is (origin/representation
— image, time-series, point cloud, text, graph, etc.), what the expected output is (the
transformation — regression, classification, anomaly detection, generation, etc.), and any
**system constraints**. Constraints are quantifiable bounds (power, latency, throughput) or
system specs (hardware platform, technology node) that are NOT part of the performance
metric being optimized — they're a fixed bound the solution must satisfy, not a thing being
maximized/minimized.

### B. Dataset
The scaffolding of input data (and truth labels, if applicable). Must follow **FAIR**:
- **Findable** — each instance uniquely identified and documented
- **Accessible** — persistent, open protocols for access
- **Interoperable** — formats/metadata follow community standards
- **Reusable** — versioned, with preprocessing scripts, enabling full reproducibility

The dataset is **bounded**: no augmentation, enrichment, or post-hoc curation unless the
benchmark explicitly allows it — a stable target is the point. A canonical, non-overlapping
train/validation/test split must be provided.

### C. Performance Metric(s)
Quantifiable measures for comparison, distinct from constraints (constraints are fixed
bounds; metrics are what's being optimized/compared). A benchmark can be multi-dimensional
(Pareto: e.g. accuracy AND latency). Metrics must be well-defined, reproducible, and
computable from the validation/test dataset. The same dataset can support multiple
benchmarks if they impose different metrics/constraints (e.g. one variant bounds accuracy
and measures throughput; another only measures accuracy).

### D. Reference Solution
A solution that satisfies the problem spec and constraints, using the defined dataset, with
its performance metrics measured as a **baseline** other solutions are compared against.

*Skill guidance (not ontology text):* **a reference solution scored against a different
target than it was trained on isn't a valid reference.** "Using the defined dataset"
includes the dataset's defined ground truth. Two things to check:

- A model trained on an adjacent label isn't measuring the benchmark's task, even when
  that label lives in the same dataset. In axess-benchmark the original checkpoints were
  trained on `hls_resource_report` (HLS estimates), not the benchmark's post-synthesis
  `resource_report`, and scored worse than predicting the mean.
- Paper prose isn't enough evidence of which label a model trained on. Prove it on data,
  by matching the training labels against each candidate field.

The reference solution also means the whole published inference procedure, not just the
weights: preprocessing, the statistics it needs, and post-processing such as inverse
transforms or caps. A checkpoint run without them isn't the reference solution. See
SKILL.md element D.

### E. Documentation and Reproducible Protocol
A protocol to reproduce the reference solution, so other submissions can make direct,
apples-to-apples comparisons. Typically reference code in a versioned, well-defined software
environment. If hardware is involved, thorough documentation and a bill of materials.

## Part 2 — The six-category rating rubric

Each of the six categories is scored **0–5**. A benchmark's overall rating is the **average
of the six category scores** (so overall is also out of 5, not out of 30). A benchmark
whose overall average is **≥ 4.5 / 5** earns the "MLCommons Science Benchmark Endorsement."

Five of the six categories are simple checklists — one point per true statement, max 5.
Two categories (Dataset, Performance Metrics) have their own internal weighting; the exact
formulas are given inline below so scoring is deterministic and reproducible, not vibes.

### 1. Software Environment (1 pt each, max 5)
- [ ] Code is available to reproduce the baseline reference solution.
- [ ] The provided code is complete.
- [ ] The code itself is well documented.
- [ ] The code does not require any modifications to run.
- [ ] The environment is either containerized, or environment details and setup
      instructions are provided.

### 2. Problem Specification and Constraints (1 pt each, max 5)
- [ ] System constraints (power, latency, throughput, etc.) are provided.
- [ ] The benchmark task is clear.
- [ ] The dataset format is clearly specified.
- [ ] The task inputs are clearly specified.
- [ ] The task outputs are clearly specified.

### 3. Dataset (max 5)
One point for each FAIR principle actually followed (max 4), **plus** one point if
well-defined train/test(/validation) splits are present (max 1). Total max 5.
- [ ] Findable
- [ ] Accessible
- [ ] Interoperable
- [ ] Reusable
- [ ] Well-defined train/test(/validation) splits are present

### 4. Performance Metrics (max 5)
Two sub-scales that sum to the category score. This is the one category where "some
credit" is graded on a scale rather than a checklist, because a half-defined metric is a
real, distinct failure mode from a well-defined-but-uninformative one.

**Metric Definitions (max 3):**
- 3 — metrics are fully defined
- 2 — metrics are clearly mentioned, but specific details/implementation are not defined
- 1 — some metrics are mentioned, but not clearly defined (what's actually being tracked
      is ambiguous)
- 0 — no metrics are mentioned or defined

**Metric Quality (max 2):**
- 2 — the metrics fully capture the solution's performance
- 1 — the metrics partially capture the solution's performance
- 0 — the metrics do not capture the solution's performance

Category score = Definitions + Quality (max 3 + 2 = 5).

### 5. Reference Solution (1 pt each, max 5)
- [ ] A reference solution is publicly available.
- [ ] The provided reference solution is well documented.
- [ ] All hardware and/or software requirements to run the reference solution are listed.
- [ ] All metrics defined as part of the benchmark are evaluated as part of the reference
      solution.
- [ ] The baseline solution/model is openly available for study (and if a neural network,
      the architecture, hyperparameters, and training code are provided).

### 6. Documentation (1 pt each, max 5)
- [ ] The task is explained and well documented.
- [ ] The task and benchmark background (scientific and otherwise) is clearly explained.
- [ ] The motivation for the benchmark is clearly explained.
- [ ] The evaluation criteria are clearly explained.
- [ ] An academic paper about the benchmark exists.

### Scoring notes
- Every criterion should be checked against **evidence you can point to** (a file, a repo
  section, a sentence in the docs), not assumed. If you can't point to it, it isn't met yet.
- Several criteria are judgment calls ("well documented", "clear task"). Make the call, but
  say why, and when genuinely ambiguous, ask the user rather than guessing generously —
  an inflated self-score isn't a favor to anyone who later applies for endorsement.
- `scripts/score_benchmark.py` implements exactly this arithmetic against a filled-in
  `assets/rubric_template.yaml`. Use it rather than hand-averaging — it's the same
  computation every time, and it explains itself in the output.

## Part 3 — Motif taxonomy (for classifying a benchmark)

Every benchmark should be tagged with its **Scientific Motif(s)** (domain — a benchmark can
have several) and exactly **one AI/ML Motif** (task type). This isn't scored by the rubric,
but it's how the ontology's website/search makes a benchmark findable (the "Findable" FAIR
criterion above, and the broader point of the ontology existing at all), so get it right.

**Scientific Motifs** (domains in the current ontology; more are added over time):
High-Energy Physics · Chemistry · Materials Science · Biology & Medicine ·
Climate & Earth Science · Computational Science & AI · Mathematics

**AI/ML Motifs** (task types — pick the single best fit):
Classification · Regression · Sequence Prediction/Forecasting · Anomaly Detection ·
Reinforcement Learning/Control · Generative · Multimodal Reasoning · Surrogate Modeling ·
Reasoning & Generalization

**Computing Motifs** (optional, describes the typical resource bottleneck — a benchmark can
have more than one): Latency Bound · Memory Bound · Throughput Bound · Utilization Bound

### What metrics do comparable existing benchmarks actually use?

**There is no single "the" metric suite for this ontology — metric choice is a function of
the AI/ML motif and the specific scientific question, not a default to reach for.** Don't
let `scripts/metrics.py`'s regression trio (R²/SMAPE/RMSE, copied from wa-hls4ml because
wa-hls4ml is a regression benchmark) become the assumed answer for a benchmark that isn't
regression. When helping a user pick metrics for element C, ground the conversation in what
benchmarks with the *same AI/ML motif* actually measure — the ontology paper (Section IV-B2)
documents real examples per motif, reproduced here:

| AI/ML Motif | Example benchmark | What it actually measures |
|---|---|---|
| Classification | Jet Classification, Smart Pixels for LHC, SatImgNet | Class accuracy (often per-class/multi-task) |
| Regression | FEABench | Solve-time and error norm |
| Regression | CFDBench | L2 error, MAE |
| Regression | OCP, Materials Project | MAE/error on physical quantities (adsorption energy, band-gap, formation energy) |
| Sequence Prediction/Forecasting | ClimateLearn | Forecast error on ERA5-based medium-range weather prediction |
| Sequence Prediction/Forecasting | GB-Biology | Standardized eval protocols for node/link/graph property prediction |
| Anomaly Detection | HDR ML Anomaly Challenge (Sea-Level Rise, Gravitational Waves) | ROC-AUC, precision/recall |
| Reinforcement Learning/Control | Beam Control | Stability loss, control-latency |
| Reinforcement Learning/Control | Quench Detection | ROC-AUC, detection latency |
| Generative | MOLGEN | log-P, QED, docking scores (chemistry-specific validity/quality measures) |
| Generative | SuperCon3D | MAE + validity |
| Multimodal Reasoning | SPIQA | Accuracy, F1 |
| Multimodal Reasoning | SeafloorAI | Segmentation pixel accuracy + QA accuracy (two metrics, one per modality) |
| Surrogate Modeling | CFDBench, The Well | L2 error, MAE |
| Reasoning & Generalization | MedQA, FrontierMath, AIME | Task accuracy |

For benchmarks that evaluate language models (most Reasoning & Generalization and many
Multimodal Reasoning entries above), the metrics are defined in an lm-evaluation-harness
task and re-implemented in the benchmark's `score.py`; see `references/llm-benchmarks.md`
for the extraction, normalization and statistical-power questions they raise.

Read this table as "here's the shape of a good answer for this motif," not a menu to copy
verbatim — e.g. a new anomaly-detection benchmark should ask whether ROC-AUC/precision-recall
actually fits its own class balance and cost structure, not just adopt them because two prior
anomaly benchmarks did. Several motifs above (Generative, Reinforcement Learning/Control,
Multimodal Reasoning) have no reusable implementation in `scripts/metrics.py` at all, on
purpose — those need bespoke, task-specific code, and pretending otherwise would just produce
a benchmark whose metrics don't capture what it claims to (a direct hit against rubric
Category 4's Metric Quality sub-score).

## Part 4 — Users this ontology is designed for

Keep these three in mind while interviewing a user about their benchmark — a good benchmark
package should genuinely serve all three, not just the person building it:

1. **Specific-benchmark seekers** — want one benchmark matching a domain + task type. Served
   by good metadata/tagging (motifs above).
2. **Category seekers** — want a slice of benchmarks (e.g. "all HEP benchmarks," or "all
   classification tasks in HEP"). Served by consistent, accurate motif tagging.
3. **Compute-pattern seekers** — hardware vendors/systems researchers looking for workloads
   with similar computational behavior regardless of domain. Served by documenting system
   constraints and computing motifs (Part 3), and, if relevant, profiling data.
