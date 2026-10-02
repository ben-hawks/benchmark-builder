# Machine profile: NERSC Perlmutter (worked example; see references/hpc.md).
# Sourced by env.sh. Every cluster-specific value lives here, never in jobs/*.sbatch.
# The scheduler, filesystem and network facts were verified 2026-10-02 with axess-benchmark
# (Slurm jobs 59209565-68). Resource sizes and the software lines are per benchmark: set
# them from this benchmark's measured needs and its own stack.

BENCH_MACHINE=perlmutter

# --- filesystems ---------------------------------------------------------------
# $SCRATCH is purged for files not accessed in 8 weeks. Copy results worth keeping to
# CFS (/global/cfs/cdirs/<project>/...) or export BENCH_ROOT there before sourcing.
: "${BENCH_ROOT:=$SCRATCH/<benchmark>}"

# --- scheduler -----------------------------------------------------------------
# The account can't go in #SBATCH lines (they don't expand variables), so submit.sh
# requires it on the command line: bash <hpc>/submit.sh -A <nersc_project>.
BENCH_REQUIRE_ACCOUNT=1
# Per-job resources, passed to sbatch on the command line by submit.sh. Perlmutter syntax:
# --constraint=cpu|gpu, --qos=shared|regular|debug, --gpus / --gpus-per-node. The sizes are
# placeholders: size each job from this benchmark's data and models.
BENCH_SB_FEATURIZE="--constraint=cpu --qos=shared --cpus-per-task=<n> --mem=<mem> --time=<hh:mm:ss>"
BENCH_SB_INFER_CPU="--constraint=cpu --qos=shared --cpus-per-task=<n> --mem=<mem> --time=<hh:mm:ss>"
BENCH_SB_INFER_GPU="--constraint=gpu --qos=shared --gpus=<n> --cpus-per-task=<n> --time=<hh:mm:ss>"
BENCH_SB_TRAIN="--constraint=gpu --qos=regular --nodes=<n> --gpus-per-node=<n> --cpus-per-task=<n> --time=<hh:mm:ss>"
BENCH_SB_SCORE="--constraint=cpu --qos=shared --cpus-per-task=<n> --mem=<mem> --time=<hh:mm:ss>"

# --- network -------------------------------------------------------------------
# Compute nodes can reach the internet, but downloads still run on the login node in
# setup.sh so jobs never depend on it.
BENCH_COMPUTE_HAS_INTERNET=1

# --- GPUs ------------------------------------------------------------------------
# NVIDIA A100. BENCH_GPU_DEVICE is the device name this benchmark's code takes for them
# (e.g. "cuda" for PyTorch); set it for the benchmark's framework.
: "${BENCH_GPU_DEVICE:=<device>}"
bench_gpu_info() { nvidia-smi --query-gpu=name,driver_version --format=csv,noheader || true; }

# --- software ------------------------------------------------------------------
# Modules each venv is layered on. Leave empty to build venvs on the default python.
# Example (axess-benchmark): the main venv used NERSC's CUDA build of PyTorch,
#   BENCH_MAIN_MODULE=pytorch/2.6.0 and BENCH_VENV_SYSTEM_SITE=1 (venv --system-site-packages),
# and a separate TensorFlow venv on `module load python`. Check versions with `module avail`.
: "${BENCH_MAIN_MODULE:=}"
: "${BENCH_ALT_MODULE:=python}"
: "${BENCH_VENV_SYSTEM_SITE:=0}"
bench_load_main_stack() { if [ -n "$BENCH_MAIN_MODULE" ]; then module load "$BENCH_MAIN_MODULE"; else module load python; fi; }
bench_unload_main_stack() { if [ -n "$BENCH_MAIN_MODULE" ]; then module unload "$BENCH_MAIN_MODULE"; fi; }
bench_load_alt_stack() { module load "$BENCH_ALT_MODULE"; }
