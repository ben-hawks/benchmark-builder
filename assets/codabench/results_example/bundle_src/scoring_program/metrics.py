"""Vendored copy of the two metric functions this scoring program needs, trimmed from
the skill's scripts/metrics.py. Vendored (not imported) deliberately: scoring_program/
is zipped and uploaded to Codabench standalone, so it can't reach back into the rest of
the skill at runtime -- see references/codabench.md's "Vendor shared code" section.
Keep this in sync with scripts/metrics.py by hand if the source functions change.
"""

import numpy as np


def r_squared(y_true, y_pred):
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)
    ss_res = np.sum((y_true - y_pred) ** 2)
    ss_tot = np.sum((y_true - np.mean(y_true)) ** 2)
    if ss_tot == 0:
        return float("nan")
    return float(1.0 - ss_res / ss_tot)


def rmse(y_true, y_pred):
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)
    return float(np.sqrt(np.mean((y_true - y_pred) ** 2)))
