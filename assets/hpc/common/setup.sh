#!/bin/bash
# One-time setup on a LOGIN node: build the venvs, download the dataset and the weights
# into $BENCH_ROOT. All downloads happen here; jobs never download anything.
#
#     BENCH_MACHINE=<machine> bash <hpc>/setup.sh            # everything
#     BENCH_MACHINE=<machine> bash <hpc>/setup.sh envs       # just the venvs
#     ... data | weights
# ADAPT: requirements file names; drop the alt venv if the benchmark has one stack, and
# the weights step if it has no pretrained weights.
set -euo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/env.sh"
mkdir -p "$BENCH_ROOT"

make_venv() {  # make_venv <main|alt> <venv path> <requirements file> [extra pip args]
    local kind="$1" venv="$2" req="$3"; shift 3
    if [ "${BENCH_VENV_SYSTEM_SITE:-0}" = 1 ] && [ "$kind" = main ]; then
        "$BENCH_PYTHON" -m venv --system-site-packages "$venv"   # reuse packages the site module provides
    else
        "$BENCH_PYTHON" -m venv "$venv"
    fi
    "$venv/bin/pip" install --upgrade pip
    "$venv/bin/pip" install -r "$req" "$@"
    bench_post_install "$kind" "$venv"
    bench_check_env "$kind" "$venv"
}

step_envs() {
    echo "== main venv ($BENCH_VENV) on $BENCH_MACHINE"
    bench_load_main_stack
    make_venv main "$BENCH_VENV" "$BENCH_REPO/requirements.txt" pytest
    bench_unload_main_stack

    if [ -f "$BENCH_REPO/requirements-alt.txt" ]; then
        echo "== alt venv ($BENCH_VENV_ALT): the stack that can't share the main environment"
        bench_load_alt_stack
        make_venv alt "$BENCH_VENV_ALT" "$BENCH_REPO/requirements-alt.txt"
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
