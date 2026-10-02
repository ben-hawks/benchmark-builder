#!/bin/bash
# Truth, metrics for every predictions_*.csv, leaderboard, Codabench zips (score_all.sh).
# Resources: BENCH_SB_SCORE.
#SBATCH --job-name=bench-score
#SBATCH --output=%x-%j.out
set -euo pipefail
# Slurm runs a spooled copy of this script, so locate env.sh through the exported repo path.
source "${BENCH_REPO:-$SLURM_SUBMIT_DIR}/${BENCH_HPC:-slurm}/env.sh"
bench_activate

bash "$BENCH_REPO/scripts/score_all.sh"
