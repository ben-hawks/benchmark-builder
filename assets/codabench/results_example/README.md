# Results-submission example (build_bundle.py pattern)

A runnable miniature of how axess-benchmark builds its Codabench bundle
(`references/codabench.md`, "Building the bundle from the benchmark"). The code-submission
counterpart is `../example_bundle/`.

```
results_example/
├── bundle_src/        hand-written, versioned: competition.yaml, logo, pages/,
│                      scoring_program/ (SUBMISSION_FILES contract, vendored metrics), starting_kit/README.md
├── build_bundle.py    adds generated files from ONE truth function, zips the bundle
└── build/             generated, git-ignored
```

The toy "benchmark" is the code example's linear-regression data:

- split `test` is the dev-phase test set, and `holdout` is the final-phase test set;
- the reference model is least squares; the weak baseline is the training mean;
- one test sample is treated as missing ground truth, to exercise the "extra rows are
  ignored" rule.

## Build and validate

```bash
python assets/codabench/results_example/build_bundle.py
python scripts/validate_codabench_bundle.py assets/codabench/results_example/build/bundle \
    --submission assets/codabench/results_example/build/bundle/starting_kit/sample_submission.zip
python scripts/validate_codabench_bundle.py assets/codabench/results_example/build/bundle \
    --submission assets/codabench/results_example/build/extra/baseline_mean_submission.zip
```

Last checked 2026-10-02:

| Check | Result |
|---|---|
| Tiers 1–3, sample submission | pass; test R² 0.998, holdout R² 0.997 |
| Tier 4 (`codalab/codalab-legacy:py312`, from WSL with `--docker-host unix:///var/run/docker.sock`) | pass; in-container scores identical |
| Discrimination: weak baseline | test R² −0.04, holdout R² −0.18 |
| Malformed submissions (missing sample, NaN, duplicate id, missing file) | each fails, naming the problem |
| Wrapping folder | tier 2 flags it as an error (zip at the root); the scoring program still tolerates it |
