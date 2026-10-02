"""Golden-output test: fixture samples -> [preprocess] -> predict -> compare with recorded goldens.

The portable form of the per-sample verification in docs/VALIDATION.md. Golden files were
recorded from the validated reference run; this test proves a new machine, environment or
device reproduces them. Run it on every new machine BEFORE submitting jobs:

    BENCH_WEIGHTS=$BENCH_WEIGHTS python -m pytest tests -q
    BENCH_WEIGHTS=$BENCH_WEIGHTS BENCH_TEST_DEVICE=<device> python -m pytest tests -q   # accelerator node

ADAPT (assets/repo/tests/test_pipeline.py in the benchmark-builder skill):
  - rename benchpkg / BENCH_; set SPLITS, MODELS and REQUIRED_WEIGHTS;
  - point preprocess() and predict_fn() at this benchmark's own entry points (drop
    preprocess() if the benchmark has no cache step);
  - set RTOL/ATOL from the spread you MEASURED between the validated run and a rerun on
    other hardware. Don't copy another benchmark's tolerances: they depend on the model,
    the outputs' scale, and the hardware. For non-numeric outputs, compare exactly;
  - fixtures/data/ holds a few dozen REAL samples per split/subset, including the edge
    cases this benchmark has (e.g. samples without ground truth, ID fallbacks, every
    group); record goldens for every fixture sample, scored or not.
"""

import os

import numpy as np
import pandas as pd
import pytest

from benchpkg import data as D
from benchpkg import score as S
from benchpkg.truth import truth_frame

HERE = os.path.dirname(__file__)
FIXTURES = os.path.join(HERE, "fixtures", "data")
WEIGHTS = os.environ.get("BENCH_WEIGHTS", os.path.join(HERE, "..", "weights"))
SPLITS = ("test",)
MODELS = ("model_a",)
REQUIRED_WEIGHTS = ("model_a.ckpt",)
HAVE_WEIGHTS = all(os.path.exists(os.path.join(WEIGHTS, f)) for f in REQUIRED_WEIGHTS)
RTOL = None  # set from the measured cross-hardware spread
ATOL = None


@pytest.fixture(scope="module")
def cache_dir(tmp_path_factory):
    """Preprocess the fixture samples once (drop if the benchmark has no cache step)."""
    from benchpkg import cache as C
    d = tmp_path_factory.mktemp("cache")
    for split in SPLITS:
        C.build(FIXTURES, split, str(d), workers=1)
    return str(d)


def test_truth_is_valid(cache_dir):
    # however this benchmark handles samples without ground truth, the truth it scores
    # against must be complete and unique
    for split in SPLITS:
        tf = truth_frame(cache_dir, split)
        assert tf["sample_id"].is_unique
        assert tf[list(D.OUTPUT_COLUMNS)].notna().all().all()


def predict_fn(model, cache_dir, split, device):
    from benchpkg import predict as P
    return P.predict(model, cache_dir, split, WEIGHTS, device)


@pytest.mark.skipif(not HAVE_WEIGHTS, reason=f"no checkpoints in {WEIGHTS}")
@pytest.mark.parametrize("model", MODELS)
@pytest.mark.parametrize("split", SPLITS)
def test_matches_golden_predictions(cache_dir, model, split):
    if RTOL is None or ATOL is None:
        pytest.fail("set RTOL/ATOL from the measured spread (see the module docstring)")
    device = os.environ.get("BENCH_TEST_DEVICE", "cpu")
    got = predict_fn(model, cache_dir, split, device).set_index("sample_id")
    want = pd.read_csv(os.path.join(HERE, "fixtures", f"golden_{split}_{model}.csv"),
                       dtype={"sample_id": str}).set_index("sample_id")
    assert list(got.index) == list(want.index)
    cols = list(D.OUTPUT_COLUMNS)
    np.testing.assert_allclose(got[cols].to_numpy(), want[cols].to_numpy(), rtol=RTOL, atol=ATOL)

    res = S.score(truth_frame(cache_dir, split), got.reset_index())
    assert res["coverage"]["n_truth_without_prediction"] == 0
