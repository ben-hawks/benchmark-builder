#!/bin/bash
# Submit the benchmark as a Slurm dependency chain (pipeline contract,
# references/repo-structure.md):
#
#   featurize --> [train] --> infer_gpu --+
#                                         +--> score (score_all.sh: truth, metrics,
#   (after featurize)   infer_cpu --------+     leaderboard, Codabench zips)
#
# Usage, from the repo root on a login node, after setup.sh and the golden tests:
#     BENCH_MACHINE=<machine> bash <hpc>/submit.sh -A <account> [--train] [--no-gpu] [--no-cpu] [sbatch args...]
# Other arguments pass through to every sbatch call (e.g. -q debug). Per-job resources come
# from the machine profile (BENCH_SB_*). #SBATCH lines can't expand variables, so the account
# and resources go on the command line and the repo path goes through --export.
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.."
HPC_DIR="$(basename "$(dirname "${BASH_SOURCE[0]}")")"
source "$HPC_DIR/env.sh"

RUN_TRAIN=0 RUN_GPU=1 RUN_CPU=1
SB_ARGS=()
for a in "$@"; do
    case "$a" in
        --train) RUN_TRAIN=1 ;;
        --no-gpu) RUN_GPU=0 ;;
        --no-cpu) RUN_CPU=0 ;;
        *) SB_ARGS+=("$a") ;;
    esac
done
if [ "${BENCH_REQUIRE_ACCOUNT:-1}" = 1 ] && ! printf '%s\n' "${SB_ARGS[@]:-}" | grep -qE '^(-A|--account)'; then
    echo "error: pass your allocation, e.g. bash $HPC_DIR/submit.sh -A <account>" >&2
    exit 2
fi
[ -e "$BENCH_DATA" ] || { echo "error: missing $BENCH_DATA -- run: bash $HPC_DIR/setup.sh" >&2; exit 1; }
if [ "$RUN_TRAIN" = 0 ]; then
    [ -e "$BENCH_WEIGHTS" ] || { echo "error: missing $BENCH_WEIGHTS -- run: bash $HPC_DIR/setup.sh weights" >&2; exit 1; }
fi

# shellcheck disable=SC2086
sb() { local res="$1"; shift; sbatch --parsable --export=ALL,BENCH_REPO="$PWD",BENCH_HPC="$HPC_DIR",BENCH_MACHINE="$BENCH_MACHINE" $res "${SB_ARGS[@]}" "$@"; }

feat=$(sb "$BENCH_SB_FEATURIZE" "$HPC_DIR/jobs/featurize.sbatch")
after="afterok:$feat"
if [ "$RUN_TRAIN" = 1 ]; then
    train=$(sb "$BENCH_SB_TRAIN" --dependency="$after" "$HPC_DIR/jobs/train.sbatch")
    after="afterok:$train"
fi
deps=""
if [ "$RUN_GPU" = 1 ]; then
    gpu=$(sb "$BENCH_SB_INFER_GPU" --dependency="$after" "$HPC_DIR/jobs/infer_gpu.sbatch")
    deps="$deps:$gpu"
fi
if [ "$RUN_CPU" = 1 ]; then
    cpu=$(sb "$BENCH_SB_INFER_CPU" --dependency="afterok:$feat" "$HPC_DIR/jobs/infer_cpu.sbatch")
    deps="$deps:$cpu"
fi
score=$(sb "$BENCH_SB_SCORE" --dependency="afterok${deps:-:$feat}" "$HPC_DIR/jobs/score.sbatch")

echo "featurize=$feat ${train:+train=$train }${gpu:+infer_gpu=$gpu }${cpu:+infer_cpu=$cpu }score=$score"
echo "results -> $BENCH_RESULTS/LEADERBOARD.md   (watch: squeue --me)"
