# The MLCommons Science Benchmarks corpus entry format

Source: [`benchmarks-format.yaml`](https://github.com/mlcommons-science/benchmark/blob/main/source/benchmarks-format.yaml)
in the `mlcommons-science/benchmark` repo — the schema behind the searchable
corpus at https://mlcommons-science.github.io/benchmark/ that
`references/ontology.md` (arXiv:2511.05614) is the paper for. Fetched and read
directly, not inferred from the one example the ontology paper's own appendix
shows — that example (Jet Classification) is reproduced in-line below wherever
it clarifies a field's intent better than the schema file's own comment does.

This is a **separate deliverable** from everything else this skill produces:
a single flat YAML entry meant to be appended to (or merged into) MLCommons'
own public corpus, not part of the standalone benchmark package's own
structure. Generate it once the standalone benchmark (and its rubric score)
already exist — every field below either comes directly from that work or
needs one targeted question, never a cold restart of the interview.

## Structure

The corpus is a YAML **list** of entries (the schema file itself starts with
`- date: ...`). Generate this benchmark's entry as a **one-item list**
(`[ {...} ]`), not a bare mapping — that's what makes it directly
appendable/mergeable into the real corpus file without reshaping.

## Field-by-field

Condition key: **required** (must be present and non-trivial), **N** meaning
"list, at least N items", **optional**, **deprecated** (schema authors say
skip it).

| Field | Condition | What it is | Where this skill already has it |
|---|---|---|---|
| `date` | required | Benchmark's availability date (official release, or entry-creation date if none) | The associated paper's date if one exists; else today |
| `version` | optional | Benchmark's own version string | `v1.0` for a first formalization pass, unless the project already versions itself |
| `last_updated` | optional | Date this entry was last edited | Today |
| `expired` | optional, `'yes'`/`'no'` | Whether the benchmark is no longer valid | `'no'` unless known otherwise |
| `valid` | required, bool | Whether the benchmark is currently usable (code/data still available) | `true` — only if actually verified working this session, per `references/ontology.md`'s Software Environment criteria |
| `valid_date` | required | Date validity was last confirmed | Today, if you just verified it |
| `name` | required | Short benchmark name | Benchmark card's title |
| `url` | required | The benchmark's main URL | **Ask, don't assume** — see "The url decision" below |
| `doi` | optional | A DOI (e.g. via Zenodo) | Only if the underlying paper/dataset actually has one |
| `domain` | **1** | Scientific domain(s) | `references/ontology.md` Part 3 Scientific Motif(s) — direct reuse |
| `focus` | required | One-sentence description | Benchmark card's opening sentence |
| `keywords` | **1** | Relevant terms | Not collected elsewhere — synthesize from the task/techniques/domain (task type, key method names, notable techniques) rather than leaving empty |
| `summary` | required | Plain-language description | Benchmark card's opening paragraph, often verbatim |
| `licensing` | required | The benchmark's license | `LICENSE` file |
| `task_types` | required | Task type(s) | AI/ML Motif from `references/ontology.md` Part 3, wrapped in a list |
| `ai_capability_measured` | **1** | What capability(ies) are being measured | Not collected elsewhere — synthesize from the Performance Metrics + Reference Solution sections (e.g. "Real-time inference", "Model compression performance") |
| `metrics` | **1** | Metric names | Performance Metric(s) element — names only here, not formulas |
| `models` | **1** | Model/method names used | Reference Solution element |
| `ml_motif` | **1** | **Ambiguous in the source schema itself** — see "Known schema ambiguities" below | Default to matching `task_types` (what the one real cataloged example actually does), not the schema file's own inconsistent example |
| `type` | required | Almost always `Benchmark` | Use `Benchmark` unless there's a specific reason not to |
| `ml_task` | **1** | Learning paradigm(s) | Not collected elsewhere — infer from AI/ML Motif (Classification/Regression → Supervised Learning; RL/Control → Reinforcement Learning; Generative → often Unsupervised/Self-Supervised Learning; state the inference, don't silently guess for an ambiguous motif) |
| `solutions` | **deprecated** | — | Omit entirely; the schema says `results` supersedes it |
| `notes` | optional | Free text | For a formalized (not from-scratch) benchmark, a one-line pointer to `NOTICE`'s change list is useful here |
| `contact` | optional | `{name, email}` | **Ask** — don't default to listing the user's contact info without asking first |
| `cite` | **1**, bibtex | Citation(s) | Documentation element's citation block — reuse verbatim, must actually be bibtex (`@...{...}`), not a URL or plain-text reference |
| `datasets.links` | **1**, `{name, url}` | Dataset access points | Dataset element's Access section |
| `results.links` | required, `{name, url}` | Where results are published | The benchmark's own repo/README/`SCORE_REPORT.md` — see "The url decision" |
| `fair.reproducible` | required, bool | — | `true` only if actually re-run and verified, matching this skill's own reproducibility bar |
| `fair.benchmark_ready` | required, bool | Schema calls this deprecated ("true implies runnable") but still shown in the one real example | Include anyway for consistency with the corpus as it actually exists; set `true` under the same condition as `reproducible` |
| `ratings` | optional | Six sub-categories, each `{rating, reason}` | **Direct 1:1 mapping from `rubric.yaml`** — see "Ratings mapping" below |

### The `url` decision

For a **brand-new benchmark** (nothing existed before this skill built it),
`url` and `results.links` obviously point at this benchmark's own repo — no
ambiguity, don't ask.

For a **formalized existing benchmark** (the upstream project didn't run
cleanly, wasn't structured as a benchmark yet, etc. — the "almost a
benchmark" case), there's a real choice: point at the original upstream
project, or at the newly-formalized, actually-working package this skill
just built? **Ask the user** — both are defensible, and whoever maintains
the real MLCommons corpus may have a preference this skill has no way to
know. If they don't have a preference, default to the formalized package's
own URL: a corpus entry claiming `valid: true` should point at something
that's actually been verified to run, and (per this skill's own findings on
Jet Classification) an unmaintained upstream repo may no longer qualify.

### Ratings mapping

`rubric.yaml`'s six category scores are already 0–5, matching this schema's
rating scale exactly — no rescaling:

| `rubric.yaml` category | Corpus `ratings` key |
|---|---|
| `software_environment` | `software` |
| `problem_specification` | `specification` |
| `dataset` | `dataset` |
| `performance_metrics` | `metrics` |
| `reference_solution` | `reference_solution` |
| `documentation` | `documentation` |

For each, set `rating` to `score_benchmark.py`'s computed category score, and
write `reason` as a short prose synthesis of that category's unmet items (or
"None" if the category scored a clean 5/5) — matching the terse style the
real cataloged entries use (e.g. "System constraints missing" for a docked
Problem Specification score), not a restatement of every checklist item.

## Known schema ambiguities (real, not this skill's error)

Found by actually reading the schema file, not assumed:

1. **`ml_motif` is self-contradictory.** The schema file's own inline example
   sets `ml_motif: [Real-time]`, but the one real cataloged entry
   (Jet Classification) sets `ml_motif: [Classification]` — identical to its
   own `task_types`. The field's comment admits this: *"TODO: we need a list
   of motifs to be in a formal document."* This skill defaults to matching
   `task_types`, following the real precedent over the schema file's own
   inconsistent example — flag this rather than silently picking one.
2. **The "unevaluated" rating sentinel is inconsistent.** The `ratings`
   section's own description says *"A value of 0 in any of the categories
   means it has not been evaluated yet,"* but its own example sets
   `rating: -1` with `reason: Not yet evaluated`. Doesn't matter for this
   skill's output (every rating generated here has actually been evaluated
   via `score_benchmark.py`), but don't copy either convention if you ever
   need to represent "not yet scored" — ask rather than guess which the real
   corpus maintainers actually enforce.
3. **A real, already-cataloged entry doesn't follow its own schema's types.**
   The actual Jet Classification entry as published sets `valid: "yes"` and
   `fair: {reproducible: "Yes", benchmark_ready: "Yes"}` — strings, not the
   booleans the schema file's own example uses for these exact fields
   (confirmed by running `scripts/validate_corpus_entry.py` against that real
   entry, which correctly flags all three as type errors). Generate proper
   booleans anyway — match the documented schema, not observed practice that
   contradicts it — but don't be surprised if a generated entry looks stricter
   than some existing corpus entries when compared side by side. That's the
   entry being more correct, not a bug in this skill's output.

## Validate before calling it done

`scripts/validate_corpus_entry.py <entry.yaml>` checks the structural rules
above (required fields present, `>=1` list fields non-empty, `cite` entries
look like bibtex, ratings in range) — always run it before treating the
entry as finished, the same way `score_benchmark.py` and
`validate_codabench_bundle.py` are never skipped for their own artifacts.
