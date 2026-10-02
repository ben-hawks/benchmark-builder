# Codabench workflow: competition bundle and example submission

The step-by-step procedure for packaging a finished benchmark as a Codabench competition.
`SKILL.md` ("Package for Codabench") says when to start. `references/codabench.md` holds
the format details these steps rely on (bundle layout, `competition.yaml` schema, scoring
contract, Docker images, validator tiers). Read both in full before touching any
Codabench file.

For an LLM benchmark, read `references/llm-benchmarks.md` ("Codabench") as well. It's a
results submission of per-sample answers, with extra checks in the scoring program.

## Build the competition bundle

Only start this once the standalone benchmark exists (dataset, metrics, reference
solution, docs). This phase reuses that work; it doesn't replace it. Read
`references/codabench.md` in full first. It's grounded in real, verified Codabench
bundles (not just the docs prose, which has gaps against actual behavior), and has the
exact directory/file contracts this step depends on. Two worked examples to
pattern-match against:

- `assets/codabench/results_example/`, a **results submission** built the
  axess-benchmark way: hand-written `bundle_src/` plus `build_bundle.py`;
- `assets/codabench/example_bundle/`, a **code submission**.

1. **Decide code submission vs. results submission from the benchmark's scope and data
   visibility.** Ask the user rather than assuming. This decides whether an
   `ingestion_program/` exists at all, so settle it before generating anything.
   - Score-only with public ground truth points to a **results submission**. That's what
     axess chose: a code submission couldn't hide the answers either, and it would have
     needed GPU workers and a custom image.
   - A benchmark that evaluates training or a method, or that has hidden data, points
     to a **code submission**.
   - Revisit the element D answer (score-only vs includes training) here.

   Write the scoring program so it works for both modes. It does if the ingestion
   program writes the same prediction files a results submission would upload.
2. **The benchmark pipeline must emit upload-ready submissions.** The last step of
   `score_all.sh` runs `src/<pkg>/submission.py`, which writes
   `<results>/codabench/<model>_submission.zip` for every model:
   - exactly the scored samples;
   - files at the zip root;
   - the same checks as the scoring program;
   - no zip and a non-zero exit for incomplete predictions.

   A participant who ran the standalone benchmark already has their upload. Adapt
   `assets/repo/submission.py`.
3. **Build the bundle from the benchmark with `codabench/build_bundle.py`**, adapted from
   `assets/codabench/build_bundle.py`. Never hand-copy data into the bundle.
   - Hand-written, versioned files live in `codabench/bundle_src/`: `competition.yaml`,
     logo, `pages/`, `scoring_program/` with vendored metrics, and `starting_kit/` docs.
   - `build_bundle.py` generates the hidden truth, scored-ID lists, `solution/`,
     `sample_submission.zip`, and a weak-baseline zip.
   - All generated files come from **the same truth function the benchmark uses**, so
     they can't diverge from it.
   - `codabench/build/` stays out of git.
4. **Derive what's already known** from the standalone benchmark, and don't ask for any
   of it again:
   - splits go to `reference_data` (plus `input_data` for code submission);
   - metrics go to `scoring_program/scoring.py`, vendored from `src/<pkg>/score.py`,
     plus leaderboard columns;
   - the reference solution goes to `solution/`;
   - the benchmark card goes to `pages/*.md`.
5. **Rank on a bounded, primary-split metric.** Leaderboard column index 0 is the
   ranking key. Don't make it a metric that's unbounded below, such as R² on an
   out-of-distribution split: axess's training-mean baseline scored −2651 there. Show
   such metrics as extra columns instead.
6. **Write the scoring program to the contract** in `references/codabench.md`
   ("Scoring program contract"):
   - a module-level `SUBMISSION_FILES = [...]`, which the validator reads;
   - literal `os.path.join(prediction_dir, "<name>")` paths;
   - tolerate one wrapping folder;
   - ignore extra rows, if predictions may cover samples that aren't scored;
   - fail with a message naming the problem on a missing file, a missing sample, a
     duplicate ID, or a value that's invalid for this task (e.g. non-finite for a
     numeric output, an unknown label for classification);
   - write NaN as `null` in `scores.json`.
7. **Ask for what only the user can supply**, sorted by `references/codabench.md`'s
   "Required vs. optional" list. Title, logo, terms, phase dates and submission mode are
   real blockers, so ask for them together in one pass. Most of what's left has sane
   defaults; offer them and move on unless the user cares.

   **Never author real participation terms.** Generate an obviously-marked placeholder
   (pattern: `assets/codabench/example_bundle/pages/terms_and_conditions.md`) and say
   plainly that it must be replaced before the competition goes live. A placeholder is
   acceptable for an upload to a dev instance only if the user confirms that's what it's
   for.
