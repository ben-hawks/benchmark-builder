#!/bin/bash
# Pipeline contract, last step (references/repo-structure.md): write truth CSVs, score every
# predictions_*.csv under $BENCH_RESULTS/<split>/, build $BENCH_RESULTS/LEADERBOARD.md, then
# package every model with predictions for all submission splits as an upload-ready
# Codabench zip in $BENCH_RESULTS/codabench/.
#
# Runs unchanged on a laptop and as the final Slurm job. Needs BENCH_CACHE, BENCH_RESULTS,
# BENCH_SPLITS and the package importable (pip install -e . or PYTHONPATH=src).
#
# ADAPT: rename BENCH_ to the benchmark's prefix and benchpkg to its package; change the
# cache filename pattern and the truth/score arguments to match this benchmark; drop the
# submission step if there is no Codabench competition.
set -euo pipefail
: "${BENCH_SPLITS:=test}"

for split in $BENCH_SPLITS; do
    dir="$BENCH_RESULTS/$split"
    mkdir -p "$dir"
    python -m benchpkg.truth --cache "$BENCH_CACHE/$split.npz" --out "$dir/truth.csv"
    shopt -s nullglob
    for pred in "$dir"/predictions_*.csv; do
        name=$(basename "$pred" .csv); name=${name#predictions_}
        python -m benchpkg.score --pred "$pred" --truth "$dir/truth.csv" \
            --out "$dir/$name" --title "$name on $split" > /dev/null
        echo "scored $split/$name"
    done
done
python -m benchpkg.report --results "$BENCH_RESULTS" --out "$BENCH_RESULTS/LEADERBOARD.md"

# Codabench submission zips: a submission needs every submission split.
missing=0
for split in $BENCH_SPLITS; do
    [ -f "$BENCH_CACHE/$split.npz" ] || missing=1
done
if [ "$missing" = 0 ]; then
    python -m benchpkg.submission --results "$BENCH_RESULTS" --cache-dir "$BENCH_CACHE"
else
    echo "skipping Codabench submissions: need a cache for every split in BENCH_SPLITS ($BENCH_SPLITS)"
fi
