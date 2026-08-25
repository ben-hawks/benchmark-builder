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
- **Scores the result** against the ontology's real six-category, 27-point rating
  rubric, with a deterministic scorer script, so the score is reproducible and
  evidence-backed rather than a vibe.
- **Packages it for Codabench**: `competition.yaml`, ingestion/scoring programs, an
  example submission, and a four-tier validator (including a no-Docker local dry run)
  that catches the most common way a bundle breaks — a leaderboard column key that
  doesn't match what the scoring program actually outputs.

## Installing

Copy (or clone) this repo into your Claude Code skills directory:

```bash
git clone https://github.com/ben-hawks/benchmark-builder.git ~/.claude/skills/benchmark-builder
```

or, for a single project rather than every session, into that project's
`.claude/skills/benchmark-builder/` instead.

## Structure

```
SKILL.md                       the actual workflow Claude follows
references/
  ontology.md                  condensed ontology + rubric spec (arXiv:2511.05614)
  wa-hls4ml-example.md         a real benchmark scored against the rubric, as a pattern
  codabench.md                 Codabench bundle format, verified against real examples
scripts/
  metrics.py                   regression/classification metric building blocks
  score_benchmark.py           deterministic rubric scorer
  validate_codabench_bundle.py four-tier Codabench bundle validator
  generate_codabench_example_data.py
assets/
  rubric_template.yaml, benchmark_card_template.md, submission_report_template.md
  codabench/
    Dockerfile.template, Dockerfile.gpu.template
    example_bundle/            a complete, self-tested worked Codabench bundle
```

## Background

This skill implements the ontology and rating rubric from *"An MLCommons Scientific
Benchmarks Ontology"* (Hawks et al., 2025), and uses *"wa-hls4ml: A Benchmark and
Surrogate Models for hls4ml Resource and Latency Estimation"* (Hawks et al., 2025,
[arXiv:2511.05615](https://arxiv.org/abs/2511.05615)) as its worked example of a
benchmark that scores well against that rubric.

## License

TODO — not yet chosen. Treat this repo as all-rights-reserved until a LICENSE file is added.
