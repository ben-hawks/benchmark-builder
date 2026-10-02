"""A small toolkit of generic building blocks for the "Performance Metric(s)" element of
the MLCommons Science Benchmarks Ontology (arXiv:2511.05614) -- NOT a default metric suite.

There is no universal "the metrics" for this ontology. What a benchmark should measure is a
function of its AI/ML motif and scientific question (see references/ontology.md's "What
metrics do comparable existing benchmarks actually use?" table): a generative-chemistry
benchmark needs validity/docking scores, an RL/control benchmark needs stability loss and
control latency, a multimodal-reasoning benchmark needs task-specific accuracy per modality.
None of those are implemented here, on purpose -- they're genuinely bespoke, and a benchmark
whose metrics don't actually fit its task loses rubric Category 4 (Performance Metrics)
credit regardless of how polished the code computing them is.

What IS implemented here are primitives for the two motifs common enough, and generic
enough, to be worth not reimplementing every time: regression (r_squared, smape, rmse, mae,
relative_l2_error, relative_percent_error + plot_rpe_boxplot) and classification/anomaly
detection (classification_report, roc_auc), plus calibration metrics for models that output
an uncertainty or a probability (brier_score, expected_calibration_error, gaussian_nll,
interval_calibration; see references/metrics-and-uq.md for when they belong in a
benchmark). The regression trio's epsilon handling in particular (see smape's docstring)
mirrors wa-hls4ml (arXiv:2511.05615, Section 3.2) specifically because it's easy to get
subtly wrong, not because R^2/SMAPE/RMSE are the "correct" choice for every regression
benchmark -- swap in mae or relative_l2_error instead where those fit better (see
FEABench/CFDBench in the ontology.md table), or write something else entirely if the task
calls for it.

This module only requires numpy (and the standard library) for the metric functions;
matplotlib is only imported inside plot_rpe_boxplot, so importing this module doesn't
require a display backend.

Usage:
    import numpy as np
    from metrics import r_squared, smape, rmse, relative_percent_error, plot_rpe_boxplot

    y_true = np.array([...])
    y_pred = np.array([...])
    print(r_squared(y_true, y_pred), smape(y_true, y_pred), rmse(y_true, y_pred))
"""

from __future__ import annotations

import numpy as np


# ---------------------------------------------------------------------------
# Regression metrics (wa-hls4ml Section 3.2, Eq. 1-4)
# ---------------------------------------------------------------------------


def r_squared(y_true, y_pred):
    """Coefficient of determination (R^2). 1.0 is perfect; can go negative for a fit
    worse than predicting the mean. Returns nan if y_true is constant (variance is zero) --
    check for that case explicitly before relying on this (see wa-hls4ml's "N/A*" footnote
    for exactly this situation with the Quarks exemplar model)."""
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)
    ss_res = np.sum((y_true - y_pred) ** 2)
    ss_tot = np.sum((y_true - np.mean(y_true)) ** 2)
    if ss_tot == 0:
        return float("nan")
    return float(1.0 - ss_res / ss_tot)


def smape(y_true, y_pred, epsilon=None):
    """Symmetric mean absolute percentage error, as a percentage (0-200 range).

    `epsilon` avoids division by zero when both y_true and y_pred are 0. wa-hls4ml sets it
    to "the smallest strictly positive value the variable can have" -- for integer counts
    (resource/latency values) that's 1; for a continuous target, pick the smallest
    meaningful unit for that variable rather than an arbitrary tiny constant. If you don't
    pass one, this defaults to 1.0 -- override it if that's not appropriate for your metric.
    """
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)
    eps = 1.0 if epsilon is None else epsilon
    denom = np.abs(y_true) + np.abs(y_pred) + eps
    return float(200.0 * np.mean(np.abs(y_true - y_pred) / denom))


def rmse(y_true, y_pred):
    """Root mean square error. Same units as the target; sensitive to outliers."""
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)
    return float(np.sqrt(np.mean((y_true - y_pred) ** 2)))


