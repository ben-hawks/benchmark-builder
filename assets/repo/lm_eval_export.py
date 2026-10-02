"""Export one lm-evaluation-harness run into the benchmark's prediction file.

    python -m benchpkg.lm_eval_export --run-dir $BENCH_RESULTS/lm_eval/<model>/<split> \\
        --task <task>_<split> --out $BENCH_RESULTS/<split>/predictions_<model>.csv

LLM benchmarks keep lm-eval's own output (results_*.json + samples_*.jsonl, written with
--log_samples) as the canonical record of a run: it is what the genesis card-eval-updater
skill reads, and what other Genesis evaluation tooling understands. This module derives
the pipeline contract's per-sample CSV from it (references/llm-benchmarks.md), so scoring,
the leaderboard and Codabench submissions work exactly as for any other benchmark:

    sample_id, answer[, answer_norm], lm_eval_<metric>...

- multiple_choice tasks: `answer` is the index of the highest-loglikelihood choice and
  `answer_norm` the index after dividing by the choice's length in characters, the
  selection rules behind lm-eval's `acc` and `acc_norm` (ties go to the first choice, as in
  lm-eval).
- generate_until tasks: `answer` is the response after the task's filters
  (filtered_resps), i.e. the extracted answer the task's metric compares.
- lm_eval_<metric>: lm-eval's own per-sample metric values, kept so score.py can check
  per-sample agreement with its own computation (references/llm-benchmarks.md,
  "Verifying LLM reference solutions"). They are not scored.

A sidecar <out>.meta.json records the run's provenance (model, model_args, lm-eval version,
task hash, n-shot, chat template, date).

Refuses, exit 1, no file written:
- more than one run (results_*.json) in --run-dir, unless --results-file picks one;
- a sample-limited run (n-samples effective < original): a smoke test, not a result;
- a missing or duplicate sample ID;
- no verifiable model identity: lm-eval names the model from model_args
  (pretrained/model/path/engine) and otherwise records a random 8-character name. Pass
  --model-id (e.g. "org/model@<revision>") rather than letting that name into a leaderboard.

ADAPT (assets/repo/lm_eval_export.py in the benchmark-builder skill):
  - ID_FIELD: the doc field that is the benchmark's sample_id (data.py's rule). Never use
    lm-eval's doc_id, which is only a position after process_docs.
  - TARGET_DELIMITER: the task's target_delimiter, if it sets one (default " ").
  - add task-specific post-processing only if the task's own metric applies it too.
"""

from __future__ import annotations

import argparse
import csv
import glob
import json
import os
import sys

ID_FIELD = "id"            # ADAPT: the doc field holding the benchmark's sample_id
TARGET_DELIMITER = " "     # ADAPT: the task's target_delimiter, if not lm-eval's default


def _fail(msg: str) -> None:
    print(f"lm_eval_export: {msg}", file=sys.stderr)
    sys.exit(1)


def _one(pattern: str, what: str, explicit: str | None = None) -> str:
    if explicit:
        return explicit
    hits = sorted(glob.glob(pattern, recursive=True))
    if len(hits) != 1:
        _fail(f"expected exactly one {what} ({pattern}), found {len(hits)}: {hits[:5]}. "
              "Point --run-dir at a single run, or pass --results-file.")
    return hits[0]


def _argmax(xs: list[float]) -> int:
    best = 0
    for i, x in enumerate(xs):
        if x > xs[best]:
            best = i
    return best


def _row(rec: dict, output_type: str) -> dict:
    doc = rec["doc"]
    if ID_FIELD not in doc:
        _fail(f"doc_id {rec.get('doc_id')}: no '{ID_FIELD}' field in doc (set ID_FIELD)")
    row = {"sample_id": doc[ID_FIELD]}
    if output_type == "multiple_choice":
        lls = [float(r[0]) for r in rec["filtered_resps"]]
        args = rec["arguments"]
        choices = [args[f"gen_args_{i}"]["arg_1"] for i in range(len(lls))]
        choices = [c[len(TARGET_DELIMITER):] if c.startswith(TARGET_DELIMITER) else c for c in choices]
        row["answer"] = _argmax(lls)
        row["answer_norm"] = _argmax([ll / max(len(c), 1) for ll, c in zip(lls, choices)])
    elif output_type == "generate_until":
        resp = rec["filtered_resps"]
        row["answer"] = resp[0] if isinstance(resp, list) else resp
    else:
        _fail(f"output_type {output_type!r} has no per-sample answer; define this task's "
              "prediction artifact (references/repo-structure.md)")
    for m in rec.get("metrics", []):
        if m in rec:
            row[f"lm_eval_{m}"] = rec[m]
    return row


