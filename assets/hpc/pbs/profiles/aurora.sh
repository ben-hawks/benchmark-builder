# Machine profile: ALCF Aurora (PBS). *** UNVERIFIED ***
# No benchmark built with this skill has run on Aurora yet. The facts below come from the
# genesis `aurora` skill (AI-ModCon/genesis-skills@b7e8434, hpc-skills/aurora); everything
# marked <...> is not covered there. Before using this profile:
#   1. load the latest genesis `aurora` skill and ALCF's user docs, and re-check every value;
#   2. fill the placeholders from the user's answers and the site docs;
#   3. run the golden tests on a compute node, then record the run in docs/AURORA.md and
#      replace this header with "verified <date> with <benchmark> (jobs ...)".

BENCH_MACHINE=aurora

# --- filesystems ---------------------------------------------------------------
# Skill: home (/home/<user>, 100 GB, for code) and Flare (Lustre, /lus/flare/projects/<project>/,
# primary job I/O, no purge listed). Every filesystem a job touches must be declared with
# -l filesystems=<tokens> (home, flare, grand, eagle), or the job fails at startup.
: "${BENCH_ROOT:=/lus/flare/projects/<project>/$USER/<benchmark>}"

# --- scheduler -----------------------------------------------------------------
# Skill: -A <project> is required; queues debug (<= 10 nodes, 1 h, 1 running + 1 queued
# job, so a whole chain doesn't fit in debug; use it to test one job), prod
# (<= 496 nodes, 24 h), prod-large (needs approval). Nodes are requested whole in the
# skill's examples (select=1:ncpus=104:ngpus=6); a CPU-only job still occupies a GPU node.
# Sizes and wall times are placeholders: set them from this benchmark's measured needs.
BENCH_REQUIRE_ACCOUNT=1
BENCH_FS="-l filesystems=home:flare"
BENCH_QS_FEATURIZE="-q <debug|prod> -l select=1:ncpus=104 -l walltime=<hh:mm:ss> $BENCH_FS"
BENCH_QS_INFER_CPU="-q <debug|prod> -l select=1:ncpus=104 -l walltime=<hh:mm:ss> $BENCH_FS"
BENCH_QS_INFER_GPU="-q <debug|prod> -l select=1:ncpus=104:ngpus=6 -l walltime=<hh:mm:ss> $BENCH_FS"
BENCH_QS_TRAIN="-q prod -l select=<nodes>:ncpus=104:ngpus=6 -l walltime=<hh:mm:ss> $BENCH_FS"
BENCH_QS_SCORE="-q <debug|prod> -l select=1:ncpus=104 -l walltime=<hh:mm:ss> $BENCH_FS"

# --- network -------------------------------------------------------------------
# <not in the skill: check ALCF docs for compute-node internet / proxy settings>. Downloads
# run on the login node in setup.sh either way.
BENCH_COMPUTE_HAS_INTERNET=0

# --- GPUs ------------------------------------------------------------------------
# Skill: 6 Intel Data Center GPU Max (Ponte Vecchio) per node; select GPUs per process with
# ZE_AFFINITY_MASK, launch multi-process work with mpiexec (there is no srun).
# BENCH_GPU_DEVICE is the name the benchmark's framework uses (PyTorch: xpu).
: "${BENCH_GPU_DEVICE:=<device, e.g. xpu>}"
bench_gpu_info() { xpu-smi discovery 2>/dev/null || sycl-ls 2>/dev/null || true; }

# --- software ------------------------------------------------------------------
# Skill: `module use /soft/modulefiles` for the Spack PE; `module load python` exists. The
# skill doesn't cover ML framework modules: <ask the user / ALCF docs which module provides
# this benchmark's framework for Intel GPUs>, and whether to layer a venv on it.
: "${BENCH_MAIN_MODULE:=}"
: "${BENCH_ALT_MODULE:=python}"
: "${BENCH_VENV_SYSTEM_SITE:=0}"
bench_load_main_stack() { module use /soft/modulefiles; if [ -n "$BENCH_MAIN_MODULE" ]; then module load "$BENCH_MAIN_MODULE"; else module load python; fi; }
bench_unload_main_stack() { if [ -n "$BENCH_MAIN_MODULE" ]; then module unload "$BENCH_MAIN_MODULE"; fi; }
bench_load_alt_stack() { module load "$BENCH_ALT_MODULE"; }