def mae(y_true, y_pred):
    """Mean absolute error. Same units as the target; unlike RMSE, doesn't disproportionately
    punish outliers -- often the better fit when large errors on rare samples shouldn't
    dominate the score (e.g. Delta^2-DFT, SuperCon3D; see ontology.md's motif table)."""
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)
    return float(np.mean(np.abs(y_true - y_pred)))


def relative_l2_error(y_true, y_pred, axis=None):
    """Relative L2 (norm-ratio) error: ||y_pred - y_true||_2 / ||y_true||_2. Common for
    field/surrogate-modeling benchmarks (e.g. CFDBench, PDE surrogate models) where the
    quantity of interest is a whole spatial/temporal field rather than independent scalar
    samples, so a plain per-element average like RMSE/MAE undersells how correlated the
    errors are across the field. Pass `axis` to compute per-sample errors over a batch of
    fields rather than one number over the whole array (e.g. axis=-1 if each row is one
    flattened field)."""
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)
    num = np.linalg.norm(y_pred - y_true, axis=axis)
    denom = np.linalg.norm(y_true, axis=axis)
    return num / denom if axis is not None else float(num / denom)


def relative_percent_error(y_true, y_pred, epsilon=1.0):
    """Per-sample relative percent error: (y_true - y_pred) / (y_true + epsilon) * 100.
    Signed -- positive means under-prediction, negative means over-prediction. This is a
    per-sample array, meant for distribution visualization (see plot_rpe_boxplot), not a
    single scalar summary."""
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)
    return (y_true - y_pred) / (y_true + epsilon) * 100.0


def regression_report(y_true, y_pred, epsilon=None):
    """Convenience: compute the R^2/SMAPE/RMSE trio at once, returned as a dict. This is
    the wa-hls4ml-style trio specifically, not "the" regression report -- if mae or
    relative_l2_error fit your benchmark's task better (see ontology.md's motif table),
    call them directly and build your own dict rather than assuming this one is complete
    for your case."""
    return {
        "r_squared": r_squared(y_true, y_pred),
        "smape": smape(y_true, y_pred, epsilon=epsilon),
        "rmse": rmse(y_true, y_pred),
    }


def plot_rpe_boxplot(errors_by_target, out_path, title="Relative Percent Error", symlog=True):
    """Box plot of per-target RPE distributions, matching the style used in wa-hls4ml
    Figures 7-12: one box per target variable, median and mean both marked, y-axis on a
    symmetric log scale by default (RPE distributions are typically heavy-tailed).

    Args:
        errors_by_target: dict of {target_name: array_of_rpe_values}, e.g.
            {"BRAM": rpe_bram, "DSP": rpe_dsp, ...} where each array comes from
            relative_percent_error().
        out_path: file path to save the figure to (png/pdf, inferred from extension).
        title: plot title.
        symlog: use a symmetric log y-axis (handles the long tails typical of RPE data);
            set False for a linear axis if your errors are small and tightly distributed.
    """
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    labels = list(errors_by_target.keys())
    data = [np.asarray(errors_by_target[k]) for k in labels]

    fig, ax = plt.subplots(figsize=(max(6, len(labels) * 1.5), 5))
    bp = ax.boxplot(data, labels=labels, showmeans=True, meanline=True, patch_artist=True)
    for patch in bp["boxes"]:
        patch.set_facecolor("#a6c8ff")
    for median in bp["medians"]:
        median.set_color("orange")
        median.set_linestyle("--")
    for mean in bp["means"]:
        mean.set_color("green")
        mean.set_linestyle("--")

    if symlog:
        ax.set_yscale("symlog")
    ax.set_ylabel("Relative Percent Error [%]")
    ax.set_title(title)
    ax.axhline(0, color="gray", linewidth=0.5)
    fig.tight_layout()
    fig.savefig(out_path)
    plt.close(fig)
    return out_path


# ---------------------------------------------------------------------------
# Classification / anomaly-detection metrics (numpy only, no sklearn dependency)
# ---------------------------------------------------------------------------


