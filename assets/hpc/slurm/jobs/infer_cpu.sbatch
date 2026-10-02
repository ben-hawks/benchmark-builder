#!/bin/bash
# Inference for CPU-only models. Resources: BENCH_SB_INFER_CPU.
# ADAPT: the model list, and which environment they need (bench_activate for the main
# venv, bench_activate_alt for a separate stack).
#SBATCH --job-name=bench-infer-cpu
#SBATCH --output=%x-%j.out
set -euo pipefail
# Slurm runs a spooled copy of this script, so locate env.sh through the exported repo path.
source "${BENCH_REPO:-$SLURM_SUBMIT_DIR}/${BENCH_HPC:-slurm}/env.sh"
bench_activate

for split in $BENCH_SPLITS; do
    for model in baseline; do
        python -m benchpkg.predict --model "$model" --cache-dir "$BENCH_CACHE" --split "$split" \
            --weights-dir "$BENCH_WEIGHTS" --device cpu \
            --out "$BENCH_RESULTS/$split/predictions_$model.csv"
    done
done
