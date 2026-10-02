#!/bin/bash
# (Optional) Preprocess each split once into $BENCH_CACHE, in whatever format the
# benchmark's cache module writes. Drop this job if the benchmark reads raw data directly.
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
        --cache-dir "$BENCH_CACHE" --workers "${SLURM_CPUS_PER_TASK:-1}"
done
