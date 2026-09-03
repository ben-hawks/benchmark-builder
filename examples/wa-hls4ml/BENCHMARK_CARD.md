# wa-hls4ml: FPGA Resource and Latency Surrogate Benchmark

> Given a neural network's architecture and its hls4ml hardware-conversion configuration,
> predict the FPGA hardware resources (LUTs, FFs, DSPs, BRAM) and timing (latency in clock
> cycles, initiation interval) that hardware synthesis would produce -- without actually
> running synthesis, which can take hours per model.

**Scientific Motif(s):** High-Energy Physics, FPGA/Hardware Design for Machine Learning
**AI/ML Motif:** Regression (multi-target)
**Computing Motif(s) (optional):** Surrogate modeling / simulation replacement

This benchmark card follows the structure defined by the MLCommons Science Benchmarks
Ontology (arXiv:2511.05614) — see `references/ontology.md` in the benchmark-builder skill
for the full definition of each section below.

Source material: Hawks et al., "wa-hls4ml: A Benchmark and Surrogate Models for hls4ml
Resource and Latency Estimation," ACM Transactions on Reconfigurable Technology and
Systems (TRETS), 2026, DOI: 10.1145/3787490, arXiv:2511.05615. This card was assembled
by reading the paper, the `fastmachinelearning/wa-hls4ml-paper` repo, and the
`fastmachinelearning/wa-hls4ml` dataset card on Hugging Face -- not by interviewing the
authors -- per this skill's "Gather artifacts before interviewing" workflow. It is a
dogfooding exercise for this skill's own `references/wa-hls4ml-example.md`, not a
replacement for that reference doc.

---

## 1. Problem Specification and Constraints

**Task.** Given `<a Keras/QKeras model description + its hls4ml conversion config>`,
produce `<6 regression targets>`: LUT count, FF count, DSP count, BRAM count, latency
(clock cycles), and initiation interval (II).

**Inputs.** A model's architecture (layer types, widths, activation functions) plus its
hls4ml config: precision (bit width), reuse factor, strategy (Latency/Resource), and I/O
type. Represented as JSON in the dataset (see `model_config`/`hls_config` fields below).

**Outputs.** Six scalar integers/counts per sample: LUTs, FFs, DSPs, BRAM, latency
(cycles), II (cycles).

**System constraints.** Target FPGA part (e.g. Xilinx Alveo U250/U200), clock period, and
Vivado/Vitis HLS version are fixed per sample and bound what a prediction means -- they
are not being optimized, but a valid prediction is only meaningful for the target/version
it was made against.

---

## 2. Dataset

**Summary.** 683,176 fully synthesized samples (608,679 fully-connected, 31,278 1D-conv,
43,219 2D-conv networks), each run all the way through Vivado/Vitis HLS synthesis to get
ground-truth resource/latency numbers -- not simulated or estimated.

**Splits.**

| Split | Size | Purpose |
|---|---|---|
| Train | 478,220 | Training |
| Validation | 102,472 | Model selection |
| Test | 102,484 | Held-out evaluation, same distribution as train |
| Exemplar (held-out generalization set) | 887 | Real scientific-application architectures (particle physics, anomaly detection, image processing) -- tests generalization beyond the synthetic training distribution |

**Schema.** Each sample is one JSON object with 9 fixed top-level fields: `meta_data`
(identifier, model name, project archive reference), `model_config` (Keras/QKeras
representation), `hls_config` (hls4ml conversion parameters), `resource_report`
(post-logic-synthesis component counts), `hls_resource_report` (post-HLS resource
estimates), `latency_report` (timing estimates), `target_part`, `vivado_version`,
`hls4ml_version`.

**Access.** Hosted on Hugging Face as `fastmachinelearning/wa-hls4ml` (4.98 GB), plus a
companion `-projects` dataset with full synthesis logs, under CC-BY-NC 4.0. Versioned via
the Hugging Face dataset's own revision history.

**FAIR checklist:**
- [x] Findable — every sample carries a `meta_data` identifier; the dataset itself has a
      stable HF dataset ID and a DOI via the paper (10.1145/3787490)
- [x] Accessible — Hugging Face `datasets` library, open access, no login required
- [x] Interoperable — JSON records with a documented, fixed 9-field schema (above);
      loadable directly via `datasets.load_dataset`
- [x] Reusable — versioned on HF; generation code (`wa-hls4ml-search`, part of
      `wa-hls4ml-paper`) is public under Apache 2.0, so the pipeline that produced it is
      itself reproducible

**Bounded-ness.** No augmentation/enrichment of the dataset is expected for a submission
-- a submission trains/evaluates against the splits as published.

---

## 3. Performance Metric(s)

| Metric | Formula / definition | What it captures | Computed on |
|---|---|---|---|
| R² | Coefficient of determination | Overall variance captured | Every target, per subset |
| SMAPE | `200%/n * Σ(\|y-ŷ\| / (\|y\|+\|ŷ\|+ε))`, ε = smallest strictly positive value the variable can take (1, since these are integer counts) — explicit division-by-zero handling | Relative accuracy, comparable across targets of very different scale (LUTs vs. cycles) | Every target, per subset |
| RMSE | Standard root-mean-square error | Magnitude of error, sensitive to outliers | Every target, per subset |
| RPE (visualization only) | Relative percent error per sample, shown as a box plot | Reveals systematic over/under-prediction a scalar metric hides | Per target variable |

