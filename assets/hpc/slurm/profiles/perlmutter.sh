# Machine profile: NERSC Perlmutter (worked example; see references/hpc.md).
# Sourced by env.sh. Every cluster-specific value lives here, never in jobs/*.sbatch.
# Verified 2026-10-02 with axess-benchmark (Slurm jobs 59209565-68).

BENCH_MACHINE=perlmutter

# --- filesystems ---------------------------------------------------------------
# $SCRATCH is purged for files not accessed in 8 weeks. Copy results worth keeping to
# CFS (/global/cfs/cdirs/<project>/...) or export BENCH_ROOT there before sourcing.
: "${BENCH_ROOT:=$SCRATCH/<benchmark>}"

# --- scheduler -----------------------------------------------------------------
# The account can't go in #SBATCH lines (they don't expand variables), so submit.sh
# requires it on the command line: bash <hpc>/submit.sh -A <nersc_project>.
BENCH_REQUIRE_ACCOUNT=1
# Per-job resources, passed to sbatch on the command line by submit.sh.
BENCH_SB_FEATURIZE="--constraint=cpu --qos=shared --cpus-per-task=64 --mem=120G --time=00:30:00"
BENCH_SB_INFER_CPU="--constraint=cpu --qos=shared --cpus-per-task=32 --mem=60G --time=02:00:00"
BENCH_SB_INFER_GPU="--constraint=gpu --qos=shared --gpus=1 --cpus-per-task=32 --time=00:30:00"
BENCH_SB_TRAIN="--constraint=gpu --qos=regular --nodes=1 --gpus-per-node=4 --cpus-per-task=32 --time=06:00:00"
BENCH_SB_SCORE="--constraint=cpu --qos=shared --cpus-per-task=4 --mem=16G --time=00:20:00"

# --- network -------------------------------------------------------------------
# Compute nodes can reach the internet, but downloads still run on the login node in
# setup.sh so jobs never depend on it.
BENCH_COMPUTE_HAS_INTERNET=1

# --- software ------------------------------------------------------------------
# GPU-stack venv layered on the site PyTorch module (reuses NERSC's CUDA build of torch):
#   module load pytorch && python -m venv --system-site-packages <venv>
# Check installed versions with `module avail pytorch`.
: "${BENCH_TORCH_MODULE:=pytorch/2.6.0}"
bench_load_torch_stack() { module load "$BENCH_TORCH_MODULE"; }
bench_unload_torch_stack() { module unload "$BENCH_TORCH_MODULE"; }
# Plain-python base for any separate venv (e.g. TensorFlow) that must not see the module's torch.
bench_load_plain_python() { module load python; }
BENCH_TORCH_VENV_SYSTEM_SITE=1
