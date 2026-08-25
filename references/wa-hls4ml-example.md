# Worked example: wa-hls4ml mapped onto the ontology

Source: Hawks et al., "wa-hls4ml: A Benchmark and Surrogate Models for hls4ml Resource and
Latency Estimation," arXiv:2511.05615. Same lead author as the ontology paper, and one of
the concrete benchmarks the ontology is meant to standardize — treat it as a positive
example of what a well-scored entry actually looks like in practice, not just in theory.

Use this file three ways:
1. **As a pattern** when scaffolding a new benchmark — each subsection below shows what a
   real, complete instance of that ontology element contains, so you can ask a user
   analogous questions instead of vague ones.
2. **As a sanity check on the rubric** — wa-hls4ml scores very well on some categories and
   has known, self-acknowledged gaps in others (see "Where it doesn't max out" at the
   bottom). If your scoring logic disagrees wildly with the numbers here for an
   apples-to-apples benchmark, something's off in how you're applying the rubric.
3. **As a model for the extraction pass itself** — everything below was written by
   reading the paper and repo (arXiv:2511.05615, the wa-hls4ml-paper repo's READMEs and
   code), not by interviewing anyone. That's exactly what SKILL.md's "Gather artifacts
   before interviewing" step should produce for a new benchmark too: evidence-cited draft
   answers per element, ready for the user to confirm or correct rather than dictate from
   scratch.

## The five elements, as wa-hls4ml implements them

### A. Problem Specification and Constraints
- **Task**: predict FPGA hardware resource usage and latency for a neural network *before*
  running hardware synthesis. Input = a Keras/QKeras model description plus its hls4ml
  conversion config (precision, reuse factor, strategy, I/O type). Output = 6 regression
  targets: LUTs, FFs, DSPs, BRAM, latency (clock cycles), initiation interval (II).
- **Constraints**: target FPGA part (e.g. Alveo U250/U200), clock period, Vitis/Vivado
  version — these bound the problem (a prediction is only valid for a given target/version)
  without themselves being optimized.
- Lesson for scaffolding: separate "what varies and is the actual regression target" from
  "what's fixed context that changes the meaning of a sample" — that's the
  constraints-vs-metrics distinction the ontology cares about.

### B. Dataset
- 683,176 synthesized samples total, explicitly split into **Training (478,220)**,
  **Validation (102,472)**, **Test (102,484)**, and a held-out **Exemplar test set (887)**
  of real scientific-application architectures used specifically to test generalization
  beyond the synthetic training distribution.
- Every sample is one JSON file with 9 fixed top-level fields: `meta_data`, `model_config`,
  `hls_config`, `resource_report`, `hls_resource_report`, `latency_report`, `target_part`,
  `vivado_version`, `hls4ml_version` — i.e. the schema is documented field-by-field, not
  just "here's a folder of JSON."
- FAIR in practice: hosted on HuggingFace (`fastmachinelearning/wa-hls4ml`, plus a
  companion `-projects` dataset with the full synthesis logs) under a named license
  (CC-BY-NC 4.0), with a dataset card — that's Findable + Accessible + Interoperable in one
  move. Reusable because the generation code (`wa-hls4ml-search`) is public alongside the
  data, so the pipeline that produced it is itself reproducible, not just the output.
- Lesson: a "dataset" isn't just files — it's files + a documented schema + a stated split
  + a documented generation process. All four are checkable independently.

### C. Performance Metric(s)
**These are wa-hls4ml's own choices for its own regression task, not a universal
template.** The pattern worth copying is *how rigorously they're defined and applied*
(exact formula, explicit edge-case handling, per-target/per-subset breakdown) — not the
specific R²/SMAPE/RMSE trio itself. A generative-chemistry or RL/control benchmark needs
completely different metrics; see `references/ontology.md`'s "What metrics do comparable
existing benchmarks actually use?" table before defaulting here.

Three metrics, formally defined, applied identically to every regression target
(BRAM/DSP/FF/LUT/Cycles/II):
- **R²** (coefficient of determination) — overall variance captured.
- **SMAPE** (symmetric mean absolute percentage error) — `200%/n * sum(|y-ŷ| / (|y|+|ŷ|+ε))`
  — relative accuracy, comparable across targets of very different scale (LUTs vs. cycles).
  Note the explicit epsilon handling: they set ε to "the smallest strictly positive value
  the resource/latency variables can have" (1, since these are integer counts) specifically
  to avoid division by zero — a well-defined metric spells out its edge cases, it doesn't
  leave them implicit.
