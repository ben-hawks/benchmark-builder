#!/bin/bash
# One-time setup on a LOGIN node: build the venvs, download the dataset and the weights
# into $BENCH_ROOT. All downloads happen here; jobs never download anything.
#
#     BENCH_MACHINE=<machine> bash <hpc>/setup.sh            # everything
#     BENCH_MACHINE=<machine> bash <hpc>/setup.sh envs       # just the venvs
#     ... data | weights
# ADAPT: requirements file names; drop step_envs' second venv if there's one stack.
set -euo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/env.sh"
mkdir -p "$BENCH_ROOT"

step_envs() {
    echo "== main venv ($BENCH_VENV) on $BENCH_MACHINE"
    bench_load_torch_stack
    if [ "${BENCH_TORCH_VENV_SYSTEM_SITE:-0}" = 1 ]; then
        python -m venv --system-site-packages "$BENCH_VENV"   # reuse the site's CUDA torch
    else
        python -m venv "$BENCH_VENV"
    fi
    "$BENCH_VENV/bin/pip" install --upgrade pip
    "$BENCH_VENV/bin/pip" install -r "$BENCH_REPO/requirements.txt" pytest
    "$BENCH_VENV/bin/python" -c "import torch; print('torch', torch.__version__, 'cuda', torch.version.cuda)"
    bench_unload_torch_stack

    if [ -f "$BENCH_REPO/requirements-alt.txt" ]; then
        echo "== separate venv ($BENCH_VENV_ALT): stack that must not share the main torch"
        bench_load_plain_python
        python -m venv "$BENCH_VENV_ALT"
        "$BENCH_VENV_ALT/bin/pip" install --upgrade pip
        "$BENCH_VENV_ALT/bin/pip" install -r "$BENCH_REPO/requirements-alt.txt"
        # triton can segfault on import on CPU-only nodes; CPU-only envs don't need it.
        "$BENCH_VENV_ALT/bin/pip" uninstall -y triton || true
    fi
}

step_data() {
    echo "== dataset -> $BENCH_DATA"
    "$BENCH_VENV/bin/python" "$BENCH_REPO/scripts/fetch_data.py" --out "$BENCH_DATA"
}

step_weights() {
    echo "== weights -> $BENCH_WEIGHTS (sha256-checked)"
    "$BENCH_VENV/bin/python" "$BENCH_REPO/scripts/fetch_weights.py" --out "$BENCH_WEIGHTS"
}

case "${1:-all}" in
    envs) step_envs ;;
    data) step_data ;;
    weights) step_weights ;;
    all) step_envs; step_data; step_weights ;;
    *) echo "usage: $0 [all|envs|data|weights]"; exit 2 ;;
esac
echo "done. Next: run the golden tests (references/hpc.md), then bash <hpc>/submit.sh -A <account>"
