#!/bin/bash
# Featurize each split once into $BENCH_CACHE (CPU, embarrassingly parallel).
# Resources: BENCH_SB_FEATURIZE in the machine profile (passed by submit.sh).
#SBATCH --job-name=bench-featurize
#SBATCH --output=%x-%j.out
set -euo pipefail
# Slurm runs a spooled copy of this script, so locate env.sh through the exported repo path.
source "${BENCH_REPO:-$SLURM_SUBMIT_DIR}/${BENCH_HPC:-slurm}/env.sh"
bench_activate
mkdir -p "$BENCH_CACHE"

for split in $BENCH_SPLITS; do
    python -m benchpkg.cache --data-root "$BENCH_DATA" --split "$split" \
        --out "$BENCH_CACHE/$split.npz" --workers "${SLURM_CPUS_PER_TASK:-1}"
done
