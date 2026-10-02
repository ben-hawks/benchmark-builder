# benchmark-builder

A [Claude Code](https://claude.com/claude-code) skill that walks you through designing,
structuring, documenting, and self-scoring a scientific ML benchmark that conforms to
the **MLCommons Science Benchmarks Ontology** ([Hawks et al., arXiv:2511.05614](https://arxiv.org/abs/2511.05614)) —
and, once the benchmark exists, adapting it into an upload-ready
[Codabench](https://www.codabench.org/) competition bundle with a validated example
submission.

## What it does

- **Interviews you** about the five elements a benchmark needs (problem specification,
  dataset, performance metrics, reference solution, documentation) — but checks your
  repo/papers/code for answers *before* asking, and only interviews genuine gaps.
- **Generates a reproducible benchmark repository.** The recommended layout (a strong
  default, not a requirement) is generalized from
  [axess-benchmark](https://github.com/ben-hawks/axess-benchmark):
  - an installable package;
  - one `fetch → cache → [train] → predict → score_all.sh` pipeline that every model
    (and every participant) plugs into;
  - sha256-checked weights;
  - golden-output tests;
  - a validation log and committed reference results;
  - generic Slurm or PBS jobs tuned to the machines you name.
- **Verifies the reference solution** before trusting it: model identity, the label it
  was trained on vs the label that's scored, the full inference procedure, and
  per-sample agreement with upstream.
- **Scores the result** against the ontology's real six-category, 27-point rating
  rubric, with a deterministic scorer script, so the score is reproducible and
  evidence-backed rather than a vibe. The scorer flags evidence that has probably gone
  stale.
- **Builds LLM evaluation benchmarks too.** The task is an lm-evaluation-harness task;
  each model run is kept in lm-eval's own format and exported to the same per-sample
  prediction file every other benchmark uses.
- **Uses Genesis Mission skills where they exist.** It loads skills from
  [AI-ModCon/genesis-skills](https://github.com/AI-ModCon/genesis-skills) on demand,
  pinned to a tested commit (HPC site skills at their latest version):
  - HPC site and scheduler facts (`perlmutter`, `frontier`, `aurora`, `slurm`, `pbs`);
  - lm-eval task building (the lm-eval-harness skills) and LLM model cards
    (`card-eval-updater`);
  - data cards (`datacard-generator`) and Croissant metadata (`croissant-validator`);
  - an independent recomputation of standard metrics (`uq-metrics-evaluator`);
  - related work (`literature-search`).

  `references/genesis-skills.md` maps which skill is used where, and the problems found
  when running them.
- **Packages it for Codabench.** The bundle is built from the benchmark's own truth
  function (`build_bundle.py`), and the benchmark pipeline emits upload-ready submission
  zips. A four-tier validator (including a no-Docker local dry run) catches the most
  common way a bundle breaks: a leaderboard column key that doesn't match what the
  scoring program actually outputs.

## Installing

Copy (or clone) this repo into your Claude Code skills directory:

```bash
git clone https://github.com/ben-hawks/benchmark-builder.git ~/.claude/skills/benchmark-builder
```

or, for a single project rather than every session, into that project's
`.claude/skills/benchmark-builder/` instead.

The Genesis Mission skills it uses don't need installing. When a step needs one, the
skill uses an installed copy if there is one. Otherwise it fetches
`AI-ModCon/genesis-skills` into a cache (`$GENESIS_SKILLS_DIR`, default
`~/.cache/genesis-skills`). To install them yourself instead, use that repo's `unpack.sh`
(e.g. `./unpack.sh hpc-skills --target ~/.claude/skills --mode symlink`).

## Structure

```
SKILL.md                       the actual workflow Claude follows
references/
  ontology.md                  condensed ontology + rubric spec (arXiv:2511.05614)
  repo-structure.md            recommended benchmark repo layout + pipeline contract (from axess-benchmark)
  reference-solution-checks.md element D: verifying a reference solution before building on it
  metrics-and-uq.md            independent metric recomputation; calibration metrics; UQ audit
  llm-benchmarks.md            LLM benchmarks: lm-eval task, pipeline mapping, verification, cards
  genesis-skills.md            which genesis-skills skill is used where, how to load it, known problems
  hpc.md                       generic Slurm/PBS, per-machine questions, site profiles (Perlmutter verified)
  wa-hls4ml-example.md         axess-benchmark: the worked example and the lessons it taught
  codabench-workflow.md        Codabench: step-by-step bundle build and example-submission validation
  codabench.md                 Codabench bundle format, build pattern, scoring contract
  mlcommons-corpus-format.md, doe-gear-cards.md
scripts/
  metrics.py                   regression/classification/calibration metric building blocks
  score_benchmark.py           deterministic rubric scorer
  render_card_results.py       metrics.json -> model card evaluation results, with a --check mode
  validate_codabench_bundle.py four-tier Codabench bundle validator
  validate_corpus_entry.py     MLCommons corpus entry validator
  generate_codabench_example_data.py
assets/
  rubric_template.yaml, benchmark_card_template.md, submission_report_template.md
  repo/                        snippets to adapt: score_all.sh, submission.py, report.py, fetch_weights.py,
                               MANIFEST.json, golden test, CITATION.cff, .gitattributes,
                               lm_eval_export.py + predict_lm_eval.sh (LLM benchmarks)
  hpc/common/                  env.sh, stack.sh (benchmark stack hooks), setup.sh (scheduler-neutral)
  hpc/slurm/                   submit.sh, jobs/*.sbatch, profiles/{perlmutter,frontier*,generic}.sh
  hpc/pbs/                     submit.sh, jobs/*.pbs, profiles/{aurora*,generic}.sh   (* unverified)
  codabench/
    Dockerfile.template, Dockerfile.gpu.template
    build_bundle.py            template: bundle from the benchmark's own truth function
    example_bundle/            self-tested code-submission bundle
    results_example/           self-tested results-submission bundle (build_bundle.py pattern)
examples/wa-hls4ml/            benchmark, model and Genesis data cards for axess-benchmark
CHANGELOG.md
```

## Background

This skill implements the ontology and rating rubric from *"An MLCommons Scientific
Benchmarks Ontology"* (Hawks et al., 2025), and uses *"wa-hls4ml: A Benchmark and
Surrogate Models for hls4ml Resource and Latency Estimation"* (Hawks et al., 2025,
[arXiv:2511.05615](https://arxiv.org/abs/2511.05615)) as its worked example of a
benchmark that scores well against that rubric.

## License

TODO — not yet chosen. Treat this repo as all-rights-reserved until a LICENSE file is added.
