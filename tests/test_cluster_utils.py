import os
import sys

import numpy as np
import pandas as pd
import pytest
from sklearn.cluster import DBSCAN, KMeans
from sklearn.datasets import make_blobs

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from layer2.cluster_utils import build_cluster_summary, fit_dbscan, fit_kmeans, pca_project


class TestFitKMeans:
    def test_returns_dict_of_fitted_models(self):
        X, _ = make_blobs(n_samples=60, centers=3, n_features=7, random_state=0)
        result = fit_kmeans(X, k_grid=[2, 3, 4])
        assert set(result.keys()) == {2, 3, 4}
        for k, model in result.items():
            assert isinstance(model, KMeans)
            assert hasattr(model, "labels_")
            assert len(model.labels_) == 60
            assert len(set(model.labels_)) == k

    def test_random_state_determinism(self):
        X, _ = make_blobs(n_samples=40, centers=3, n_features=7, random_state=0)
        first = fit_kmeans(X, k_grid=[3])
        second = fit_kmeans(X, k_grid=[3])
        np.testing.assert_array_equal(first[3].labels_, second[3].labels_)

    def test_k_greater_than_n_samples_raises(self):
        X = np.random.RandomState(0).randn(3, 7)
        with pytest.raises(ValueError):
            fit_kmeans(X, k_grid=[5])


class TestFitDBSCAN:
    def test_two_blobs_recovered(self):
        X, _ = make_blobs(
            n_samples=60, centers=[[0, 0], [10, 10]], cluster_std=0.3, random_state=0
        )
        model = fit_dbscan(X, eps=0.8, min_samples=5)
        assert isinstance(model, DBSCAN)
        non_noise = set(model.labels_) - {-1}
        assert len(non_noise) == 2

    def test_extreme_eps_returns_valid_model(self):
        X, _ = make_blobs(n_samples=30, centers=2, n_features=7, random_state=0)
        all_noise = fit_dbscan(X, eps=1e-6, min_samples=5)
        assert isinstance(all_noise, DBSCAN)
        assert set(all_noise.labels_) == {-1}

        single = fit_dbscan(X, eps=1e6, min_samples=5)
        assert isinstance(single, DBSCAN)
        assert set(single.labels_) == {0}


class TestPcaProject:
    def test_output_shape(self):
        X = np.random.RandomState(0).randn(50, 7)
        coords = pca_project(X)
        assert coords.shape == (50, 2)

    def test_determinism(self):
        X = np.random.RandomState(0).randn(50, 7)
        first = pca_project(X)
        second = pca_project(X)
        np.testing.assert_allclose(first, second)


FEATURE_COLS = [
    "silence_ratio",
    "narration_density",
    "words_per_minute",
    "avg_silence_duration",
    "avg_confidence",
    "unique_words_ratio",
    "avg_sentence_length",
]


