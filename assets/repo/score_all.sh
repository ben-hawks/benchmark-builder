#!/bin/bash
# Pipeline contract, last step (references/repo-structure.md): write truth files, score every
# predictions_*.csv under $BENCH_RESULTS/<split>/, build $BENCH_RESULTS/LEADERBOARD.md, then
# package every model with predictions for all submission splits as an upload-ready
# Codabench zip in $BENCH_RESULTS/codabench/.
#
# Runs unchanged on a laptop and as the final Slurm job. Needs BENCH_CACHE (or wherever the
# truth module reads ground truth from), BENCH_RESULTS, BENCH_SPLITS, and the package
# importable (pip install -e . or PYTHONPATH=src).
#
# ADAPT: rename BENCH_ to the benchmark's prefix and benchpkg to its package; match the
# truth/score arguments to this benchmark's modules; drop the submission step if there is
# no Codabench competition.
set -euo pipefail
: "${BENCH_SPLITS:=test}"

for split in $BENCH_SPLITS; do
    dir="$BENCH_RESULTS/$split"
    mkdir -p "$dir"
    python -m benchpkg.truth --cache-dir "$BENCH_CACHE" --split "$split" --out "$dir/truth.csv"
    shopt -s nullglob
    for pred in "$dir"/predictions_*.csv; do
        name=$(basename "$pred" .csv); name=${name#predictions_}
        python -m benchpkg.score --pred "$pred" --truth "$dir/truth.csv" \
            --out "$dir/$name" --title "$name on $split" > /dev/null
        echo "scored $split/$name"
    done
done
python -m benchpkg.report --results "$BENCH_RESULTS" --out "$BENCH_RESULTS/LEADERBOARD.md"

# Codabench submission zips (a model is packaged only if it has predictions for every
# submission split; incomplete models are reported and make this step exit non-zero).
python -m benchpkg.submission --results "$BENCH_RESULTS" --cache-dir "$BENCH_CACHE"

# Optional: track these results in AmSC MLflow (the amsc-mlflow skill). Prefer running this
# from a login node after the job instead (no token in the queue); see references/hpc.md.
# if [ -n "${BENCH_MLFLOW_SKILL:-}" ]; then
#     python "$BENCH_MLFLOW_SKILL/scripts/log_benchmark_results.py" --benchmark <name> \
#         --results "$BENCH_RESULTS" --repo "$BENCH_REPO" --auxiliary <auxiliary models>
# fi
