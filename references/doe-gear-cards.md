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
Data Card is not: the FAIR page's own link goes to a full external skill
(`AI-ModCon/BaseData_Skills`'s `datacard-generator`) implementing the
**Genesis Mission Data Card v1.2** schema — a large (100+ KB), multi-section
template (Discoverability/Accessibility/Interoperability/Reusability/
Governed Use/AI Usability) with its own directory-introspection script and,
critically, **mandatory live identifier verification** (ORCID/ROR/DOI/OSTI,
checked against live APIs) before the tool considers a card valid. Two real
consequences:

- **Prefer running the generator's workflow properly**, even when it isn't
  installed as a skill. Clone `AI-ModCon/BaseData_Skills`, read
  `skills/datacard-generator/SKILL.md`, and follow its steps:
  1. introspect the data (`scripts/introspect.py`);
  2. resolve any DOI and apply its provenance gate (a paper DOI is related work,
     not the dataset's identity);
  3. ask the user the questions only they can answer: authors and CRediT roles,
     sponsors, identifiers, AI-usage statuses, science domain;
  4. verify every ORCID and ROR live;
  5. write the YAML frontmatter and the narrative body;
  6. validate with
     `uv run --with linkml linkml-validate -s scripts/genesis_datacard.yaml -C GenesisDatacardClass <frontmatter.yaml>`.

  `examples/wa-hls4ml/genesis_datacard_wa_hls4ml.md` is a worked example that
  validates clean. Building it surfaced facts no hand-filled card had: 3 `null`
  array entries in train/val, record counts that differ from the dataset card's,
  and a public dCache mirror.
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
  whatever fields the current template asks for. Map field-by-field once
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
