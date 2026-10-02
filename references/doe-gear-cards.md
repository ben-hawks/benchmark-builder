# DOE GEAR xCards (Model Card, Agent Card, Dataset/Data Card)

DOE's GEAR platform (part of the Genesis Mission program) hosts a separate,
parallel documentation convention from everything else in this skill: a
family of short, standardized "cards" — Model Card, Agent Card, Data Card,
Tool Card — for documenting AI artifacts. This is an **optional, additional**
deliverable, not a replacement for the benchmark card or the MLCommons corpus
entry this skill already produces. Offer it when the reference solution is a
model or an agentic system, or when the user is specifically working under a
DOE/Genesis Mission RFA that expects these cards.

**These templates are live DOE pages, not fixed by this skill's own schema
knowledge — fetch and read the current version each time, don't rely on any
description cached in this file.** GEAR is an active platform (the template
files are under a dated path, `.../resources/2026-07/...`, implying they get
revised) and this skill has no way to know if a field has been added, renamed,
or the template restructured since this doc was last checked.

## What to fetch, and when

| Card | Landing page (check first — it may link a newer template or more examples) | Use when |
|---|---|---|
| Model Card | https://gear.doe.gov/rfa-teams/ai-and-agents/model-card-template | The reference solution (element D) is a trained model |
| Agent Card | https://gear.doe.gov/rfa-teams/ai-and-agents/agent-card-template | The reference solution or the benchmark's own task is an agentic system (tool-using, multi-step, LLM-driven) rather than a single model |
| Dataset / FAIR | https://gear.doe.gov/rfa-teams/data-management/fair | Always relevant to element B (Dataset) — this is DOE's own elaboration of the FAIR checklist already in `references/ontology.md`, plus the Genesis Mission data-card framework and identifier services (ARK, OSTI DOI) |

Each landing page links its own current template/example files (as of the
last check, direct-download markdown under `/system/files/resources/...` —
don't hardcode those paths here either, since the dated directory implies
they move; re-derive the link from the landing page each time) — follow the
landing page's own links rather than guessing a file path:

- Model Card: a v1 template plus one worked example (ORBIT2).
- Agent Card: a v1 template plus three worked examples (Argonne AI4HPC
  LASSI-Translate, LBNL MOAT osprey, ModCon BaseData DSAGT) — useful for
  matching tone/depth on a real agent card, the same way
  `references/wa-hls4ml-example.md` is used elsewhere in this skill.
- FAIR / Data Management page: describes the broader "Genesis Mission xCards"
  framework (data cards, model cards, agent cards, tool cards), DOE identifier
  services for datasets (OLCF Atlas ARK IDs pre-publication, OSTI DOI Data ID
  Service post-publication), and links out to a data-card-generator tool
  (`github.com/AI-ModCon/BaseData_Skills`) and a tool-card repo
  (`github.com/AI-ModCon/BaseData_Toolcards`).

**The Dataset/Data Card is a materially different shape from Model/Agent Card
— confirmed by actually fetching it, not assumed.** Model Card and Agent Card
are each a single downloadable markdown template you fill in by hand. The
Data Card is not: the FAIR page's own link goes to a full skill,
`datacard-generator`, implementing the **Genesis Mission Data Card v1.2**
schema — a large (100+ KB), multi-section template
(Discoverability/Accessibility/Interoperability/Reusability/Governed Use/AI
Usability) with its own directory-introspection script and, critically,
**mandatory live identifier verification** (ORCID/ROR/DOI/OSTI, checked against
live APIs) before the tool considers a card valid. The FAIR page links the
older standalone repo `AI-ModCon/BaseData_Skills`; the same skill now lives in
the Genesis catalog at `skills/basedata-skills/datacard-generator` in
`AI-ModCon/genesis-skills`. Use that copy. Two real consequences:

- **Run the generator's workflow properly**: load `datacard-generator` as
  `references/genesis-skills.md` describes (installed, `skill-search`, or a
  pinned clone), read its `SKILL.md` in full, and follow its steps. In outline:
  1. introspect the data (`scripts/introspect.py`);
  2. resolve any DOI and apply its provenance gate (a paper DOI is related work,
     not the dataset's identity);
  3. ask the user the questions only they can answer: authors and CRediT roles,
     sponsors, identifiers, AI-usage statuses, science domain;
  4. verify every ORCID and ROR live;
  5. write the YAML frontmatter and the narrative body;
  6. validate with
     `uv run --with linkml linkml-validate -s scripts/genesis_datacard.yaml -C GenesisDatacardClass <frontmatter.yaml>`.

  Hand it what element B already settled (splits, license, FAIR answers, the
  `croissant.json` if there is one) so it confirms rather than asks again.

  `examples/wa-hls4ml/genesis_datacard_wa_hls4ml.md` is a worked example that
  validates clean (built with the same workflow from `BaseData_Skills@7ef7694`).
  Building it surfaced facts no hand-filled card had: 3 `null` array entries in
  train/val, record counts that differ from the dataset card's, and a public
  dCache mirror.
- **If the workflow can't be run** (no network for the identifier checks, or no
  way to run the validator), a hand-filled card following the v1.2 outline is
  still worth producing. But **every field the tool would verify live (identifiers,
  author roles, org/facility affiliations, exact dates) must be flagged as
  unverified rather than guessed.** Don't let a hand-filled card imply a rigor it
  doesn't have.

