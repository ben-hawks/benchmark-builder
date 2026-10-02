#!/bin/bash
# Submit the benchmark as a PBS dependency chain (pipeline contract,
# references/repo-structure.md). Same chain as the Slurm version:
#
#   featurize --> [train] --> infer_gpu --+
#                                         +--> score (score_all.sh: truth, metrics,
#   (after featurize)   infer_cpu --------+     leaderboard, Codabench zips)
#
# ADAPT: drop the featurize job (and point the others at raw data) if the benchmark has no
# cache step, and the weights check if it has no pretrained weights.
#
# Usage, from the repo root on a login node, after setup.sh and the golden tests:
#     BENCH_MACHINE=<machine> bash <hpc>/submit.sh -A <project> [--train] [--no-gpu] [--no-cpu] [qsub args...]
# Other arguments pass through to every qsub call (e.g. -q debug). Per-job resources come
# from the machine profile (BENCH_QS_*). #PBS lines can't expand variables, so the account
# and resources go on the command line and the repo path goes through qsub -v.
# For scheduler commands and troubleshooting (qstat -f, qstat -xf, held jobs), load the
# genesis `pbs` skill and, for the site, its site skill (references/genesis-skills.md).
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.."
HPC_DIR="$(basename "$(dirname "${BASH_SOURCE[0]}")")"
source "$HPC_DIR/env.sh"

RUN_TRAIN=0 RUN_GPU=1 RUN_CPU=1
QS_ARGS=()
for a in "$@"; do
    case "$a" in
        --train) RUN_TRAIN=1 ;;
        --no-gpu) RUN_GPU=0 ;;
        --no-cpu) RUN_CPU=0 ;;
        *) QS_ARGS+=("$a") ;;
    esac
done
if [ "${BENCH_REQUIRE_ACCOUNT:-1}" = 1 ] && ! printf '%s\n' "${QS_ARGS[@]:-}" | grep -qE '^-A'; then
    echo "error: pass your project, e.g. bash $HPC_DIR/submit.sh -A <project>" >&2
    exit 2
fi
[ -e "$BENCH_DATA" ] || { echo "error: missing $BENCH_DATA -- run: bash $HPC_DIR/setup.sh" >&2; exit 1; }
if [ "$RUN_TRAIN" = 0 ]; then
    [ -e "$BENCH_WEIGHTS" ] || { echo "error: missing $BENCH_WEIGHTS -- run: bash $HPC_DIR/setup.sh weights" >&2; exit 1; }
fi

# qsub prints the job ID (e.g. 12345.<server>), which -W depend= takes as is.
# qsub -v values can't contain commas; keep the repo path free of them.
# shellcheck disable=SC2086
qs() { local res="$1"; shift; qsub -v "BENCH_REPO=$PWD,BENCH_HPC=$HPC_DIR,BENCH_MACHINE=$BENCH_MACHINE" $res "${QS_ARGS[@]}" "$@"; }

feat=$(qs "$BENCH_QS_FEATURIZE" "$HPC_DIR/jobs/featurize.pbs")
after="afterok:$feat"
if [ "$RUN_TRAIN" = 1 ]; then
    train=$(qs "$BENCH_QS_TRAIN" -W depend="$after" "$HPC_DIR/jobs/train.pbs")
    after="afterok:$train"
fi
deps=""
if [ "$RUN_GPU" = 1 ]; then
    gpu=$(qs "$BENCH_QS_INFER_GPU" -W depend="$after" "$HPC_DIR/jobs/infer_gpu.pbs")
    deps="$deps:$gpu"
fi
if [ "$RUN_CPU" = 1 ]; then
    cpu=$(qs "$BENCH_QS_INFER_CPU" -W depend="afterok:$feat" "$HPC_DIR/jobs/infer_cpu.pbs")
    deps="$deps:$cpu"
fi
score=$(qs "$BENCH_QS_SCORE" -W depend="afterok${deps:-:$feat}" "$HPC_DIR/jobs/score.pbs")

echo "featurize=$feat ${train:+train=$train }${gpu:+infer_gpu=$gpu }${cpu:+infer_cpu=$cpu }score=$score"
echo "results -> $BENCH_RESULTS/LEADERBOARD.md   (watch: qstat -u \$USER)"
