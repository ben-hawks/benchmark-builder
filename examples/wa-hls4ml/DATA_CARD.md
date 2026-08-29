# wa-hls4ml Dataset — Data Card

Structured against the **Genesis Mission Data Card v1.2** outline (the template the DOE
GEAR FAIR page links to via `github.com/AI-ModCon/BaseData_Skills`'s
`datacard-generator` skill, fetched 2026-08-28). That generator tool does more than this
card does by hand — directory introspection (`scripts/introspect.py`) and **mandatory
live identifier verification** against ORCID/ROR/DOI/OSTI APIs before a real submission
is considered valid (`scripts/validate_datacard.py`). Neither of those ran here; this is
a best-effort manual fill from public sources (the paper, the repo, the Hugging Face
dataset card), and every place that would normally require live verification is flagged
below rather than asserted as confirmed. Treat this as a draft for a human (or the actual
generator tool, run properly) to finish, not a submission-ready card.

## `supports_*` capability flags

| Flag | Value | Why |
|---|---|---|
| `supports_discoverability` | Yes | Always required per the schema |
| `supports_accessibility` | Yes | Dataset is openly shared on Hugging Face |
| `supports_interoperability` | Yes | Fixed, documented JSON schema; standard HF `datasets` loading |
| `supports_reusability` | Yes | Explicitly licensed (CC-BY-NC 4.0), versioned, generation code public |
| `supports_governed_use` | No | No access restrictions, PII, or compliance regime identified in source material |
| `supports_ai_usability` | Yes | Purpose-built as an ML training/benchmark dataset |

## Discoverability [REQUIRED]

