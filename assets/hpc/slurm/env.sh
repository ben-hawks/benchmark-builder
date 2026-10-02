# Source before any benchmark step, on a login or compute node:
#     BENCH_MACHINE=<machine> source <hpc>/env.sh
#
# Machine-specific values come from profiles/$BENCH_MACHINE.sh; this file and jobs/*.sbatch
# stay machine-agnostic. Override any path by exporting it before sourcing.
# ADAPT: rename BENCH_ / bench_ to the benchmark's prefix, set the venv list and splits.

BENCH_HPC_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# Pick a profile: explicit BENCH_MACHINE, else NERSC's $NERSC_HOST, else generic.
: "${BENCH_MACHINE:=${NERSC_HOST:-generic}}"
if [ ! -f "$BENCH_HPC_DIR/profiles/$BENCH_MACHINE.sh" ]; then
    echo "env.sh: no profile $BENCH_HPC_DIR/profiles/$BENCH_MACHINE.sh" >&2
    return 1 2>/dev/null || exit 1
fi
# shellcheck disable=SC1090
source "$BENCH_HPC_DIR/profiles/$BENCH_MACHINE.sh"

: "${BENCH_DATA:=$BENCH_ROOT/data}"          # dataset snapshot (+ recorded revision)
: "${BENCH_CACHE:=$BENCH_ROOT/cache}"        # featurized splits
: "${BENCH_WEIGHTS:=$BENCH_ROOT/weights}"    # checkpoints + small derived artifacts
: "${BENCH_RESULTS:=$BENCH_ROOT/results}"    # predictions, metrics, LEADERBOARD.md, codabench/
: "${BENCH_VENV:=$BENCH_ROOT/venv-torch}"    # main stack: featurize, GPU models, scoring
: "${BENCH_VENV_ALT:=$BENCH_ROOT/venv-alt}"  # (optional) conflicting stack, e.g. TensorFlow
: "${BENCH_SPLITS:=test}"
export BENCH_MACHINE BENCH_ROOT BENCH_DATA BENCH_CACHE BENCH_WEIGHTS BENCH_RESULTS \
       BENCH_VENV BENCH_VENV_ALT BENCH_SPLITS

# Repo root (this directory lives in <repo>/<hpc>/). Jobs get it via --export from submit.sh.
: "${BENCH_REPO:=$(cd "$BENCH_HPC_DIR/.." && pwd)}"
export BENCH_REPO
export PYTHONPATH="$BENCH_REPO/src${PYTHONPATH:+:$PYTHONPATH}"

# torch_geometric -> torch._dynamo -> triton can segfault on import on CPU-only nodes;
# keep dynamo out of inference. Quiet TF/oneDNN. Unbuffered logs for Slurm .out files.
export TORCHDYNAMO_DISABLE=1 TF_CPP_MIN_LOG_LEVEL=3 PYTHONUNBUFFERED=1

bench_activate() {
    bench_load_torch_stack
    # shellcheck disable=SC1091
    source "$BENCH_VENV/bin/activate"
}

bench_activate_alt() {
    bench_load_plain_python
    # shellcheck disable=SC1091
    source "$BENCH_VENV_ALT/bin/activate"
}
