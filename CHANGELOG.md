# Changelog

## Unreleased (2026-10-02): axess-benchmark repository structure

This release codifies [axess-benchmark](https://github.com/ben-hawks/axess-benchmark) (the
wa-hls4ml benchmark built with this skill) as the recommended structure for every
benchmark, and folds in what organizing it and running it on NERSC Perlmutter taught.

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
