#!/bin/bash
# OPTIONAL: only for benchmarks that include training (references/repo-structure.md,
# "Score-only vs includes training"). Writes checkpoints + derived artifacts to
# $BENCH_WEIGHTS for the inference jobs. Resources: BENCH_SB_TRAIN.
# ADAPT: the model list, the training/validation split names, seeds, and the launcher
# (srun, or the framework's own multi-GPU/multi-node launcher).
#SBATCH --job-name=bench-train
#SBATCH --output=%x-%j.out
set -euo pipefail
# Slurm runs a spooled copy of this script, so locate env.sh through the exported repo path.
source "${BENCH_REPO:-$SLURM_SUBMIT_DIR}/${BENCH_HPC:-slurm}/env.sh"
bench_activate
mkdir -p "$BENCH_WEIGHTS"

for model in model_a; do
    srun python -m benchpkg.train --model "$model" --cache-dir "$BENCH_CACHE" \
        --train-split train --val-split val --device "$BENCH_GPU_DEVICE" \
        --out-dir "$BENCH_WEIGHTS" --seed "${BENCH_SEED:-0}"
done