## How this fits what this skill already builds

Don't re-run the interview — a GEAR card should draw on element answers
already gathered:

- **Model Card** ← element D (Reference Solution): architecture, training
  procedure, hyperparameters, results, requirements map directly onto
  whatever fields the current template asks for. The results themselves are
  written by script (see "Evaluation results in a Model Card" below). Map field-by-field once
  the live template is in hand; don't guess the mapping in advance since the
  fields aren't known until fetched.
- **Agent Card** ← element A (Problem Specification, for what the agent is
  asked to do) + element D (the agent's own architecture/tools/model choices).
- **Dataset/Data Card** ← element B (Dataset) directly — the FAIR checklist
  already in `assets/benchmark_card_template.md` is a starting point; the
  live FAIR page may ask for more (an ARK or DOI identifier specifically,
  for instance) that this skill's own checklist doesn't currently prompt for.

Generate the card as its own file (e.g. `MODEL_CARD.md`, `AGENT_CARD.md`, and
for a data card the generator's own name, `genesis_datacard_<name>.md`) alongside
the benchmark card, using whatever structure the
live template actually specifies — copy its section headers, don't invent a
structure that merely resembles what this doc describes above.

## Evaluation results in a Model Card: written by script

A Model Card's evaluation sections report the benchmark's numbers for that model. Follow
the genesis `card-eval-updater` rule: **every number is copied by a script from the run's
output, never retyped**, and a validator re-renders the block to prove it still matches.

| Benchmark | Tool | Reads | Writes |
|---|---|---|---|
| LLM benchmark (lm-eval, Eval Factory or NeMo-Skills runs) | the genesis `card-eval-updater` skill (`references/genesis-skills.md`) | one run directory | `### Automated benchmark results` blocks in `## Evaluation data`, `## Evaluation Procedure`, `## Uncertainty Quantification` and `## Evaluation results`, plus `metrics:` entries |
| any other benchmark | `scripts/render_card_results.py` | `reference_results/<split>/<model>/metrics.json` | a `### Benchmark results (from metrics.json)` block in `## Evaluation results` (coverage and source sha256 included), plus `<benchmark>/<metric>` entries in `metrics:` |

For a non-LLM benchmark, run from the benchmark repo root:

```bash
python scripts/render_card_results.py MODEL_CARD.md --benchmark <name> --model <model> --results reference_results
python scripts/render_card_results.py MODEL_CARD.md --benchmark <name> --model <model> --results reference_results --check
```

- `--check` exits 1 if a number in the card no longer matches its `metrics.json`. Run it
  after every re-run of the reference results, alongside re-checking `rubric.yaml`'s
  evidence (`SKILL.md`, "Iterate").
- Hand-written prose and tables in `## Evaluation results` stay above the block. Write the
  interpretation there ("the exemplar split is out of distribution, so R² < 0 is expected"),
  never inside the block.
- The two tools use different block headings, so they can share a card: tested on one card
  with both blocks, both validators pass.
- The other evaluation sections (`## Evaluation data`, `## Evaluation Procedure`,
  `## Uncertainty Quantification`) stay hand-written for a non-LLM benchmark, from elements
  B and E. If the benchmark has calibration metrics (`references/metrics-and-uq.md`),
  report them in `## Uncertainty Quantification`. They're also in the rendered table.

## Step by step

1. **Ask which card(s) apply.** Model Card when element D is a trained model, Agent Card
   when element D (or the benchmark's own task) is an agentic system, and/or Dataset/Data
   Card for element B. Don't assume all three.
2. **Fetch the current landing page and its linked template/examples live** for each Model
   or Agent card that applies (the table at the top of this file). These are DOE-maintained
   pages this skill has no schema for and no way to keep in sync. Never draft a card from
   memory of an earlier fetch if meaningful time has passed, and never from this file's
   paraphrase of what the template contains.
3. **Map from what this skill already built** ("How this fits what this skill already
   builds", above) rather than re-running the interview. Match the live template's actual
   section headers; don't impose a structure of your own.
4. **Write the evaluation results by script** (the section above), never by hand.
5. **Save each card as its own file** (e.g. `MODEL_CARD.md`, `AGENT_CARD.md`) alongside the
   benchmark card.
6. **For a Data Card, run the genesis `datacard-generator` skill** (above). It writes
   `genesis_datacard_<name>.md` and validates it with `linkml-validate`. Worked example:
   `examples/wa-hls4ml/genesis_datacard_wa_hls4ml.md`.
