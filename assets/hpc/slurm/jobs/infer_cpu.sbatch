#!/bin/bash
# Inference for CPU-only models (often the ones needing the separate venv, e.g. TensorFlow).
# Resources: BENCH_SB_INFER_CPU. ADAPT: the model list and which venv to activate.
#SBATCH --job-name=bench-infer-cpu
#SBATCH --output=%x-%j.out
set -euo pipefail
# Slurm runs a spooled copy of this script, so locate env.sh through the exported repo path.
source "${BENCH_REPO:-$SLURM_SUBMIT_DIR}/${BENCH_HPC:-slurm}/env.sh"
bench_activate_alt

for split in $BENCH_SPLITS; do
    for model in baseline; do
        python -m benchpkg.predict --model "$model" --cache "$BENCH_CACHE/$split.npz" \
            --weights-dir "$BENCH_WEIGHTS" --device cpu \
            --out "$BENCH_RESULTS/$split/predictions_$model.csv"
    done
done
