# Machine profile TEMPLATE for a PBS / OpenPBS cluster. Copy to profiles/<machine>.sh and fill
# in every value. If the genesis HPC skills cover this machine (the `pbs` skill for the
# scheduler, a site skill such as `aurora`), load them first and pre-fill from them; ask the
# user only for what they don't answer (references/hpc.md, "What to ask per machine").
# Don't guess: a wrong queue or resource name fails at submit time, but a wrong filesystem
# choice (purged scratch) loses results silently weeks later.

BENCH_MACHINE="<machine>"   # profile name; file is profiles/<machine>.sh

# --- filesystems ---------------------------------------------------------------
# Where caches/results/venvs live. Note purge policy and quota in docs/<MACHINE>.md.
: "${BENCH_ROOT:=<scratch or project path>/<benchmark>}"

# --- scheduler -----------------------------------------------------------------
BENCH_REQUIRE_ACCOUNT=1     # 0 if the site has no projects/allocations (-A)
# Queue (-q), resource chunks (-l select=<nodes>:ncpus=<n>:ngpus=<n>:mem=<mem>), wall time
# (-l walltime=), and any site-required resources (e.g. Aurora's -l filesystems=): all per
# job, on the qsub command line, because #PBS lines can't expand variables. Size each job
# from the benchmark's data and models.
BENCH_QS_FEATURIZE="-q <queue> -l select=1:ncpus=<n>:mem=<mem> -l walltime=<hh:mm:ss>"
BENCH_QS_INFER_CPU="-q <queue> -l select=1:ncpus=<n>:mem=<mem> -l walltime=<hh:mm:ss>"
BENCH_QS_INFER_GPU="-q <queue> -l select=1:ncpus=<n>:ngpus=<n> -l walltime=<hh:mm:ss>"
BENCH_QS_TRAIN="-q <queue> -l select=<nodes>:ncpus=<n>:ngpus=<n> -l walltime=<hh:mm:ss>"
BENCH_QS_SCORE="-q <queue> -l select=1:ncpus=<n>:mem=<mem> -l walltime=<hh:mm:ss>"

# --- network -------------------------------------------------------------------
BENCH_COMPUTE_HAS_INTERNET=0  # if 0, setup.sh must download everything on a login node

# --- GPUs ------------------------------------------------------------------------
# Vendor and model (NVIDIA, AMD, Intel, ...), and the device name the benchmark's framework
# uses for them (e.g. PyTorch: cuda for NVIDIA and ROCm builds, xpu for Intel).
: "${BENCH_GPU_DEVICE:=<device>}"
bench_gpu_info() { :; }     # e.g. nvidia-smi -L, rocm-smi, xpu-smi discovery

# --- software ------------------------------------------------------------------
# One of: site module + venv, conda env, or container (Apptainer/Singularity, podman). For a
# container, have bench_load_main_stack set BENCH_RUN, e.g.
#   BENCH_RUN="apptainer exec $BENCH_ROOT/bench.sif"
: "${BENCH_MAIN_MODULE:=}"        # module the main venv is layered on, if any
: "${BENCH_ALT_MODULE:=}"         # module the alt venv is layered on, if any
: "${BENCH_VENV_SYSTEM_SITE:=0}"  # 1 to let the main venv see the module's packages
# BENCH_PYTHON=python3            # interpreter venvs are built from, if python3 isn't right here
bench_load_main_stack() { if [ -n "$BENCH_MAIN_MODULE" ]; then module load "$BENCH_MAIN_MODULE"; fi; }
bench_unload_main_stack() { if [ -n "$BENCH_MAIN_MODULE" ]; then module unload "$BENCH_MAIN_MODULE"; fi; }
bench_load_alt_stack() { if [ -n "$BENCH_ALT_MODULE" ]; then module load "$BENCH_ALT_MODULE"; fi; }
