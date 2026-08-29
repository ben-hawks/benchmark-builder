---
language:
- en
tags:
- type:model
- science:particlephysics
- risk:general
license: cc-by-nc-4.0
datasets:
    - https://huggingface.co/datasets/fastmachinelearning/wa-hls4ml
metrics:
    - r_squared
    - smape
    - rmse
---

# wa-hls4ml GNN Surrogate Model

A 5-layer GATv2 (graph attention network) surrogate model that predicts FPGA hardware
resource usage and latency for a neural network's hls4ml hardware conversion, without
running Vivado/Vitis HLS synthesis. Introduced in Hawks et al., "wa-hls4ml: A Benchmark
and Surrogate Models for hls4ml Resource and Latency Estimation" (ACM TRETS, 2026;
arXiv:2511.05615). Original implementation: `wa_hls4ml_models` submodule of
`fastmachinelearning/wa-hls4ml-paper`.

*Last Updated*: **2026-08-28** (date this card was assembled; not the model's own release
date — see Model Changelog)

## Developed by

Fast Machine Learning Lab (Benjamin Hawks, Jason Weitz, and coauthors — see paper for
full author list).

## Contributed by

Not separately distinguished in the source material; see the paper's acknowledgments for
full contributor list.

## Model Changelog

+ Introduced alongside the paper (arXiv:2511.05615, submitted 2025; published ACM TRETS
  2026) as one of three reference solutions for the wa-hls4ml benchmark.

## Model short description

GATv2-based graph neural network that predicts 6 FPGA resource/latency targets (LUTs,
FFs, DSPs, BRAM, latency cycles, initiation interval) from a neural network architecture
graph plus its hls4ml conversion config.

## Model description

The model represents the input neural network as a graph (nodes = layers, edges =
connections) and applies 5 layers of GATv2 (Graph Attention Network v2) attention-based
message passing to produce a fixed-size embedding, which is then regressed onto the six
resource/latency targets. It is one of three reference solutions in the wa-hls4ml
benchmark (alongside a baseline MLP from prior work, `rule4ml`, and a Transformer
variant) — all three are evaluated with the identical metric suite for direct comparison
(see the benchmark's own `BENCHMARK_CARD.md`, section 4).

## Finetuned from model (optional)

Not a fine-tune; trained from scratch on the wa-hls4ml dataset.

## Model Type

Graph Attention Network v2 (GATv2), 5 layers, custom regression head.

## Inputs and outputs

- **Input**: a neural network architecture (Keras/QKeras layer graph) plus its hls4ml
  conversion configuration (precision, reuse factor, strategy, I/O type), represented as
  the `model_config`/`hls_config` JSON fields documented in the dataset schema.
- **Output**: 6 scalar predictions — LUT count, FF count, DSP count, BRAM count, latency
  (clock cycles), initiation interval (clock cycles).

## Compute Infrastructure

### Hardware

Trained on an NVIDIA A10 GPU, per the paper.

### Software

Not fully specified as a pinned dependency file in the source material — the
`wa_hls4ml_models` submodule's own README documents its own requirements separately from
the other two reference solutions (baseline MLP, Transformer). This is a real, named gap;
don't paper over it with an invented requirements list.

## Papers and Scientific Outputs

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
DOI (published version): 10.1145/3787490.

## Model License

CC-BY-NC 4.0 (Creative Commons Attribution-NonCommercial 4.0) — applies to the trained
surrogate models specifically, per `wa-hls4ml-paper`'s README (note this differs from the
dataset-generation code and the `rule4ml` baseline, which use Apache 2.0 and GPLv3
respectively — see the benchmark card's Reference Solution section for the full
per-component license breakdown).

## Contact Info and Model Card Authors

Not filled in — the source material (paper, repo) does not surface a single
corresponding-author email suitable for direct contact; see the paper itself for author
affiliations. This card was assembled by benchmark-builder's dogfooding pass on the
wa-hls4ml benchmark, not by the model's own authors.

# Intended Uses

## Intended Use

Predicting FPGA resource/latency for a candidate neural network + hls4ml config, to avoid
running full hardware synthesis during architecture search or quantization tuning.

### Primary Intended Users