Metrics are computed **per target variable** (BRAM/DSP/FF/LUT/Cycles/II) and **per
dataset subset** (all/dense/conv1d/conv2d, and per exemplar architecture) — not a single
aggregate number. This is a single-dimensional regression-quality benchmark (no Pareto
tradeoff between targets is imposed; each target is scored independently).

---

## 4. Reference Solution

**Summary.** Three reference solutions, positioned as a strength-of-evidence ladder, all
evaluated with the identical metric suite on the identical test/exemplar splits:

1. **Baseline MLP** (from prior work, rule4ml) — code in
   `fastmachinelearning/wa-hls4ml-paper`'s `rule4ml` submodule
   (`notebooks/benchmark.ipynb`, `notebooks/train.ipynb`), GPLv3.
2. **GNN** — 5-layer GATv2 (graph attention network), code in the `wa_hls4ml_models`
   submodule, CC-BY-NC 4.0.
3. **Transformer** — 2 encoder blocks with per-layer tokenization, same submodule/license.

**Architecture / method.**
- Baseline MLP: 200 training epochs, Adam optimizer, MSLE loss.
- GNN (GATv2, 5 layers): attention-based message passing over the model's layer graph;
  trained on an NVIDIA A10.
- Transformer (2 encoder blocks): per-layer tokenization of the model architecture;
  trained on an NVIDIA A100.

**Results.** Reported in the paper's Table 4 (main test set, per-subset breakdown) and
Table 5 (exemplar set) across all six targets and all three metrics for all three
models -- e.g. the baseline MLP performs well on dense-layer targets but is
specifically weak on DSP prediction, a finding only visible because of the per-subset
breakdown.

**Requirements.** Python; GNN/Transformer need an NVIDIA GPU (A10/A100 used for training,
inference is lighter); baseline MLP usable via the `rule4ml` PyPI package (v0.2.0+).

---

## 5. Documentation and Reproducible Protocol

**Reproduction steps.**
1. `git clone --recurse-submodules` `fastmachinelearning/wa-hls4ml-paper` (submodules are
   >1 GB; `git submodule update --init --recursive` if cloned without `--recurse-submodules`).
2. Dataset generation: see `wa-hls4ml-search` submodule's own README, or skip generation
   and load the published dataset directly from Hugging Face.
3. Baseline MLP: `rule4ml/notebooks/train.ipynb` then `benchmark.ipynb`.
4. GNN/Transformer: see `wa_hls4ml_models` submodule's own README for training/eval
   entry points.

**Environment.** No single top-level environment file covers all three reference
solutions -- each submodule (`rule4ml`, `wa_hls4ml_models`, `wa-hls4ml-search`) documents
its own dependencies separately. This is a real, self-acknowledged gap (see Score
below), not glossed over here.

**Motivation.** Hardware synthesis (Vivado/Vitis HLS) for a single FPGA design can take
hours; a fast, accurate surrogate model lets researchers iterate on architecture/
quantization choices without paying that cost for every candidate design, which is the
practical bottleneck this benchmark exists to address.

**Background.** hls4ml converts trained Keras/QKeras models into FPGA firmware (HLS C++)
for real-time inference in physics detectors and other latency-critical scientific
instruments. Choosing an architecture and hls4ml config that fits a hardware resource
budget currently requires expensive trial-and-error synthesis runs; this benchmark
targets the surrogate-model problem of predicting synthesis outcomes directly.

**Citation.**
```bibtex
@misc{hawks2025wahls4mlbenchmarksurrogatemodels,
      title={wa-hls4ml: A Benchmark and Surrogate Models for hls4ml
      Resource and Latency Estimation},
      author={Benjamin Hawks and Jason Weitz and others},
      year={2025},
      eprint={2511.05615},
      archivePrefix={arXiv},
      primaryClass={cs.LG},
      url={https://arxiv.org/abs/2511.05615}
}
```

---

## Submission Guidelines

Adapting the paper's own three-tier framing (Section 3.1):
- **Required**: predicted values for all six targets on the test and exemplar sets, plus
  R²/SMAPE/RMSE computed per-target and per-subset.
- **Strongly recommended**: architecture/hyperparameter description, shared code and
  trained weights, inference hardware + timing.
- **Suggested**: RPE box plots per target; documentation of any additional training data
  or constraints used.

> See `assets/submission_report_template.md` in the benchmark-builder skill for the full
> report format.

---

## Known limitations (stated, not hidden)

- The exemplar set's distribution differs meaningfully from the synthetic
  training/test distribution (real scientific architectures vs. randomly generated
  ones) — the paper's own "Summary and Outlook" names this as limiting how far
  generalization claims can be pushed.
- RMSE "may reflect a tendency towards smaller absolute predictions rather than better
  accuracy" per the paper's own discussion — a known blind spot of that specific metric,
  which is why R²/SMAPE are reported alongside it rather than RMSE alone.
- No single top-level environment/dependency file spans all three reference solutions
  (see Documentation section above).