def confusion_counts(y_true, y_pred, positive_label=1):
    """Binary confusion matrix counts. For multi-class, one-vs-rest: pass the class of
    interest as positive_label and treat everything else as negative."""
    y_true = np.asarray(y_true)
    y_pred = np.asarray(y_pred)
    tp = int(np.sum((y_true == positive_label) & (y_pred == positive_label)))
    tn = int(np.sum((y_true != positive_label) & (y_pred != positive_label)))
    fp = int(np.sum((y_true != positive_label) & (y_pred == positive_label)))
    fn = int(np.sum((y_true == positive_label) & (y_pred != positive_label)))
    return {"tp": tp, "tn": tn, "fp": fp, "fn": fn}


def classification_report(y_true, y_pred, positive_label=1):
    """Accuracy, precision, recall, and F1 for a binary (or one-vs-rest) classification
    task. Returns 0.0 for precision/recall/F1 when the denominator is zero rather than
    raising, since "no positive predictions/labels" is a valid, if degenerate, outcome
    worth reporting rather than crashing on."""
    c = confusion_counts(y_true, y_pred, positive_label=positive_label)
    total = c["tp"] + c["tn"] + c["fp"] + c["fn"]
    accuracy = (c["tp"] + c["tn"]) / total if total else float("nan")
    precision = c["tp"] / (c["tp"] + c["fp"]) if (c["tp"] + c["fp"]) else 0.0
    recall = c["tp"] / (c["tp"] + c["fn"]) if (c["tp"] + c["fn"]) else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) else 0.0
    return {
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        **c,
    }


def roc_auc(y_true, y_score):
    """ROC-AUC via the rank-sum (Mann-Whitney U) method -- no sklearn required. y_true
    must be binary (0/1); y_score is the predicted probability/score for the positive
    class. Returns nan if y_true is all one class (AUC is undefined)."""
    y_true = np.asarray(y_true)
    y_score = np.asarray(y_score, dtype=float)
    n_pos = np.sum(y_true == 1)
    n_neg = np.sum(y_true == 0)
    if n_pos == 0 or n_neg == 0:
        return float("nan")
    order = np.argsort(y_score)
    ranks = np.empty_like(order, dtype=float)
    ranks[order] = np.arange(1, len(y_score) + 1)
    # handle ties by averaging ranks
    _, inv, counts = np.unique(y_score, return_inverse=True, return_counts=True)
    sum_ranks = np.zeros(len(counts))
    np.add.at(sum_ranks, inv, ranks)
    avg_ranks = sum_ranks / counts
    ranks = avg_ranks[inv]
    sum_ranks_pos = np.sum(ranks[y_true == 1])
    auc = (sum_ranks_pos - n_pos * (n_pos + 1) / 2) / (n_pos * n_neg)
    return float(auc)


# ---------------------------------------------------------------------------
# Calibration / uncertainty metrics (numpy + stdlib only)
#
# Only for benchmarks whose models output an uncertainty (a Gaussian std per prediction) or
# a class probability, and where calibration is part of what the benchmark measures
# (references/metrics-and-uq.md). The definitions match the genesis uq-metrics-evaluator
# skill (uncertainty-toolbox for regression, its own ECE/Brier for classification), so that
# skill can serve as an independent cross-check; differences are noted per function.
# ---------------------------------------------------------------------------


def brier_score(y_true, y_prob):
    """Mean squared error between the predicted positive-class probability and the 0/1
    label (binary). Lower is better; 0.25 is what a constant 0.5 scores."""
    y_true = np.asarray(y_true, dtype=float)
    y_prob = np.asarray(y_prob, dtype=float)
    return float(np.mean((y_prob - y_true) ** 2))


