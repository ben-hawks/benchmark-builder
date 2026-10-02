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
# shared vs exclusive, wall-time limits: all per job, on the sbatch command line. Size each
# job from the benchmark's data and models.
BENCH_SB_FEATURIZE="--partition=<cpu> --cpus-per-task=<n> --mem=<mem> --time=<hh:mm:ss>"
BENCH_SB_INFER_CPU="--partition=<cpu> --cpus-per-task=<n> --mem=<mem> --time=<hh:mm:ss>"
BENCH_SB_INFER_GPU="--partition=<gpu> --gres=gpu:<n> --cpus-per-task=<n> --time=<hh:mm:ss>"
BENCH_SB_TRAIN="--partition=<gpu> --nodes=<n> --gres=gpu:<n> --cpus-per-task=<n> --time=<hh:mm:ss>"
BENCH_SB_SCORE="--partition=<cpu> --cpus-per-task=<n> --mem=<mem> --time=<hh:mm:ss>"

# --- network -------------------------------------------------------------------
BENCH_COMPUTE_HAS_INTERNET=0  # if 0, setup.sh must download everything on a login node

# --- GPUs ------------------------------------------------------------------------
# Vendor and model (NVIDIA, AMD, Intel, ...), and the device name the benchmark's framework
# uses for them.
: "${BENCH_GPU_DEVICE:=<device>}"
bench_gpu_info() { :; }     # e.g. nvidia-smi --query-gpu=name --format=csv,noheader, or rocm-smi

# --- software ------------------------------------------------------------------
# One of: site module + venv, conda env, or container (podman-hpc, Apptainer/Singularity,
# Shifter). For a container, have bench_load_main_stack set BENCH_RUN, e.g.
#   BENCH_RUN="apptainer exec --nv $BENCH_ROOT/bench.sif"
: "${BENCH_MAIN_MODULE:=}"        # module the main venv is layered on, if any
: "${BENCH_ALT_MODULE:=}"         # module the alt venv is layered on, if any
: "${BENCH_VENV_SYSTEM_SITE:=0}"  # 1 to let the main venv see the module's packages
# BENCH_PYTHON=python3            # interpreter venvs are built from, if python3 isn't right here
bench_load_main_stack() { if [ -n "$BENCH_MAIN_MODULE" ]; then module load "$BENCH_MAIN_MODULE"; fi; }
bench_unload_main_stack() { if [ -n "$BENCH_MAIN_MODULE" ]; then module unload "$BENCH_MAIN_MODULE"; fi; }
bench_load_alt_stack() { if [ -n "$BENCH_ALT_MODULE" ]; then module load "$BENCH_ALT_MODULE"; fi; }
