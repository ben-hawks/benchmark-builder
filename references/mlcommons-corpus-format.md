# The MLCommons Science Benchmarks corpus entry format

Source: [`benchmarks-format.yaml`](https://github.com/mlcommons-science/benchmark/blob/main/source/benchmarks-format.yaml)
in the `mlcommons-science/benchmark` repo — the schema behind the searchable
corpus at https://mlcommons-science.github.io/benchmark/ that
`references/ontology.md` (arXiv:2511.05614) is the paper for. Fetched and read
directly, not inferred from the one example the ontology paper's own appendix
shows — that example (Jet Classification) is reproduced in-line below wherever
it clarifies a field's intent better than the schema file's own comment does.
Also fetched directly: `CONTRIBUTING.md`, `docs/benchmark-format.md`, and the
`id`-generation code in `bin/yaml_manager.py`/`bin/mkdocs_writer.py` — these
back the "How `name` becomes the entry's published URL" and "If this entry is
headed upstream" sections below.

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

### How `name` becomes the entry's published URL — check this live, don't trust a cached copy

The corpus entry has no `id`/`slug` field to fill in yourself: the publishing
pipeline derives one from `name` when it loads the catalogue, and that
derived `id` is what the published site uses as the page path
(`https://mlcommons-science.github.io/benchmark/<id>/`). The exact
derivation is real upstream code, not part of this skill's own schema, so
**fetch and read it fresh each time `name` needs to be finalized for a real
corpus entry** rather than relying on a description written into this file —
it can change without this skill knowing:

- `bin/yaml_manager.py` — the `clean_string`/`id`-assignment logic that turns
  `name` into the slug.
- `bin/mkdocs_writer.py` — confirms the `id` is used verbatim as the output
  filename/URL path.

As of the last time this was checked, the transform lowercases `name`,
replaces spaces with underscores, and strips everything that isn't a letter,
hyphen, or underscore (digits included) — which means a version number or
year in `name` can silently vanish from the slug, and two names that collapse
to the same `id` is a real error condition upstream, not just a lint warning.
Treat that as a reason to re-check the live source before finalizing `name`,
not as a fact to take on faith from this paragraph.

This only matters when the entry is headed for the real upstream corpus (see
"If this entry is headed upstream" below); it doesn't change anything about
this skill's own output beyond picking `name` thoughtfully.

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

## If this entry is headed upstream: read the live repo conventions, don't rely on a snapshot

Everything above produces a correct entry per the schema. If the user actually
intends to submit it as a PR to `mlcommons-science/benchmark` (not just keep
it as this skill's own deliverable), there are real contribution conventions
this skill's schema table doesn't cover — indentation/quoting style, the
placeholder convention for unknown fields, which of two catalogue files to
target, required validation commands, and PR conventions. These live in the
upstream repo itself and are this skill's actual dependency, not something to
keep a paraphrased copy of here (a copy goes stale the moment the maintainers
edit their own docs). Before finalizing a file meant for a real PR, fetch and
follow, in full, whatever is currently written in:

- `CONTRIBUTING.md` — the workflow: fork/branch, which of
  `source/benchmarks.yaml` (main catalogue) vs `source/benchmarks-addon.yaml`
  (supplemental) to target, the required `make check` (and optional
  `make check_url`) before opening a PR, and PR title/description
  conventions.
- `docs/benchmark-format.md` — authoring rules layered on top of the schema
  itself: indentation and quoting style, booleans, multiline-text style, and
  the placeholder convention for a field that's genuinely unknown (this
  skill's own bar is stricter — ask the user, don't fabricate — but once
  something really can't be determined, match whatever that doc currently
  says to write instead of leaving `assets/mlcommons_corpus_entry_template.yaml`'s
  blank `""` placeholder in place).

Don't skip this fetch because the schema-conformant entry already validates
against `scripts/validate_corpus_entry.py` — that script checks this skill's
own schema understanding, not the upstream repo's separate authoring/PR
conventions, and the two can diverge.

## Validate before calling it done

`scripts/validate_corpus_entry.py <entry.yaml>` checks the structural rules
above (required fields present, `>=1` list fields non-empty, `cite` entries
look like bibtex, ratings in range) — always run it before treating the
entry as finished, the same way `score_benchmark.py` and
`validate_codabench_bundle.py` are never skipped for their own artifacts.

## Step by step

Do this once the standalone benchmark and its rubric score both exist. The
sections above give the field-by-field mapping, the two real ambiguities in the
source schema, and the schema-vs-practice mismatch found by testing the
validator against a cataloged entry; don't rediscover these by guessing.

1. **Start from `assets/mlcommons_corpus_entry_template.yaml`.** Most fields
   map directly from work already done — the field-by-field table above says
   exactly where each one comes from (rubric.yaml's six scores map 1:1 onto
   `ratings`, no rescaling needed). A few fields (`keywords`,
   `ai_capability_measured`, `ml_task`) aren't collected anywhere else in this
   skill's workflow — synthesize them from what you already know rather than
   leaving them blank, but say plainly that they're a synthesis, not a fact
   pulled from a source.
2. **Pick `name` with its downstream URL in mind.** The published corpus
   derives each entry's page URL from `name` automatically — there's no
   separate `id`/`slug` field to set. The exact derivation lives in the
   upstream repo's own code and can change, so per "How `name` becomes the
   entry's published URL" above, fetch
   it fresh rather than trusting a paraphrase before finalizing `name`.
3. **Ask about `url` and `contact` rather than assuming.** If this is a
   formalized existing benchmark (not built from scratch), the "The url
   decision" section above explains why this is a real, unresolved
   choice between the upstream project and the newly-formalized package --
   ask the user. Similarly, never default to listing the user's own contact
   info without asking first.
4. **Only set `valid: true` / `fair.reproducible: true` / `fair.benchmark_ready: true`
   if actually verified**, the same bar this skill already applies everywhere
   else -- these are booleans per the documented schema (a real cataloged
   entry using strings instead is a known, documented mismatch to not repeat).
5. **Validate before calling it done**:
   ```bash
   python scripts/validate_corpus_entry.py <entry.yaml>
   ```
   Fix everything it flags as an error; warnings (e.g. the deprecated
   `solutions` field, or `ml_motif` diverging from `task_types`) are judgment
   calls to consider, not blockers.
6. **If the entry is actually headed upstream as a PR**, fetch and follow the
   upstream repo's own `CONTRIBUTING.md` and `docs/benchmark-format.md`
   live rather than relying on any paraphrase of them — see the "If this entry is headed
   upstream" section above for exactly which files and why this is a live
   dependency, not baked-in fact.

