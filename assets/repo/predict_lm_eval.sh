#!/bin/bash
# The `predict` step of an LLM benchmark (references/llm-benchmarks.md): run one model on one
# split through lm-evaluation-harness, keep lm-eval's own output as the canonical record,
# and export the pipeline contract's per-sample prediction file from it.
#
#   bash scripts/predict_lm_eval.sh <name> <split> <lm_eval model type> "<model_args>" [extra lm_eval args...]
#
#   e.g. bash scripts/predict_lm_eval.sh llama31-8b test hf \
#            "pretrained=meta-llama/Llama-3.1-8B-Instruct,revision=<commit>,dtype=bfloat16" \
#            --apply_chat_template --batch_size auto
#        bash scripts/predict_lm_eval.sh served-model test local-chat-completions \
#            "model=<served name>,base_url=<OpenAI-compatible endpoint>/chat/completions" --apply_chat_template
#
# Writes:
#   $BENCH_RESULTS/lm_eval/<name>/<split>/...      results_*.json + samples_*.jsonl (lm-eval's layout)
#   $BENCH_RESULTS/<split>/predictions_<name>.csv  sample_id, answer[, answer_norm], lm_eval_<metric>...
#   $BENCH_RESULTS/<split>/predictions_<name>.meta.json   run provenance
#
# Never pass --limit: a sample-limited run is a smoke test (the configuration-tester skill's
# job), not a result, and the export refuses it. Every run setting that changes results
# (few-shot count, chat template, decoding/gen_kwargs, seed) belongs in the task YAML or in
# this benchmark's documented protocol, so that each reference model is run the same way.
#
# ADAPT: rename BENCH_/benchpkg; TASK naming (one lm-eval task per benchmark split, here
# <task>_<split>); the fixed protocol flags below.
set -euo pipefail
[ $# -ge 4 ] || { sed -n '2,13p' "$0"; exit 2; }
name="$1" split="$2" model_type="$3" model_args="$4"; shift 4
TASK="<task>_${split}"          # ADAPT
: "${BENCH_RESULTS:?set BENCH_RESULTS}"

repo="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo"   # task YAMLs give local data_files relative to the repo root
run_dir="$BENCH_RESULTS/lm_eval/$name/$split"
if compgen -G "$run_dir/**/results_*.json" >/dev/null || compgen -G "$run_dir/*/results_*.json" >/dev/null; then
    echo "error: $run_dir already holds a run; move it aside so the export reads exactly one" >&2
    exit 1
fi

# Fixed protocol for every model (ADAPT): few-shot count, seeds.
python -m lm_eval --model "$model_type" --model_args "$model_args" \
    --tasks "$TASK" --include_path "$repo/tasks" \
    --num_fewshot 0 --seed 0,1234,1234,1234 \
    --output_path "$run_dir" --log_samples "$@"

python -m benchpkg.lm_eval_export --run-dir "$run_dir" --task "$TASK" \
    --out "$BENCH_RESULTS/$split/predictions_$name.csv" ${BENCH_MODEL_ID:+--model-id "$BENCH_MODEL_ID"}