def _make_fixture(n: int = 10, seed: int = 0):
    rng = np.random.RandomState(seed)
    X_raw = pd.DataFrame(rng.rand(n, len(FEATURE_COLS)), columns=FEATURE_COLS)
    ids = pd.DataFrame(
        {
            "window_id": [f"w{i}" for i in range(n)],
            "tester_name": ["alice"] * (n // 2) + ["bob"] * (n - n // 2),
            "project": ["wa"] * (n // 3) + ["uq"] * (n - n // 3),
        }
    )
    return X_raw, ids


class TestBuildClusterSummary:
    def test_summary_row_count_matches_unique_clusters(self):
        X_raw, ids = _make_fixture(n=9)
        labels = np.array([0, 0, 0, 1, 1, 1, 2, 2, 2])
        summary, _ = build_cluster_summary(X_raw, labels, ids, FEATURE_COLS, "kmeans")
        assert len(summary) == 3
        assert set(summary["cluster_id"]) == {0, 1, 2}
        assert (summary["algorithm"] == "kmeans").all()
        assert summary["n_windows"].sum() == 9

    def test_composition_row_count(self):
        X_raw, ids = _make_fixture(n=9)
        labels = np.array([0, 0, 0, 1, 1, 1, 2, 2, 2])
        _, composition = build_cluster_summary(X_raw, labels, ids, FEATURE_COLS, "kmeans")
        expected_rows = 0
        for label in set(labels):
            mask = labels == label
            expected_rows += ids.loc[mask, "tester_name"].nunique()
            expected_rows += ids.loc[mask, "project"].nunique()
        assert len(composition) == expected_rows
        assert set(composition["dimension"].unique()) <= {"tester_name", "project"}
        assert (composition["count"] > 0).all()

    def test_raw_mean_matches_manual(self):
        X_raw, ids = _make_fixture(n=6)
        labels = np.array([0, 0, 0, 1, 1, 1])
        summary, _ = build_cluster_summary(X_raw, labels, ids, FEATURE_COLS, "kmeans")
        cluster0_mean = X_raw.iloc[:3].mean()
        row = summary[summary["cluster_id"] == 0].iloc[0]
        for col in FEATURE_COLS:
            assert row[f"{col}_mean"] == pytest.approx(cluster0_mean[col])

    def test_noise_label_kept_as_separate_cluster(self):
        X_raw, ids = _make_fixture(n=8)
        labels = np.array([0, 0, 0, 0, 1, 1, -1, -1])
        summary, composition = build_cluster_summary(X_raw, labels, ids, FEATURE_COLS, "dbscan")
        assert -1 in set(summary["cluster_id"])
        noise_row = summary[summary["cluster_id"] == -1].iloc[0]
        assert noise_row["n_windows"] == 2
        assert -1 in set(composition["cluster_id"])

    def test_singleton_std_is_zero_not_nan(self):
        X_raw, ids = _make_fixture(n=5)
        labels = np.array([0, 0, 0, 0, 1])
        summary, _ = build_cluster_summary(X_raw, labels, ids, FEATURE_COLS, "kmeans")
        row = summary[summary["cluster_id"] == 1].iloc[0]
        for col in FEATURE_COLS:
            assert row[f"{col}_std"] == 0.0
            assert not np.isnan(row[f"{col}_std"])

    def test_missing_id_col_raises(self):
        X_raw, ids = _make_fixture(n=6)
        labels = np.array([0, 0, 0, 1, 1, 1])
        bad_ids = ids.drop(columns=["project"])
        with pytest.raises(ValueError, match="project"):
            build_cluster_summary(X_raw, labels, bad_ids, FEATURE_COLS, "kmeans")

        bad_ids2 = ids.drop(columns=["tester_name"])
        with pytest.raises(ValueError, match="tester_name"):
            build_cluster_summary(X_raw, labels, bad_ids2, FEATURE_COLS, "kmeans")


class TestEndToEnd:
    def test_kmeans_then_summary_pipeline(self):
        X, _ = make_blobs(
            n_samples=30, centers=3, n_features=len(FEATURE_COLS), random_state=0
        )
        X_raw = pd.DataFrame(X, columns=FEATURE_COLS)
        ids = pd.DataFrame(
            {
                "window_id": [f"w{i}" for i in range(30)],
                "tester_name": (["alice"] * 15) + (["bob"] * 15),
                "project": (["wa"] * 10) + (["uq"] * 10) + (["suncorp"] * 10),
            }
        )
        models = fit_kmeans(X, k_grid=[3])
        labels = models[3].labels_
        summary, composition = build_cluster_summary(X_raw, labels, ids, FEATURE_COLS, "kmeans")
        assert len(summary) == 3
        assert summary["n_windows"].sum() == 30
        for cluster_id in summary["cluster_id"]:
            n = int(summary.loc[summary["cluster_id"] == cluster_id, "n_windows"].iloc[0])
            for dim in ("tester_name", "project"):
                s = composition[
                    (composition["cluster_id"] == cluster_id)
                    & (composition["dimension"] == dim)
                ]["count"].sum()
                assert s == n
