---
language:
- en
tags:
- project:genesis
- project:AXESS
- type:model
- science:particlephysics, computing
- risk:general
license: cc-by-nc-4.0
license_link: https://creativecommons.org/licenses/by-nc/4.0/
datasets:
    - https://huggingface.co/datasets/fastmachinelearning/wa-hls4ml (train/val/test splits; mirror https://amsc.fnal.gov:2880/amsc/public/axess/wa-hls4ml/)
metrics:
    - training_loss (MSE on log-transformed, z-scored targets; logged in the release's train.log)
    - validation_loss (same; drives ReduceLROnPlateau and early stopping)
    - R² (coefficient of determination), per target and per group (axess-benchmark score.py)
    - SMAPE (symmetric mean absolute percentage error, ε = 1), per target and per group (axess-benchmark score.py)
    - RMSE (root mean square error), per target and per group (axess-benchmark score.py)
---

# wa-hls4ml GNN (GATv2), retrained on post-synthesis resources

A 5-layer GATv2 graph neural network that predicts the FPGA resources (LUT, FF, DSP,
BRAM) and latency (cycles, initiation interval) of an hls4ml-converted neural network
from the network and its hls4ml configuration, without running synthesis. It is the
paper's GNN architecture (Hawks et al., "wa-hls4ml: A Benchmark and Surrogate Models for
hls4ml Resource and Latency Estimation," ACM TRETS 19(2), 2026,
doi:10.1145/3787490, §4.2) **retrained on post-logic-synthesis resource labels**. It's
one of the three reference solutions of the wa-hls4ml benchmark as packaged in
[axess-benchmark](https://github.com/ben-hawks/axess-benchmark).

This is **not** the checkpoint behind the paper's Table 4. That one
(`gnn_final_model.pth`) was trained on the HLS C-synthesis estimates
(`hls_resource_report`), so it predicts a different quantity. Scored against the
benchmark's ground truth, it does worse than predicting the mean on all four resource
targets (axess-benchmark `docs/VALIDATION.md` §5).

*Last Updated*: **2026-10-02**

## Developed by

Architecture and original training code: Jason Weitz and Dmitri Demler (University of
California San Diego), per the `wa-hls4ml-paper` README. Retraining on post-synthesis
labels: the `resource-report-retraining` branch of
[ben-hawks/wa_hls4ml_models](https://github.com/ben-hawks/wa_hls4ml_models), merged as
release `resource-report-retrain` (commit `ac394e9`).

## Contributed by

The wa-hls4ml paper authors (full list in the citation below). Benchmark packaging and
inference verification: axess-benchmark.

## Model Changelog

+ **2025** original GNN trained on HLS C-synthesis estimates (`hls_resource_report`),
  reported in the paper's Table 4. Superseded as a benchmark reference solution.
+ **2026** retrained on post-synthesis `resource_report` labels; release
  `resource-report-retrain` (`ac394e9`). This card.

## Model short description

GATv2 graph neural network regressing 6 FPGA resource/latency targets from a network's
per-layer description and its hls4ml conversion settings.

## Model description

Each input network is a graph: one node per layer with 33 features, sequential edges,
and a 4-dimensional global feature vector. Five GATv2 layers (5 heads × 512, concatenated)
with LayerNorm, ELU and residual connections feed a learned add/mean/max pooling and an
MLP head (516 → 512 → 256 → 6). Targets are log-transformed (ε = 1e-6) and z-scored for
training. Predictions are inverted (`exp(y·σ + μ) − ε`), clamped at 0, and **capped at
the per-target training maximum**. The cap is part of the published inference procedure:
without it a few inputs extrapolate to physically impossible values. 54,471,945
parameters.

On the benchmark's test split it reaches mean R² 0.78 over the six targets, behind the
retrained Transformer (0.81) and well ahead of the baseline MLP (0.32).

## Finetuned from model (optional)

Not a fine-tune; trained from scratch.

## Model Type

Graph Attention Network v2 (`FPGA_GNN_GATv2`, PyTorch Geometric `GATv2Conv`).

## Inputs and outputs

- **Input:** a sample's `model_config` (flat per-layer list) and `hls_config` (precision,
  reuse factor, strategy, I/O type) from the wa-hls4ml dataset. These are turned into 18
  raw features per layer by upstream preprocessing (vendored bit-identically in
  axess-benchmark `src/wa_hls4ml_bench/features.py`), then encoded to 33 per node:
  - 12 numerical features, z-scored with the shipped normalization statistics;
  - one-hot layer type (12), activation (6) and padding (3);
  - global one-hot strategy (2) and I/O type (2).

  The model never uses any `*_report` field as input.
- **Output:** 6 non-negative values per network: `BRAM`, `DSP`, `FF`, `LUT` (absolute
  counts, BRAM in half-block units), `cycles_max` and `interval_max` (clock cycles).

## Compute Infrastructure

### Hardware

- **Training:** one CUDA GPU (`Using device: cuda` in the release's `train.log`); the GPU
  model isn't recorded in the log. The paper trained the original GNN on an NVIDIA A10.
- **Inference:** CPU or one GPU.
  - 1.1 ms/sample on a workstation CPU, including featurization.
  - The full benchmark ran on one NVIDIA A100 on
    [NERSC Perlmutter](https://docs.nersc.gov/systems/perlmutter/) (Slurm jobs
    59209565–68, 2026-10-02) and reproduced the CPU reference results to ≤2.4e-4
    relative.

### Software

PyTorch + PyTorch Geometric. Inference environment: axess-benchmark `requirements.txt`
(`torch>=2.6`, `torch_geometric==2.6.1`, pure Python, no compiled PyG extensions). On
Perlmutter it's layered on the NERSC `pytorch` module (`perlmutter/setup.sh`). The
training environment was a Python 3.11 venv; see `5_26_requirements.txt` in
`wa_hls4ml_models`.

## Papers and Scientific Outputs

```bibtex
@article{hawks2026wahls4ml,
  title={wa-hls4ml: A Benchmark and Surrogate Models for hls4ml Resource and Latency Estimation},
  author={Hawks, Benjamin and Weitz, Jason and Demler, Dmitri and Tame-Narvaez, Karla and Plotnikov, Dennis and Rahimifar, Mohammad Mehdi and Rahali, Hamza Ezzaoui and Therrien, Audrey C. and Sproule, Donovan and Khoda, Elham E. and Smith, Keegan A. and Marroquin, Russell and Di Guglielmo, Giuseppe and Tran, Nhan and Duarte, Javier and Loncar, Vladimir},
  journal={ACM Transactions on Reconfigurable Technology and Systems},
  volume={19}, number={2}, pages={1--29}, year={2026},
  publisher={Association for Computing Machinery},
  doi={10.1145/3787490}, url={https://doi.org/10.1145/3787490}
}
```

## Model License

The weights are licensed CC-BY-NC 4.0
([license text](https://creativecommons.org/licenses/by-nc/4.0/)), the same license as the
paper's surrogate models in the `wa-hls4ml-paper` README. The authors confirmed on
2026-10-02 that it covers the retrained checkpoint; the `resource-report-retrain` release
doesn't state it. The training and model **code** is Apache-2.0 (the `wa_hls4ml_models`
LICENSE).

## Contact Info and Model Card Authors

Corresponding author: **not filled in.** Ask the authors rather than inferring one from
the author list. This card was written with the benchmark-builder skill from the
release, the paper and axess-benchmark, not by the model's authors.

# Intended Uses

## Intended Use

Fast pre-synthesis estimates of FPGA resources and latency for hls4ml designs, for
architecture search, quantization tuning and other hardware/software codesign loops,
where one synthesis run takes minutes to hours.

### Primary Intended Users

Researchers and engineers building real-time ML on FPGAs (e.g. particle-physics trigger
systems and other latency-critical scientific instruments).

### Mission Relevance

Supports DOE real-time scientific instrumentation (e.g. HL-LHC trigger electronics),
where synthesis-in-the-loop design-space exploration is a practical bottleneck.

## Out-of-Scope Use Cases

- Tools other than hls4ml, or FPGA parts and toolchain versions outside the training
  data. The target part isn't a model input.
- Architectures far from the synthetic training distribution. See the exemplar results
  below: on real scientific architectures, latency predictions can fail badly.
- Utilization fractions without knowing the target part (outputs are absolute counts).

# How to use

## Install Instructions

```bash
git clone https://github.com/ben-hawks/axess-benchmark.git && cd axess-benchmark
pip install torch && pip install -r requirements.txt
python scripts/fetch_weights.py --out weights_dl   # downloads + sha256-checks the checkpoint
```

| File | sha256 | Bytes |
|---|---|---|
| `gnn_resource_report_final_model.pth` ([release asset](https://github.com/ben-hawks/wa_hls4ml_models/releases/tag/resource-report-retrain)) | `ac8bbfbf766898412271298b3f39318f3a3e522d62febaeb68bdb85d8fea2b0c` | 217,909,055 |
| `normalization_stats.json` (versioned in axess-benchmark `weights/`) | — | small |

## Training configuration

See "Pre-training information" below; the training script is
`GNN/training_scripts/y_03_GAT_vanilla_bigboi.py` in `wa_hls4ml_models` at `ac394e9`.

## Inference configuration

The checkpoint needs `normalization_stats.json`: feature and label statistics plus the
per-target cap. Neither checkpoint ships them. axess-benchmark rebuilt them from the
train split (`python -m wa_hls4ml_bench.stats`); they agree with the release's
`normalization_stats_log.npy` to float32 precision. The caps are:

| Cycles | FF | LUT | BRAM | DSP | II |
|---|---|---|---|---|---|
| 38,349,241 | 1,570,553 | 2,265,699 | 1,029.5 | 12,280 | 38,349,236 |

# Code snippets of how to use the model

```bash
python -m wa_hls4ml_bench.cache --data-root $WA_DATA --split test --out $WA_CACHE/test.npz
python -m wa_hls4ml_bench.predict --model gnn --cache $WA_CACHE/test.npz \
    --weights-dir $WA_WEIGHTS --device cuda --out results/test/predictions_gnn.csv   # or --device cpu
python -m pytest tests -q   # golden outputs on 40 real samples; WA_TEST_DEVICE=cuda on a GPU
```

# Limitations

## Risks

No CBRNE or novel security-vulnerability risk identified. This is a small regression
model for FPGA design-cost estimation, not a general-purpose or frontier model.

## Limitations

- **Out-of-distribution latency.** Exemplar Cycles/II R² is −6.9/−5.8. The cause is
  almost entirely the 119 Bipc exemplar samples (Cycles RMSE 9,497 vs ~690 elsewhere).
  Those samples need a feature-extraction fallback, and the Transformer and rule4ml
  models handle them normally. Not resolved.
- **DSP** stays well below the paper's HLS-estimate GNN (R² 0.56). The worst errors are
  large designs (~12,000 DSPs) predicted at 1,000–2,000; about a third of conv models use
  no DSPs after synthesis.
- **BRAM:** the `2_20` subset was synthesized for three FPGAs while the target part isn't
  an input. It's 1.5% of the test set but 49% of the GNN's BRAM squared error. Half-block
  BRAM isn't predictable from the features.
- **Training coverage** leans to fully connected models. Only about 29% of conv2d and
  42% of conv1d records have post-synthesis results.
- **Latency labels** come from `latency_report`, the post-HLS latency estimate. The
  dataset has no post-synthesis latency, so only the four resource targets are
  post-logic-synthesis.

# Training details

## Training data

[wa-hls4ml](https://huggingface.co/datasets/fastmachinelearning/wa-hls4ml)
(CC-BY-NC 4.0) train/val/test splits, converted by `dataset/Dataset_to_csvs6_with_ii.py
--resource-key resource_report` in `wa_hls4ml_models`:

- FF/LUT/BRAM/DSP come from post-logic-synthesis `resource_report`; cycles and II from
  `latency_report`.
- Samples without a `resource_report` are skipped. A missing latency report is read as 0;
  that converter filter differs slightly from the benchmark's scoring filter.

| Split | Networks | Array shape |
|---|---|---|
| Train | 433,676 | (433676, 51, 18) |
| Validation | 92,992 | (92992, 51, 18) |
| Test | 92,933 | (92933, 51, 18) |

The dataset revision used for training isn't recorded in the release. axess-benchmark's
`scripts/fetch_data.py` records the revision for each benchmark run. See `genesis_datacard_wa_hls4ml.md`.

## Training Procedure

- AdamW, learning rate 3e-3, weight decay 5e-6, batch size 1024;
- MSE loss on log/z-scored targets, dropout 0.3;
- ReduceLROnPlateau (the learning rate halves on plateaus);
- early stopping: stopped at epoch 105 of a 200-epoch budget; best validation epoch
  65. The release doesn't say which epoch's weights the published checkpoint holds.

### Reproducibility Information (optional)

- Random seed used: **not recorded** in the release.
- Machine/environment info: one CUDA GPU (model not recorded); Python 3.11 venv.
- Link to training pipeline: [wa_hls4ml_models @ `ac394e9`](https://github.com/ben-hawks/wa_hls4ml_models/tree/resource-report-retrain),
  `GNN/training_scripts/y_03_GAT_vanilla_bigboi.py` and `resource_report_results/README.md`.

## Pre-training information

+ Hyperparameters: the paper's GNN configuration (hidden 512, 5 layers, 5 heads, MLP
  hidden 512); no new tuning for the retrain is reported.
+ Initialization: from scratch.
+ Optimizer: AdamW (lr 3e-3, weight decay 5e-6), ReduceLROnPlateau.
+ Loss function: MSE on log-transformed, z-scored targets.
+ Stopping criterion: early stopping on validation loss.
+ Number of training epochs: 105 run (best validation loss at epoch 65).
+ Batch size: 1024 (423 training batches per epoch).
+ Best validation loss: 0.0749.

# Evaluation details

## Evaluation data

The benchmark's test split (102,484 networks, 92,933 with post-synthesis ground truth)
and exemplar split (887 real scientific architectures, 886 with ground truth). Samples
without ground truth are excluded, never imputed. See `genesis_datacard_wa_hls4ml.md`.

## Evaluation Procedure

axess-benchmark `src/wa_hls4ml_bench/score.py` computes R², SMAPE (ε = 1, as paper Eq. 2
states) and RMSE per target, overall and per group (test: dense/conv1d/conv2d; exemplar:
per architecture), plus per-sample RPE box plots. The baselines are the other reference
solutions on the same samples.

Inference was verified per sample against the release's own `test_predictions.npz`:
max |ours − theirs| / (|theirs| + 1) = 2.8e-4 over 92,933 samples, with identical cap
counts (9) and identical reported R².

## Uncertainty Quantification.

None. The model gives point estimates, and no seed-to-seed variance has been measured.

## Evaluation results

R², all scored samples (axess-benchmark `reference_results/`, 2026-10-02):

| Split | BRAM | DSP | FF | LUT | Cycles | II | mean |
|---|---|---|---|---|---|---|---|
| Test (n = 92,933) | 0.640 | 0.565 | 0.935 | 0.901 | 0.815 | 0.827 | 0.780 |
| Exemplar (n = 886) | −0.213 | 0.038 | 0.522 | 0.563 | −6.863 | −5.785 | −1.956 |

SMAPE % (ε = 1):

| Split | BRAM | DSP | FF | LUT | Cycles | II |
|---|---|---|---|---|---|---|
| Test | 21.6 | 14.8 | 14.1 | 14.0 | 17.9 | 14.5 |
| Exemplar | 57.2 | 84.1 | 85.6 | 57.0 | 88.0 | 116.3 |

For comparison, test mean R² is 0.809 for the Transformer and 0.319 for the baseline MLP.
Per-group tables are in `reference_results/<split>/gnn/METRICS.md`.

**Evaluation runtime:** about 2 minutes for the test split on a workstation CPU
(1.1 ms/sample including featurization). GPU timings on Perlmutter haven't been recorded.

# More Information (optional)

This card follows the live GEAR Model Card v1 template
(https://gear.doe.gov/rfa-teams/ai-and-agents/model-card-template, file fetched
2026-10-02). The front matter tags it as a Genesis Mission model of the AXESS team, as the
authors confirmed. It was re-targeted on 2026-10-02 from an earlier draft (2026-08-28) that
described the paper's original HLS-estimate checkpoint.
