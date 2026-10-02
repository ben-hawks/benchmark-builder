# Machine profile TEMPLATE. Copy to profiles/<machine>.sh and fill in every value from the
# answers to the questions in references/hpc.md ("What to ask per machine"). Don't guess:
# a wrong partition or module name fails at submit time, but a wrong filesystem choice
# (purged scratch) loses results silently weeks later.

BENCH_MACHINE="<machine>"   # profile name; file is profiles/<machine>.sh

# --- filesystems ---------------------------------------------------------------
# Where caches/results/venvs live. Note purge policy and quota in docs/<MACHINE>.md.
: "${BENCH_ROOT:=<scratch or project path>/<benchmark>}"

# --- scheduler -----------------------------------------------------------------
BENCH_REQUIRE_ACCOUNT=1     # 0 if the site has no accounts/allocations
# Partition/qos names, --constraint, GPU syntax (--gpus=N | --gres=gpu:N | --gpus-per-node=N),
# shared vs exclusive, wall-time limits: all per job, on the sbatch command line.
BENCH_SB_FEATURIZE="--partition=<cpu> --cpus-per-task=32 --mem=64G --time=00:30:00"
BENCH_SB_INFER_CPU="--partition=<cpu> --cpus-per-task=16 --mem=32G --time=01:00:00"
BENCH_SB_INFER_GPU="--partition=<gpu> --gres=gpu:1 --cpus-per-task=8 --time=00:30:00"
BENCH_SB_TRAIN="--partition=<gpu> --nodes=1 --gres=gpu:4 --cpus-per-task=32 --time=12:00:00"
BENCH_SB_SCORE="--partition=<cpu> --cpus-per-task=4 --mem=16G --time=00:20:00"

# --- network -------------------------------------------------------------------
BENCH_COMPUTE_HAS_INTERNET=0  # if 0, setup.sh must download everything on a login node

# --- software ------------------------------------------------------------------
# One of: site module + venv, conda env, or container (podman-hpc, Apptainer/Singularity,
# Shifter). For a container, have bench_load_torch_stack set BENCH_RUN, e.g.
#   BENCH_RUN="apptainer exec --nv $BENCH_ROOT/bench.sif"
: "${BENCH_TORCH_MODULE:=}"
bench_load_torch_stack() { [ -n "$BENCH_TORCH_MODULE" ] && module load "$BENCH_TORCH_MODULE" || true; }
bench_unload_torch_stack() { [ -n "$BENCH_TORCH_MODULE" ] && module unload "$BENCH_TORCH_MODULE" || true; }
bench_load_plain_python() { module load python 2>/dev/null || true; }
BENCH_TORCH_VENV_SYSTEM_SITE=0  # 1 when layering the venv on a module that provides torch
