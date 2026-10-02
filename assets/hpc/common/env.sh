# Source before any benchmark step, on a login or compute node:
#     BENCH_MACHINE=<machine> source <hpc>/env.sh
#
# Scheduler-neutral: the same file serves Slurm (assets/hpc/slurm/) and PBS (assets/hpc/pbs/)
# job chains. Cluster-specific values come from profiles/$BENCH_MACHINE.sh and benchmark-stack
# hooks from stack.sh; this file and the job scripts stay generic. Override any path by
# exporting it before sourcing.
# ADAPT: rename BENCH_ / bench_ to the benchmark's prefix, set the splits, drop the alt venv
# if the benchmark has a single software stack.

BENCH_HPC_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# Pick a profile: explicit BENCH_MACHINE, else NERSC's $NERSC_HOST, else generic.
: "${BENCH_MACHINE:=${NERSC_HOST:-generic}}"
if [ ! -f "$BENCH_HPC_DIR/profiles/$BENCH_MACHINE.sh" ]; then
    echo "env.sh: no profile $BENCH_HPC_DIR/profiles/$BENCH_MACHINE.sh" >&2
    return 1 2>/dev/null || exit 1
fi
# shellcheck disable=SC1090
source "$BENCH_HPC_DIR/profiles/$BENCH_MACHINE.sh"
# shellcheck disable=SC1091
source "$BENCH_HPC_DIR/stack.sh"

: "${BENCH_DATA:=$BENCH_ROOT/data}"          # dataset snapshot (+ recorded revision)
: "${BENCH_CACHE:=$BENCH_ROOT/cache}"        # (optional) preprocessed splits, format chosen by the benchmark
: "${BENCH_WEIGHTS:=$BENCH_ROOT/weights}"    # checkpoints + small derived artifacts
: "${BENCH_RESULTS:=$BENCH_ROOT/results}"    # predictions, metrics, LEADERBOARD.md, codabench/
: "${BENCH_VENV:=$BENCH_ROOT/venv-main}"     # main environment: preprocessing, models, scoring
: "${BENCH_VENV_ALT:=$BENCH_ROOT/venv-alt}"  # (optional) a stack that conflicts with the main one
: "${BENCH_SPLITS:=test}"
: "${BENCH_PYTHON:=python3}"           # interpreter venvs are built from (after loading the stack modules)
export BENCH_MACHINE BENCH_ROOT BENCH_DATA BENCH_CACHE BENCH_WEIGHTS BENCH_RESULTS \
       BENCH_VENV BENCH_VENV_ALT BENCH_SPLITS BENCH_PYTHON

# Repo root (this directory lives in <repo>/<hpc>/). Jobs get it via --export from submit.sh.
: "${BENCH_REPO:=$(cd "$BENCH_HPC_DIR/.." && pwd)}"
export BENCH_REPO
export PYTHONPATH="$BENCH_REPO/src${PYTHONPATH:+:$PYTHONPATH}"

# Unbuffered output so job log files show progress as it happens.
export PYTHONUNBUFFERED=1
bench_stack_env

bench_activate() {
    bench_load_main_stack
    # shellcheck disable=SC1091
    source "$BENCH_VENV/bin/activate"
}

bench_activate_alt() {
    bench_load_alt_stack
    # shellcheck disable=SC1091
    source "$BENCH_VENV_ALT/bin/activate"
}
