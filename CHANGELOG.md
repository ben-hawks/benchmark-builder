# Changelog

## Unreleased (2026-10-02): axess-benchmark repository structure

This release codifies [axess-benchmark](https://github.com/ben-hawks/axess-benchmark) (the
wa-hls4ml benchmark built with this skill) as the recommended structure for every
benchmark, and folds in what organizing it and running it on NERSC Perlmutter taught.

### Keep the generic templates free of wa-hls4ml specifics

The skill's structure, pipeline and conventions are generic. What goes inside a benchmark's
files is decided per benchmark while the skill runs, and is implemented in that
benchmark's own code and docs. axess-benchmark's choices now appear only as labelled
examples.

- **Slurm templates:**
  - new `assets/hpc/slurm/stack.sh` with empty `bench_stack_env`, `bench_post_install`
    and `bench_check_env` hooks for the benchmark's own stack fixes;
  - the PyTorch Geometric/triton workaround (`TORCHDYNAMO_DISABLE`, uninstalling triton)
    and TensorFlow log settings are now commented examples, not defaults;
  - stack-neutral names (`venv-main`, `bench_load_main_stack`, `BENCH_MAIN_MODULE`,
    `BENCH_VENV_SYSTEM_SITE`);
  - the venv interpreter is configurable (`BENCH_PYTHON`, default `python3`);
  - the GPU device name and info command come from the machine profile, not hard-coded
    `cuda`/`nvidia-smi`;
  - jobs pass `--cache-dir`/`--split`, so the cache format is the benchmark's choice
    (no `.npz`);
  - Perlmutter's job sizes and modules are placeholders, keeping only verified cluster
    facts.
- **Repo snippets:**
  - `report.py` needs this benchmark's `METRICS` (no R²/SMAPE default);
  - `submission.py` has a task-specific `check_values()` hook and no cache-format
    assumption;
  - `test_pipeline.py` needs measured `RTOL`/`ATOL` (no copied tolerances);
  - `build_bundle.py` has a `weak_baseline()` hook (no training-mean default);
  - the snippets use `data.OUTPUT_COLUMNS` and `truth.truth_frame(cache_dir, split)` /
    `scored_ids(cache_dir, split)`.
- **References and SKILL.md:**
  - missing-ground-truth handling, streaming, caching, post-processing, prediction
    format, weak baselines, validity checks and test tolerances are now questions to
    answer per benchmark;
  - the cache step is optional in the pipeline contract;
  - non-per-sample tasks define their own prediction artifact;
  - `strict=True` is framed as one framework's strict loading;
  - `references/hpc.md` separates machine facts from the benchmark's stack, and moves
    the triton issue to "stack-specific problems: found per benchmark".

### SKILL.md

- **Repository layout.** "Build the artifacts" now proposes the axess-derived layout
  (an installable `src/<pkg>/`, `weights/MANIFEST.json`, golden tests,
  `reference_results/`, `docs/VALIDATION.md`, per-machine HPC scripts, `codabench/`) and
  the pipeline contract. The layout is a strong default, not a requirement. The repo is
  generated per benchmark from a spec, not copied from a skeleton.
- **Element D, reference solution:**
  - a mandatory verification step: architecture identity with `strict=True`, sha256
    manifest, training-label vs scored-label audit on data, the full inference procedure
    (preprocessing + stats + post-processing), per-sample agreement, and reference vs
    auxiliary;
  - the question "score-only or includes training?".
- **Element C, metrics:** recompute a published number with the stated formula, and
  check tables for internal inconsistencies.
- **Element B, dataset:** sample-ID, missing-truth, streaming and filter defaults.
- **Element E, documentation:** ask which machine(s) the benchmark runs on; citations
  from doi.org.
- **Iterate:** re-read rubric evidence whenever a fact changes, with dated `notes:`.
- **Codabench:**
  - mode chosen from scope + data visibility;
  - the pipeline emits submission zips;
  - the bundle is built by a `build_bundle.py` from the same truth function;
  - a scoring program contract;
  - ranking on a bounded primary metric;
  - a discrimination check every time;
  - malformed-submission checks;
  - terms placeholders allowed only for confirmed dev-instance uploads.

### New references

- `references/repo-structure.md`: the layout, piece by piece, with each file's contract,
  the optional pieces, the score-only vs training variants, and conventions.
- `references/hpc.md`: generic Slurm, the per-machine questions, the Perlmutter worked
  profile, and gotchas.

### New assets

- `assets/repo/`: snippets for `score_all.sh`, `submission.py`, `report.py`,
  `fetch_weights.py`, `weights/MANIFEST.json`, the golden `tests/test_pipeline.py`,
  `CITATION.cff`, `.gitattributes` and a `.gitignore` snippet.
- `assets/hpc/slurm/`: `env.sh`, `setup.sh`, `submit.sh`, `jobs/{featurize,train,
  infer_gpu,infer_cpu,score}.sbatch`, and `profiles/{perlmutter,generic}.sh`.
- `assets/codabench/build_bundle.py` (template) and `assets/codabench/results_example/`
  (a runnable results-submission example using that pattern, validated through tier 4).

### Scripts

- `validate_codabench_bundle.py`:
  - tier 2 reads a declared `SUBMISSION_FILES` contract, parsed with `ast`, falling back
    to the regex;
  - tier 3 reports a missing host package as "host missing dependency", not a scoring
    failure;
  - new `--docker-host` option, with a troubleshooting hint when the engine isn't
    reachable;
  - a clean error for a missing `--submission` file.
- `score_benchmark.py`: lists evidence with provisional wording ("pending", "not yet",
  "TODO", "will be") under "Evidence to re-check".

### Other

- `references/wa-hls4ml-example.md` rewritten from axess-benchmark, now with "What this
  example teaches".
- `references/ontology.md`: a reference solution scored against a different target than
  it was trained on isn't a valid reference.
- `references/codabench.md`: the build pattern, the scoring contract, ranking and
  discrimination, and tier 3/4 troubleshooting.
- `.gitattributes` keeps `*.sh`/`*.sbatch` templates LF on Windows checkouts.
- `SKILL.md` description trimmed to 983 characters (limit 1024).
- `examples/wa-hls4ml/` cards re-targeted to axess-benchmark:
  - `MODEL_CARD.md` now documents the retrained reference GNN (release
    `resource-report-retrain`), following the live GEAR Model Card v1 template fetched
    2026-10-02, instead of the paper's HLS-estimate checkpoint;
  - `BENCHMARK_CARD.md` follows the skill's card template. It states the ground truth
    (post-synthesis resources, post-HLS latency), coverage, reference results, ontology
    motifs, Table 4 caveats and the published citation;
  - `DATA_CARD.md`, a hand-filled outline, is replaced by
    `genesis_datacard_wa_hls4ml.md`. That card has full Genesis v1.2 frontmatter and
    body, follows the datacard-generator workflow (AI-ModCon/BaseData_Skills@7ef7694),
    has 16 ORCIDs and every ROR verified live, and passes `linkml-validate`. It records
    parsed record counts (including 3 null array entries in train/val), per-file
    sha256 values, and the public Fermilab dCache mirror.
    `references/doe-gear-cards.md` and SKILL.md now point to the generator workflow
    instead of hand-filling.