IDENTITY_KEYS = ("pretrained", "model", "path", "engine")
# Model types whose model_args actually select the weights or the served model. For any
# other (custom) model class, a `pretrained=` in model_args may be ignored by the class and
# still become lm-eval's model_name: the genesis card-eval-updater example recorded a model
# that never ran this way. Warn, so the identity gets checked by hand.
WEIGHT_SELECTING_TYPES = {"hf", "huggingface", "hf-auto", "vllm", "sglang",
                          "local-completions", "local-chat-completions",
                          "openai-completions", "openai-chat-completions"}


def export(run_dir: str, task: str, out: str, results_file: str | None = None,
           model_id: str | None = None) -> dict:
    res_path = _one(os.path.join(run_dir, "**", "results_*.json"), "results file", results_file)
    with open(res_path) as f:
        res = json.load(f)
    stamp = os.path.basename(res_path)[len("results_"):-len(".json")]
    samples_path = os.path.join(os.path.dirname(res_path), f"samples_{task}_{stamp}.jsonl")
    if not os.path.exists(samples_path):
        _fail(f"no {os.path.basename(samples_path)} next to {res_path}: run lm_eval with "
              "--log_samples, and check --task")
    n = res.get("n-samples", {}).get(task, {})
    if n and n.get("effective") != n.get("original"):
        _fail(f"sample-limited run ({n.get('effective')} of {n.get('original')} samples): "
              "re-run without --limit")
    output_type = res["configs"][task]["output_type"]
    model_args = res.get("config", {}).get("model_args") or {}
    if isinstance(model_args, str):  # older lm-eval: "k=v,k=v"
        model_args = dict(kv.split("=", 1) for kv in model_args.split(",") if "=" in kv)
    model_type = res.get("config", {}).get("model")
    if not model_id and model_type not in WEIGHT_SELECTING_TYPES:
        print(f"lm_eval_export: warning: model type {model_type!r} is not one where model_args "
              f"selects the model; check that model_name {res.get('model_name')!r} is what ran, "
              "or pass --model-id", file=sys.stderr)
    if not model_id and not any(model_args.get(k) for k in IDENTITY_KEYS):
        _fail(f"lm-eval recorded no model identity (model_name {res.get('model_name')!r} "
              "is not derived from model_args): pass --model-id")

    rows, seen = [], set()
    with open(samples_path) as f:
        for line in f:
            row = _row(json.loads(line), output_type)
            if row["sample_id"] in seen:
                _fail(f"duplicate sample_id {row['sample_id']!r}")
            seen.add(row["sample_id"])
            rows.append(row)
    if n and len(rows) != n.get("original"):
        _fail(f"{len(rows)} samples logged, task has {n.get('original')}")

    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    cols = list(dict.fromkeys(k for r in rows for k in r))
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(rows)

    cfg = res.get("config", {})
    meta = {
        "results_file": os.path.relpath(res_path, os.path.dirname(os.path.abspath(out))),
        "task": task,
        "task_version": res.get("versions", {}).get(task),
        "task_hash": res.get("task_hashes", {}).get(task),
        "output_type": output_type,
        "n_samples": len(rows),
        "n_shot": res.get("n-shot", {}).get(task),
        "model": cfg.get("model"),
        "model_args": cfg.get("model_args"),
        "model_name": res.get("model_name"),
        "model_id": model_id or res.get("model_name"),
        "model_id_provenance": "user" if model_id else "harness",
        "chat_template_sha": res.get("chat_template_sha"),
        "lm_eval_version": res.get("lm_eval_version"),
        "date": res.get("date"),
        "harness_results": res.get("results", {}).get(task),
    }
    with open(out[:-len(".csv")] + ".meta.json" if out.endswith(".csv") else out + ".meta.json", "w") as f:
        json.dump(meta, f, indent=2, default=str)
    return meta


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--run-dir", required=True, help="lm_eval --output_path of ONE run")
    p.add_argument("--task", required=True, help="the lm-eval task name for this split")
    p.add_argument("--out", required=True, help="<results>/<split>/predictions_<model>.csv")
    p.add_argument("--results-file", help="pick one results_*.json when the run dir holds several")
    p.add_argument("--model-id", help="model identity to record when lm-eval couldn't (e.g. org/model@rev)")
    args = p.parse_args(argv)
    meta = export(args.run_dir, args.task, args.out, args.results_file, args.model_id)
    print(f"wrote {args.out}: {meta['n_samples']} samples, model {meta['model_id']}, "
          f"harness says {meta['harness_results']}")


if __name__ == "__main__":
    main()