def expected_calibration_error(y_true, y_prob, n_bins=10):
    """Binary ECE and MCE of the positive-class probability, with equal-width bins.

    ECE = sum over bins of (bin fraction) * |fraction positive - mean probability|; MCE is
    the largest per-bin gap. Empty bins are skipped. The last bin is closed ([0.9, 1.0]),
    so a probability of exactly 1.0 is counted. (uq-metrics-evaluator uses half-open bins
    everywhere, which drops p == 1.0 from every bin; the two agree whenever no probability
    is exactly 1.0.) This is the calibration of the positive-class probability, not the
    "top-label confidence" ECE used for multi-class models; say which one the benchmark
    reports."""
    y_true = np.asarray(y_true, dtype=float)
    y_prob = np.asarray(y_prob, dtype=float)
    edges = np.linspace(0.0, 1.0, n_bins + 1)
    idx = np.clip(np.searchsorted(edges, y_prob, side="right") - 1, 0, n_bins - 1)
    ece, mce, n = 0.0, 0.0, len(y_true)
    for b in range(n_bins):
        mask = idx == b
        if not mask.any():
            continue
        gap = abs(y_true[mask].mean() - y_prob[mask].mean())
        ece += mask.sum() / n * gap
        mce = max(mce, gap)
    return {"ece": float(ece), "mce": float(mce)}


def gaussian_nll(y_true, mu, sigma):
    """Mean negative log-likelihood of y_true under N(mu, sigma^2), per sample. sigma must
    be strictly positive; a benchmark should reject submissions where it isn't rather than
    clip it. Matches uncertainty-toolbox's nll_gaussian (scaled)."""
    y_true = np.asarray(y_true, dtype=float)
    mu = np.asarray(mu, dtype=float)
    sigma = np.asarray(sigma, dtype=float)
    if np.any(sigma <= 0):
        raise ValueError("gaussian_nll: sigma must be > 0 for every sample")
    z = (y_true - mu) / sigma
    return float(np.mean(0.5 * np.log(2 * np.pi) + np.log(sigma) + 0.5 * z**2))


def interval_calibration(y_true, mu, sigma, n_levels=100):
    """Calibration of Gaussian central prediction intervals.

    For each expected coverage p in linspace(0, 1, n_levels), the observed coverage is the
    fraction of samples with |y - mu| / sigma <= z_p, where z_p is the two-sided
    standard-normal quantile (z_0 = 0, z_1 = inf). Returns the mean and RMS absolute gap between expected and
    observed coverage (uncertainty-toolbox's mean_absolute_calibration_error and
    root_mean_squared_calibration_error with prop_type="interval"), plus the curve itself for
    a reliability plot. 0 is perfectly calibrated."""
    from statistics import NormalDist

    y_true = np.asarray(y_true, dtype=float)
    mu = np.asarray(mu, dtype=float)
    sigma = np.asarray(sigma, dtype=float)
    if np.any(sigma <= 0):
        raise ValueError("interval_calibration: sigma must be > 0 for every sample")
    abs_z = np.abs((y_true - mu) / sigma)
    expected = np.linspace(0.0, 1.0, n_levels)
    nd = NormalDist()
    z = [float("inf") if p >= 1.0 else nd.inv_cdf(0.5 + p / 2) for p in expected]
    observed = np.array([np.mean(abs_z <= zp) for zp in z])
    gaps = np.abs(observed - expected)
    return {
        "mean_calibration_error": float(np.mean(gaps)),
        "rms_calibration_error": float(np.sqrt(np.mean(gaps**2))),
        "expected": expected.tolist(),
        "observed": observed.tolist(),
    }


if __name__ == "__main__":
    # Smoke test / usage example.
    rng = np.random.default_rng(0)
    y_true = rng.integers(10, 1000, size=200).astype(float)
    y_pred = y_true * rng.normal(1.0, 0.1, size=200)

    print("Regression report:", regression_report(y_true, y_pred))

    rpe = relative_percent_error(y_true, y_pred)
    print("RPE mean/median:", np.mean(rpe), np.median(rpe))

    y_true_c = rng.integers(0, 2, size=200)
    y_pred_c = rng.integers(0, 2, size=200)
    print("Classification report:", classification_report(y_true_c, y_pred_c))
    print("ROC-AUC (random scores):", roc_auc(y_true_c, rng.random(200)))
