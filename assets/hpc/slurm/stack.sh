# Benchmark software-stack hooks, sourced by env.sh after the machine profile.
#
# Machine profiles (profiles/*.sh) describe the cluster. This file describes the
# BENCHMARK's software stack: environment variables its frameworks need, and fixes to apply
# after installing its requirements. Every hook is empty by default. Fill them only with
# problems actually found for this benchmark's stack (record each in docs/<MACHINE>.md),
# never with fixes copied from another benchmark.
#
# ADAPT: rename BENCH_ / bench_ to the benchmark's prefix.

# Environment the benchmark's stack needs in every job, e.g. framework flags or log levels.
bench_stack_env() {
    :
    # Example (axess-benchmark, PyTorch Geometric + TensorFlow): importing torch_geometric
    # pulled in torch._dynamo -> triton, which segfaulted on CPU-only Perlmutter nodes, and
    # TensorFlow logged noisily:
    #   export TORCHDYNAMO_DISABLE=1 TF_CPP_MIN_LOG_LEVEL=3
}

# Fixes to run after `pip install -r <requirements>` into a venv. $1 is "main" or "alt",
# $2 the venv path.
bench_post_install() {
    :
    # Example (axess-benchmark): the CPU-only alt venv didn't need triton, which segfaulted
    # on import:
    #   [ "$1" = alt ] && "$2/bin/pip" uninstall -y triton || true
}

# A one-line import check for each venv after installing, so a broken environment fails in
# setup.sh rather than in a queued job. $1 is "main" or "alt", $2 the venv path.
bench_check_env() {
    "$2/bin/python" -c "import benchpkg; print('benchpkg ok')"
    # Example (axess-benchmark, main venv): also report the framework build it got:
    #   "$2/bin/python" -c "import torch; print('torch', torch.__version__, 'cuda', torch.version.cuda)"
}