8. **Decide the Docker image** using `references/codabench.md`'s "Docker image" section.
   Check the reference solution's real dependency file against the stock-image table
   first; most benchmarks need nothing custom (a results-submission scoring program
   usually needs only numpy and pandas).

   Only if a stock image doesn't cover it, write one from
   `assets/codabench/Dockerfile.template` (CPU) or `Dockerfile.gpu.template` (GPU) and
   save it as `Dockerfile` at the bundle root. The validator's tier 4 then builds and
   tests it automatically. That's all local and reversible, so it needs no confirmation
   (see the next section).

   Get **explicit confirmation before `docker push`**. Publishing an image to a public
   registry is a publish action, not a default-and-forget step, and the confirmation is
   per instance, even if the user approved a push earlier in this conversation. The
   validator never pushes.
9. **Generate the bundle** following the directory layout in `references/codabench.md`.
   - Vendor any shared metric code into `scoring_program/` (and `ingestion_program/` if
     it needs any) rather than importing from outside the bundle. Both directories are
     zipped and uploaded independently, so anything they need must live inside them.
   - Write `ingestion.py`/`scoring.py` with the `CODABENCH_ROOT` environment-variable
     convention (default `/app`, overridden for local testing) rather than hardcoding
     `/app` the way Codabench's own raw examples do. That's what makes the next section
     possible without Docker.

## Build and validate an example submission bundle

Every Codabench competition bundle needs a submission a participant can look at and
run, and this doubles as the fastest way to prove the bundle actually works end to end.

1. **Reuse the reference solution as the example submission.** Zip it flat (root files
   only, no wrapping folder: `zipfile.ZipFile(...).write(path, arcname=filename)`, not a
   recursive directory zip) into `starting_kit/sample_submission.zip`.
   - **Results submission:** `build_bundle.py` does this from the reference model's
     predictions.
   - **Code submission:** `solution/model.py` becomes the zip, as in
     `assets/codabench/example_bundle/`.

   If a weaker, more obviously-a-starting-point baseline would help participants more
   than the full reference solution, put that in `starting_kit/model.py` and keep the
   reference solution's zip as a separate "working example" download. The example
   bundle demonstrates both patterns.
2. **Validate with `scripts/validate_codabench_bundle.py`**:
   ```bash
   python scripts/validate_codabench_bundle.py <bundle_dir> --submission <sample_submission.zip> --task-index 0
   ```
   Read its docstring for what each of its four tiers checks. Tiers 1-3 need no Docker,
   so always run them before calling a bundle finished. Fix whatever they flag:
   - The most common break is a leaderboard column key that doesn't match `scores.json`.
     Tier 3 catches it by actually producing `scores.json` and diffing its keys against
     every configured column.
   - Tier 2 reads the scoring/ingestion program's declared `SUBMISSION_FILES` contract,
     falling back to a source regex.
   - Tier 3 runs on the host's Python, so a missing host package (numpy, pandas) is
     reported as a host problem, not a bundle failure.

   For a results submission, also validate every zip the benchmark pipeline wrote
   (`<results>/codabench/*_submission.zip`), plus a few deliberately malformed ones:
   - a missing sample;
   - a NaN;
   - a missing file;
   - a wrapping folder.

   Each malformed zip must fail with a message naming the problem; the wrapping folder
   must be tolerated by the scoring program.

   **If Docker is available on this machine, run tier 4 as well**, by adding `--docker`:
   ```bash
   python scripts/validate_codabench_bundle.py <bundle_dir> --submission <sample_submission.zip> --docker
   ```
   - It builds the bundle's `Dockerfile` if it has one (otherwise it uses or pulls
     `competition.yaml`'s `docker_image`), then runs the real ingestion and scoring
     programs inside the container against Codabench's actual `/app/...` layout.
   - It's the only tier that catches "works on my machine, but the declared image is
     missing a dependency". Tiers 1-3 can't see that, since they run on the host's own
     Python.
   - Check for Docker rather than assuming. The tier skips itself and says why when the
     daemon isn't reachable, so just run it and read the output.
   - "Not reachable" is often the client-to-engine bridge, not the engine itself. Use
     `--docker-host` or run from WSL/Linux (`references/codabench.md`, "Tier 4
     troubleshooting").
   - Everything it does is local and reversible: build, pull, run, and
     `--rm-built-image` to clean up an image it built. It never pushes.
3. **Report the actual scores**, not just "validation passed". Show the user the
   `scores.json` values the example submission produced, the same way the standalone
   benchmark's scoring step reports real numbers rather than a pass/fail flag.

   **Run the discrimination check every time:** score the reference solution and the
   weak-baseline zip from `build_bundle.py`, and report both. Pick the weak baseline for
   the task: e.g. the training mean for regression, the majority class for
   classification, a random policy for control. (axess used the training mean: mean R²
   0.809 vs 0.000, SMAPE 10.3% vs 114%.) If they don't separate clearly, flag it before calling
   the bundle done. Also check that Codabench's scores for the pipeline's zips equal the
   benchmark's own `metrics.json`.
4. **Record the validation** in `codabench/README.md`: the mode, the phases, the ranking,
   a tier-by-tier result table with the date, the discrimination numbers, and a
   pre-upload checklist (terms, logo, image).
