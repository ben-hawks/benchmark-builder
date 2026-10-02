# Machine profile: OLCF Frontier (Slurm). *** UNVERIFIED ***
# No benchmark built with this skill has run on Frontier yet. The facts below come from the
# genesis `frontier` skill (AI-ModCon/genesis-skills@b7e8434, hpc-skills/frontier); everything
# marked <...> is not covered there. Before using this profile:
#   1. load the latest genesis `frontier` skill and OLCF's user docs, and re-check every value;
#   2. fill the placeholders from the user's answers and the site docs;
#   3. run the golden tests on a compute node, then record the run in docs/FRONTIER.md and
#      replace this header with "verified <date> with <benchmark> (jobs ...)".

BENCH_MACHINE=frontier

# --- filesystems ---------------------------------------------------------------
# Skill: $MEMBERWORK (Lustre Orion, 50 TB, 90-day purge of files not accessed) for job I/O,
# $PROJWORK (no purge) for shared project data, home 50 GB for code. The exact directory form
# under $MEMBERWORK (per project) isn't settled by the skill: <check OLCF docs>. Copy results
# worth keeping to $PROJWORK, or point BENCH_ROOT there.
: "${BENCH_ROOT:=<\$MEMBERWORK or \$PROJWORK path>/<benchmark>}"

# --- scheduler -----------------------------------------------------------------
# Skill: -A <project> required; the only partition is batch; QOS debug (2 h, 1 running job,
# <= 2 nodes), regular (24 h), extended (> 24 h, needs approval); at most 100 queued jobs.
# 8 of 64 cores per node are reserved (--core-spec=8), so 56 are allocatable. Nodes have
# 4 MI250X = 8 GCDs; the skill's examples request GPUs per task (--gpus-per-task=1).
# Sizes and wall times are placeholders: set them from this benchmark's measured needs.
BENCH_REQUIRE_ACCOUNT=1
BENCH_SB_FEATURIZE="-p batch --qos=<debug|regular> --nodes=1 --cpus-per-task=<n<=56> --time=<hh:mm:ss>"
BENCH_SB_INFER_CPU="-p batch --qos=<debug|regular> --nodes=1 --cpus-per-task=<n<=56> --time=<hh:mm:ss>"
BENCH_SB_INFER_GPU="-p batch --qos=<debug|regular> --nodes=1 --gpus-per-node=<n<=8> --cpus-per-task=<n> --time=<hh:mm:ss>"
BENCH_SB_TRAIN="-p batch --qos=regular --nodes=<n> --gpus-per-node=8 --cpus-per-task=<n> --time=<hh:mm:ss>"
BENCH_SB_SCORE="-p batch --qos=<debug|regular> --nodes=1 --cpus-per-task=<n<=56> --time=<hh:mm:ss>"

# --- network -------------------------------------------------------------------
# <not in the skill: check OLCF docs for compute-node internet / proxy settings>. Downloads
# run on the login node in setup.sh either way.
BENCH_COMPUTE_HAS_INTERNET=0

# --- GPUs ------------------------------------------------------------------------
# Skill: AMD MI250X (ROCm/HIP), 64 GB HBM per GCD. BENCH_GPU_DEVICE is the name the
# benchmark's framework uses (PyTorch's ROCm build keeps the name cuda).
: "${BENCH_GPU_DEVICE:=<device, e.g. cuda for PyTorch on ROCm>}"
bench_gpu_info() { rocm-smi --showproductname 2>/dev/null || true; }

# --- software ------------------------------------------------------------------
# Skill: Cray PE (PrgEnv-amd / PrgEnv-gnu), `module load rocm/<version>` (its examples use
# 5.7.1; list what's installed with `module avail rocm`). The skill doesn't cover Python or
# ML framework modules: <ask the user / OLCF docs how this benchmark's framework is provided
# for ROCm (module, conda env or container)>, and whether to layer a venv on it.
: "${BENCH_ROCM_MODULE:=rocm}"
: "${BENCH_MAIN_MODULE:=}"
: "${BENCH_ALT_MODULE:=}"
: "${BENCH_VENV_SYSTEM_SITE:=0}"
bench_load_main_stack() { module load "$BENCH_ROCM_MODULE"; if [ -n "$BENCH_MAIN_MODULE" ]; then module load "$BENCH_MAIN_MODULE"; fi; }
bench_unload_main_stack() { if [ -n "$BENCH_MAIN_MODULE" ]; then module unload "$BENCH_MAIN_MODULE"; fi; }
bench_load_alt_stack() { if [ -n "$BENCH_ALT_MODULE" ]; then module load "$BENCH_ALT_MODULE"; fi; }
