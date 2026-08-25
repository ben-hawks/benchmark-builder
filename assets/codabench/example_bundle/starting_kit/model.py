"""Starting-kit baseline for the toy linear-regression example bundle: predicts the
training mean regardless of input. Deliberately weak -- it's a template showing the
required `Model.fit`/`Model.predict` interface, not a solution. Replace this with your
own model, keep the same interface, zip just this file (no wrapping folder) as
model.py, and submit.
"""

import numpy as np


class Model:
    def __init__(self):
        self.mean_y = 0.0

    def fit(self, X, y):
        self.mean_y = float(np.mean(y))

    def predict(self, X):
        X = np.asarray(X, dtype=float)
        return np.full(X.shape[0], self.mean_y)