**Data Card metadata**
- `created_date`: 2026-08-28 (this card's assembly date)
- `template_version`: 1.2
- `creation_method`: Hybrid (built from public-source extraction, not directory
  introspection or interview)
- `language`: en

**Identification**
- `name`: wa-hls4ml
- `version`: not separately versioned beyond the Hugging Face dataset revision at time of
  access — **needs live check** against the HF repo's own commit/version history if a
  precise version string is required.
- `id`: not assigned here (no ARK/DOI minted for this card itself); the *paper's* DOI
  (10.1145/3787490) is not the same as a dataset-specific identifier — **flag for the
  user**: check whether the dataset itself has (or should get) its own OSTI DOI/ARK,
  separate from the paper's.

**Description.** 683,176 fully hardware-synthesized samples (Keras/QKeras model +
hls4ml conversion config → post-synthesis FPGA resource/latency ground truth), built to
train and evaluate surrogate models that predict synthesis outcomes without running
synthesis. See `BENCHMARK_CARD.md` section 2 for the full schema.

**Product & Dataset Type.** Structured/tabular (JSON records); ML training + benchmark
evaluation dataset.

**Release Status.** Published (publicly available on Hugging Face at time of this card's
assembly).

**Dataset Contacts.** Not filled in — no single corresponding contact for the dataset
specifically (as opposed to the paper's author list) was found in the source material.
**Ask the user** rather than defaulting to anyone's personal contact info here, per this
skill's standing rule for the MLCommons corpus entry's `contact` field.

**Authorship & Credit.** Benjamin Hawks, Jason Weitz, and coauthors (full list in the
paper) — CRediT roles (the generator's own v2 vocabulary requires 16 standardized values
per author) are **not assigned here**; that requires either the paper's own contribution
statement or asking the authors directly, not a guess.

**Sponsor Organizations / Research Organizations / Facilities.** Not confirmed from the
source material fetched for this card — the paper's acknowledgments section (not fetched
here) would be the authoritative source; **flag as a gap**, don't fabricate a DOE lab
affiliation from the "Fast Machine Learning Lab" name alone.

**Genesis Sensitivity & Security.** Public — no restricted-access, PII, or export-control
indicators found. (This is also why `supports_governed_use = No` above.)

**Workflow & Lifecycle.** `workflow.state`: published/stable (no indication of active
in-progress revision as of access). Per the generator's own gotcha list, this is
independent from `release_status` — both are set to essentially the same value here
because nothing in the source material suggests they'd diverge, not because they're
redundant by definition.

## Accessibility [accessibility_required]

**Access Policy.** Open, no login/agreement required.

**Access Endpoints.** `https://huggingface.co/datasets/fastmachinelearning/wa-hls4ml`
(main dataset, 4.98 GB); a companion `fastmachinelearning/wa-hls4ml-projects` dataset
holds the full synthesis logs/project archives referenced by each sample's `meta_data`.

**Dataset Scale & Size Metrics.**
- Record count: 683,176 total samples (478,220 train / 102,472 validation / 102,484 test
  / 887 exemplar).
- Compressed size: 4.98 GB (main dataset only; companion projects dataset size not
  stated in source material).

## Interoperability [interoperability_required]

**Dataset Structure (format, encoding, features).** One JSON object per sample, UTF-8,
with 9 fixed top-level fields: `meta_data`, `model_config`, `hls_config`,
`resource_report`, `hls_resource_report`, `latency_report`, `target_part`,
`vivado_version`, `hls4ml_version` — see `BENCHMARK_CARD.md` section 2 for what each
contains. Loadable via the standard Hugging Face `datasets` library.

**Provenance (`was_generated_by`).** Generated via the `wa-hls4ml-search` code
(submodule of `fastmachinelearning/wa-hls4ml-paper`, Apache 2.0), which drives real
Vivado/Vitis HLS synthesis runs per sample — this is real hardware-synthesis output, not
simulated. This is the one provenance field the generator skill's own gotcha list flags
as "often forgotten" — included here deliberately.

**Dates.** Paper/dataset associated with the 2025 arXiv submission (2511.05615) /
2026 ACM TRETS publication; exact dataset first-published date not separately stated in
source material — **needs live check** against the HF repo's own creation timestamp.

**Domain Metadata.** FPGA target part, Vivado/Vitis version, and hls4ml version are
recorded per-sample (`target_part`, `vivado_version`, `hls4ml_version`) — this *is* the
domain metadata, not a separate add-on.

## Reusability [reusability_required]

**License & Rights.** CC-BY-NC 4.0 (SPDX: `CC-BY-NC-4.0`) for the dataset itself. Note
this is **narrower** than an unrestricted-reuse license (non-commercial only) — worth
calling out explicitly to a prospective reuser rather than leaving "licensed" ambiguous
about which license.

**Stewardship & Versioning.** Versioned via the Hugging Face dataset's own revision
history; no separate DOE-side stewardship plan identified in source material.

**Data Quality.** Every sample is a real synthesis output (not simulated/estimated), so
label quality is bounded by Vivado/Vitis HLS's own synthesis accuracy rather than a
separate annotation process — no known labeling-error rate is stated.

**Dataset Citation.**
```bibtex
@misc{hawks2025wahls4mlbenchmarksurrogatemodels,
      title={wa-hls4ml: A Benchmark and Surrogate Models for hls4ml
      Resource and Latency Estimation},
      author={Benjamin Hawks and Jason Weitz and others},
      year={2025},
      eprint={2511.05615},
      archivePrefix={arXiv},
      primaryClass={cs.LG},
      url={https://arxiv.org/abs/2511.05615}
}
```
DOI (published version): 10.1145/3787490.

**Integrity & Fixity.** Not stated in source material (no checksum/hash manifest found)
— **flag as a gap**, don't invent a checksum.

## Governed Use [governed_use_required — set to No above, included for completeness]

**Use Governance.** None identified — open, non-commercial-use dataset with no PII,
export-control, or restricted-access indicators in the source material reviewed.

## AI Usability

- `training_use_status`: Yes — this is the dataset's primary designed purpose.
- `inference_use_status`: Conditional — a trained surrogate model's *inputs* at inference
  time are the same `model_config`/`hls_config` shape as this dataset's records, but the
  dataset itself isn't consumed at inference time.
- `evaluation_use_status`: Yes — the Test and Exemplar splits are the benchmark's own
  evaluation sets (see `BENCHMARK_CARD.md` section 2/3).

---

**Gaps requiring a live check or a human decision, listed explicitly rather than
silently resolved:** a dataset-specific identifier (ARK/OSTI DOI) distinct from the
paper's DOI; dataset contact info; CRediT-role author attribution; sponsor/research
organization and facility affiliations; exact first-published date; and a fixity/checksum
manifest. Per this skill's own `references/mlcommons-corpus-format.md` precedent, none of
these are guessed to make the card look more complete than it is.
