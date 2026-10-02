#!/bin/bash
# Inference for the GPU models on every split. Resources: BENCH_SB_INFER_GPU.
# ADAPT: the model list.
#SBATCH --job-name=bench-infer-gpu
#SBATCH --output=%x-%j.out
set -euo pipefail
# Slurm runs a spooled copy of this script, so locate env.sh through the exported repo path.
source "${BENCH_REPO:-$SLURM_SUBMIT_DIR}/${BENCH_HPC:-slurm}/env.sh"
bench_activate
nvidia-smi --query-gpu=name,driver_version --format=csv,noheader || true

for split in $BENCH_SPLITS; do
    for model in model_a model_b; do
        python -m benchpkg.predict --model "$model" --cache "$BENCH_CACHE/$split.npz" \
            --weights-dir "$BENCH_WEIGHTS" --device cuda \
            --out "$BENCH_RESULTS/$split/predictions_$model.csv"
    done
done