Researchers and engineers designing real-time ML-on-FPGA systems (e.g. particle physics
trigger systems, other latency-critical scientific instruments) who need to explore many
architecture/quantization candidates faster than synthesis allows.

### Mission Relevance

Directly supports DOE-relevant real-time scientific instrumentation work (e.g. HL-LHC
trigger electronics) where synthesis-in-the-loop architecture search is currently a
practical bottleneck.

## Out-of-Scope Use Cases

Not validated for FPGA parts, Vivado/Vitis versions, or architecture families outside
what the training data covers (the exemplar set's own held-out generalization results are
the best evidence of how well this holds up outside the training distribution — see the
benchmark card's "Known limitations" section).

# How to use

## Install Instructions

See the `wa_hls4ml_models` submodule's own README in `fastmachinelearning/wa-hls4ml-paper`
(`git submodule update --init --recursive` after cloning; submodules exceed 1GB).

## Training configuration

Not reduced to a single pinned config file in the source material beyond what's stated
under Training details below; see the submodule README for the authoritative version.

## Inference configuration

Not separately documented from training configuration in the source material.

# Code snippets of how to use the model

Not reproduced here — see the `wa_hls4ml_models` submodule directly; this card
intentionally doesn't restate code that lives in, and can drift from, the source repo.

# Limitations

## Risks

No CBRNE-relevant or novel security-vulnerability risks identified — this is a hardware
resource/latency regression model for FPGA firmware design, not a general-purpose or
frontier model in the sense the DOE AI Action Plan risk framing addresses.

## Limitations

- Trained and evaluated primarily on synthetically generated architectures; the held-out
  exemplar set (887 real scientific-application architectures) shows the model
  generalizes less cleanly to real-world designs than to in-distribution synthetic ones —
  the paper's own "Summary and Outlook" names this directly.
- Per the benchmark card's Table-4-derived finding, resource-target accuracy varies by
  layer type (e.g. weaker on DSP prediction for some architectures) — not uniformly
  accurate across all six targets.

# Training details

## Training data

wa-hls4ml dataset (`fastmachinelearning/wa-hls4ml` on Hugging Face), Train split
(478,220 samples of the 683,176 total) — see `DATA_CARD.md` for full dataset detail.
Downloaded via the `datasets` library; version = the dataset's current HF revision as of
this card's creation date.

## Training Procedure

5-layer GATv2 architecture; trained on an NVIDIA A10. Exact epoch count, batch size, and
learning rate are not stated in the source material at the level of detail this skill
requires before asserting them as fact — flagged here as a genuine gap rather than
guessed.

### Reproducibility Information (optional)

- Random seed used: not stated in source material.
- Machine/environment info: NVIDIA A10 GPU (training); software stack not pinned in a
  single file (see Compute Infrastructure above).
- Link to training pipeline: `wa_hls4ml_models` submodule of
  `fastmachinelearning/wa-hls4ml-paper`.

## Pre-training information

Not applicable — trained from scratch, not pretrained/fine-tuned.

# Evaluation details

## Evaluation data

wa-hls4ml dataset Test split (102,484 samples) and Exemplar set (887 samples, held out
specifically to test generalization to real scientific architectures) — same source and
access as Training data above.

## Evaluation Procedure

Evaluated with R², SMAPE, and RMSE, computed per target variable (LUT/FF/DSP/BRAM/
latency/II) and per dataset subset (all/dense/conv1d/conv2d, and per exemplar
architecture) — see `BENCHMARK_CARD.md` section 3 for exact formulas including SMAPE's
epsilon handling.

## Uncertainty Quantification

Not reported in the source material for this model.

## Evaluation results

Full per-target, per-subset results are in the paper's Table 4 (test set) and Table 5
(exemplar set) — not reproduced numerically in this card since transcription risk
(a wrong digit read off a PDF table) outweighs the convenience; readers needing exact
numbers should go to the primary source.

# More Information (optional)

This model is one of three reference solutions in the wa-hls4ml benchmark (see
`BENCHMARK_CARD.md`). This card was generated as part of a dogfooding pass on the
benchmark-builder skill's DOE GEAR card workflow, following the live Model Card v1
template at https://gear.doe.gov/rfa-teams/ai-and-agents/model-card-template (fetched
2026-08-28) rather than a cached copy of its field structure.
