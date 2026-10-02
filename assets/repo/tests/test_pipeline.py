"""Golden-output test: fixture samples -> cache -> predict -> compare with recorded goldens.

The portable form of the per-sample verification in docs/VALIDATION.md. Golden CSVs were
recorded from the validated reference run; this test proves a new machine, environment or
GPU reproduces them. Run it on every new machine BEFORE submitting jobs:

    BENCH_WEIGHTS=$BENCH_WEIGHTS python -m pytest tests -q
    BENCH_WEIGHTS=$BENCH_WEIGHTS BENCH_TEST_DEVICE=cuda python -m pytest tests -q   # GPU node

ADAPT (assets/repo/tests/test_pipeline.py in the benchmark-builder skill):
  - rename benchpkg / BENCH_, set SPLITS, MODELS and REQUIRED_WEIGHTS;
  - point predict_fn() at this benchmark's predict entry point;
  - choose tolerances from the measured CPU-vs-GPU spread (axess: rtol 2e-3, atol 1e-2
    against goldens that agreed with the full run to <4e-6);
  - fixtures/data/ holds a few dozen REAL samples per split/subset, including edge cases
    (missing ground truth, id fallbacks, every group); record goldens for every sample,
    scored or not.
"""

import os

import numpy as np
import pandas as pd
import pytest

from benchpkg import cache as C
from benchpkg import data as D
from benchpkg import score as S
from benchpkg.truth import truth_frame

HERE = os.path.dirname(__file__)
FIXTURES = os.path.join(HERE, "fixtures", "data")
WEIGHTS = os.environ.get("BENCH_WEIGHTS", os.path.join(HERE, "..", "weights"))
SPLITS = ("test",)
MODELS = ("model_a",)
REQUIRED_WEIGHTS = ("model_a_final.pt",)
HAVE_WEIGHTS = all(os.path.exists(os.path.join(WEIGHTS, f)) for f in REQUIRED_WEIGHTS)


@pytest.fixture(scope="module")
def caches(tmp_path_factory):
    d = tmp_path_factory.mktemp("cache")
    out = {}
    for split in SPLITS:
        path = str(d / f"{split}.npz")
        C.build_cache(FIXTURES, split, path, workers=1)
        out[split] = C.SplitCache(path)
    return out


def test_truth_excludes_missing(caches):
    # fixtures deliberately include samples without ground truth: excluded, never imputed
    for split, cache in caches.items():
        tf = truth_frame(cache)
        assert np.isfinite(tf[D.TARGETS].to_numpy()).all()
        assert tf["sample_id"].is_unique


def predict_fn(model, cache, device):
    from benchpkg import predict as P
    return P.predict(model, cache, WEIGHTS, device)


@pytest.mark.skipif(not HAVE_WEIGHTS, reason=f"no checkpoints in {WEIGHTS}")
@pytest.mark.parametrize("model", MODELS)
@pytest.mark.parametrize("split", SPLITS)
def test_matches_golden_predictions(caches, model, split):
    device = os.environ.get("BENCH_TEST_DEVICE", "cpu")
    got = predict_fn(model, caches[split], device).set_index("sample_id")
    want = pd.read_csv(os.path.join(HERE, "fixtures", f"golden_{split}_{model}.csv"),
                       dtype={"sample_id": str}).set_index("sample_id")
    assert list(got.index) == list(want.index)
    np.testing.assert_allclose(got[D.TARGETS].to_numpy(), want[D.TARGETS].to_numpy(),
                               rtol=2e-3, atol=1e-2)

    res = S.score(truth_frame(caches[split]), got.reset_index())
    assert res["coverage"]["n_truth_without_prediction"] == 0
