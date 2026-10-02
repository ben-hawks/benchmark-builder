# Metric cross-checks and uncertainty metrics (element C)

Two things element C asks for beyond choosing the metrics (`SKILL.md`, element C):

1. an **independent recomputation** of the benchmark's metrics on a reference solution's
   predictions;
2. a decision about **uncertainty**: whether calibration belongs among the benchmark's
   metrics, and whether its reference solution's uncertainty handling needs an audit.

Both use genesis skills from `skills/basesafe-skills/` (`references/genesis-skills.md`
says how to load them). The benchmark's own `score.py` stays the source of truth either
way. It's what ships in the Codabench scoring program, so it can't depend on another
skill being installed.

## Independent recomputation with `uq-metrics-evaluator`

**When:** the benchmark is regression or classification, and its `score.py` computes
standard metrics (R², RMSE, MAE, accuracy, ROC-AUC, ...) itself or through
`scripts/metrics.py`. Bespoke metrics have no second implementation to compare against.
For those, the edge-case tests in `tests/test_score.py` and the reproduction of a published
number (element C) are the checks.

**How:**

1. **Join first.** The tool aligns rows by position, not by key. Join
   `predictions_<model>.csv` with `truth.csv` on `sample_id`, keeping exactly the scored
   samples. Write the joined CSV to a scratch directory outside the benchmark's results,
   because the tool writes its artifacts (residuals, plots) next to its input.
2. **Run it from that directory.** It refuses inputs outside `--allowed-root` (default:
   the current directory) and symlinked inputs. Pass the joined file as both the
   predictions and the truth file, with `--pred-col`/`--truth-col` (plus
   `--uncertainty-col` or `--prob-col` if they exist).
3. **Check `row_count` equals the benchmark's `n_scored`.** The tool:
   - drops rows with a missing value in any selected column;
   - reads at most 500,000 rows (`MAX_ROWS`) **without warning**.

   For a larger split, check a random subset of at most 500,000 scored samples and say so.
   If the benchmark scores missing predictions as failures, the tool's numbers aren't
   comparable on those rows; compare on the rows both score.
4. **Compare and record.** The tool rounds its outputs to 4 significant figures, so
   "agrees" means agreeing to that precision. Write the table, the tool's commit and the
   date into `docs/VALIDATION.md` ("Independent metric recomputation").

**What corresponds to what** (checked 2026-10-02 at the pinned commit, on synthetic data:
2,000 regression and 2,000 binary-classification samples):

| `scripts/metrics.py` | `uq-metrics-evaluator` | Same definition? |
|---|---|---|
| `r_squared`, `rmse`, `mae` | `r2`, `rmse`, `mae` | yes (agreed to all printed digits) |
| `roc_auc` | `roc_auc` | yes |
| `classification_report()["accuracy"]` | `accuracy` | yes |
| `classification_report()` precision/recall/F1 (positive class) | `precision_macro`, `recall_macro`, `f1_macro` | **no**: macro averages over classes. Compare only if `score.py` also macro-averages. |
| `smape`, `relative_l2_error`, `relative_percent_error` | — (`marpd` is a different relative error) | no counterpart |
| `brier_score` | `brier_score` | yes |
| `expected_calibration_error` (`ece`, `mce`) | `expected_calibration_error`, `max_calibration_error` | yes, 10 equal-width bins, unless some probability is exactly 1.0 (the tool's half-open bins drop it) |
| `gaussian_nll` | `nll` | yes |
| `interval_calibration` (`mean_`/`rms_calibration_error`) | `mean_calibration_error`, `rms_calibration_error` | yes (uncertainty-toolbox, 100 central intervals) |
| — | `miscalibration_area`, `sharpness`, `crps`, `check_score`, `interval_score` | not in `scripts/metrics.py`; use the tool's values only as a cross-check, or implement them in `score.py` |

A disagreement is a finding, not noise. Before recording it, look for its cause:
- different sample sets;
- a different definition (macro vs positive class, ε in SMAPE);
- a bug in `score.py`.

## Uncertainty and calibration

### Do calibration metrics belong in this benchmark?

Ask when either holds:
- a reference solution outputs a predictive uncertainty (a standard deviation, an interval,
  an ensemble spread) or class probabilities;
- the scientific use of the benchmark depends on knowing when a prediction is unreliable.
  For example, a surrogate that gates whether a simulation still has to be run, or a
  classifier whose scores set an alarm threshold.

If calibration is part of what matters, it belongs in the benchmark's metrics. Leaving it
out costs Metric Quality credit ("captures what matters"). If no model is expected to
produce uncertainties, don't add calibration metrics only because they're available.

When adding them, settle the definition the same way as any other metric:

- **What participants must submit.** Extra columns in the prediction file: `<output>_std`
  per regression output, or `prob_<class>` per class. Update `data/SCHEMA.md`,
  `SUBMISSION.md`, `submission.py`'s `check_values()` and the Codabench scoring program's
  validity checks. A std must be finite and > 0; probabilities must be in [0, 1] and, for
  multi-class, sum to 1 within a stated tolerance.
- **Models without uncertainty.** Is their calibration score "not applicable" (blank on
  the leaderboard), or scored with a stated default? Decide this, and don't rank on a
  calibration metric that only some entries can have.
- **Exact definitions.** Gaussian or not (`gaussian_nll` and `interval_calibration`
  assume a Gaussian predictive distribution with the submitted std). Number of bins for
  ECE. Positive-class vs top-label ECE for classification.
- **Implementation.** Implement the definitions in `score.py`, from `scripts/metrics.py`
  where they fit, and cross-check with `uq-metrics-evaluator` as above.
- **Reliability plot.** Optional, generated by `score.py` (the curve is in
  `interval_calibration()["observed"]`), with the tool's plot as a visual cross-check.

### Auditing the reference solution with `uncertainty-quantification`

**When:** a reference model's confidence is meant to drive decisions (abstention,
escalation, gating a downstream step), or the user asks how the benchmark handles
uncertainty.

Load the skill and run its workflow on the reference solution's code. Its classification
of each UQ control (implemented / partial / missing / unknown, with file evidence) goes in:
- `docs/VALIDATION.md`, as a short section linking the full report;
- the `evidence:` of the Performance Metrics `quality_level` in `rubric.yaml`, when it bears
  on whether the metrics "capture what matters".

It's an audit, not a metric. It doesn't change the leaderboard by itself.
