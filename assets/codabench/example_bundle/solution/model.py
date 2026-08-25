"""Reference solution for the toy linear-regression example bundle: ordinary least
squares. This is what a real submission is expected to look like -- the ingestion
program imports `Model` from this file and calls `fit`/`predict` on it, so any
submission (including this one, re-zipped as the starting kit's sample_submission.zip)
must expose exactly this interface.
"""

import numpy as np


class Model:
    def __init__(self):
        self.weights = None

    def fit(self, X, y):
        X = np.asarray(X, dtype=float)
        y = np.asarray(y, dtype=float)
        X_with_bias = np.hstack([X, np.ones((X.shape[0], 1))])
        self.weights, *_ = np.linalg.lstsq(X_with_bias, y, rcond=None)

    def predict(self, X):
        X = np.asarray(X, dtype=float)
        X_with_bias = np.hstack([X, np.ones((X.shape[0], 1))])
        return X_with_bias @ self.weights