- **RMSE** — magnitude of error, sensitive to outliers.
- Plus a visualization metric, **RPE** (relative percent error) per sample, shown as a
  box plot per target variable — this is what makes systematic over/under-prediction
  visible in a way a single scalar can't.
- Metrics are computed **per target variable separately**, and separately again per dataset
  subset (all/dense/conv1d/conv2d, and per exemplar architecture) — this is what "the
  metrics fully capture a given solution's performance" looks like at rubric-scoring time:
  not one number, but a breakdown fine enough to reveal where a model actually fails (e.g.
  their own Table 4 shows the baseline MLP is fine on dense layers but bad on DSP
  prediction specifically).

### D. Reference Solution
Not one reference solution but three, deliberately positioned as a strength-of-evidence
ladder:
- **Baseline MLP** (from prior work, rule4ml) — architecture, training procedure
  (200 epochs, Adam, MSLE loss) documented in the paper text.
- **GNN** (5-layer GATv2, described down to the attention formula) — architecture figure,
  hyperparameters, training hardware (NVIDIA A10), training procedure all stated.
- **Transformer** (2 encoder blocks, per-layer tokenization) — same level of detail,
  training hardware (A100) stated.
- All three are evaluated with the *exact same* metric suite on the *exact same* test/
  exemplar splits, and results are reported in full tables (Table 4, Table 5) — satisfying
  "all metrics defined as part of the benchmark are evaluated as part of the reference
  solution" for every reference solution, not just one.

### E. Documentation and Reproducible Protocol
- A full paper (this one) plus a repo README that separates "how to reproduce the dataset,"
  "how to reproduce the surrogate models," and "how to reproduce the plots" into distinct,
  linked sections rather than one undifferentiated wall of instructions.
- Section 3.1 of the paper ("Submission Guidelines") is itself a documentation-of-protocol
  artifact: it tells a *future* contributor exactly what a valid submission must include
  (predicted values for every metric, RPE box plots) vs. strongly recommended (architecture/
  hyperparameter description, shared code/weights, inference hardware + timing) vs.
  suggested (further constraints/training data documented). That three-tier framing
  (required / strongly recommended / suggested) is a reusable pattern — steal it directly
  when writing a submission_report template for a new benchmark.

## Rubric self-audit (approximate — treat as illustrative, not authoritative)

This is what applying the six-category rubric to wa-hls4ml as published looks like, to
calibrate your own scoring against a known case:

- **Software Environment**: code is public across multiple repos (dataset gen, models,
  baseline) and documented per-component, but the repo is spread across several large git
  submodules with no single one-command reproduction path, and the paper itself doesn't
  claim "runs without modification." Strong but not a clean 5/5.
- **Problem Specification and Constraints**: task, inputs, outputs, and target-hardware
  constraints are all explicit (Table 2, Section 2.1.1's parameter ranges). Close to 5/5.
- **Dataset**: hits all four FAIR points (hosted, licensed, documented schema, versioned
  with public generation code) plus explicit train/val/test/exemplar splits. 5/5.
- **Performance Metrics**: R²/SMAPE/RMSE are fully defined with explicit edge-case handling
  (the ε term) — Definitions likely 3/3. Whether they "fully capture" performance is a
  judgment call: the paper itself flags that RMSE "may reflect a tendency towards smaller
  absolute predictions rather than better accuracy" — the authors are explicitly aware
  their metric suite has a known blind spot on its own reference results. That kind of
  self-aware caveat is evidence *for* Metric Quality being taken seriously, but it also
  means don't auto-assume 2/2 without checking whether it's addressed.
- **Reference Solution**: three fully-documented, independently reproducible reference
  solutions, all evaluated against all metrics. 5/5.
- **Documentation**: task/background/motivation/evaluation are all explained at length, and
  an academic paper exists (this one, plus the companion rule4ml paper it builds on). 5/5.

The paper's own "Summary and Outlook" (Section 6) explicitly names the honest gaps: the
exemplar/test distribution mismatch limits generalization claims, and they call out future
work to broaden dataset diversity. **A benchmark doesn't need to claim perfection to score
well** — the rubric rewards being correct and complete about what's actually true, including
naming known limitations, over overclaiming. Encourage users you're helping to do the same:
a documented limitation is worth more, rubric-wise and scientifically, than silence about it.
