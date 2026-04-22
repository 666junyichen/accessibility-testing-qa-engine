import os
import sys

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from layer2.feature_diagnosis import (
    build_cluster_dominance,
    compute_pca_loadings,
    compute_tester_specificity,
)


def test_compute_tester_specificity_ranks_tester_specific_features_and_flags_unstable():
    frame = pd.DataFrame(
        {
            "tester_name": ["alice"] * 4 + ["bob"] * 4,
            "tester_style": [0.0, 0.1, -0.1, 0.0, 10.0, 10.1, 9.9, 10.0],
            "within_noise": [0.0, 2.0, -2.0, 1.0, 0.0, 2.0, -2.0, 1.0],
            "constant_by_tester": [3.0] * 8,
            "mild_gap": [0.0, 0.2, -0.2, 0.1, 1.0, 1.2, 0.8, 1.1],
            "mixed": [0.0, 5.0, 1.0, 4.0, 2.0, 7.0, 3.0, 6.0],
        }
    )
    feature_cols = [
        "tester_style",
        "within_noise",
        "constant_by_tester",
        "mild_gap",
        "mixed",
    ]

    result = compute_tester_specificity(
        frame, id_cols=["tester_name"], feature_cols=feature_cols
    )

    assert list(result.columns) == [
        "feature",
        "between_var",
        "within_var",
        "specificity_ratio",
        "median_abs_dev_of_tester_means",
        "max_tester_mean_gap",
        "unstable",
    ]
    assert result.iloc[0]["feature"] == "tester_style"
    constant = result[result["feature"] == "constant_by_tester"].iloc[0]
    assert constant["unstable"] is True
    assert constant["specificity_ratio"] == pytest.approx(0.0)
    assert result["specificity_ratio"].is_monotonic_decreasing


def test_compute_pca_loadings_returns_component_loadings_and_explained_variance():
    frame = pd.DataFrame(
        {
            "x_axis": [-2.0, -1.0, 1.0, 2.0],
            "y_axis": [0.0, 0.0, 0.0, 0.0],
            "z_axis": [0.0, 0.0, 0.0, 0.0],
        }
    )

    result = compute_pca_loadings(
        frame, feature_cols=["x_axis", "y_axis", "z_axis"], n_components=2
    )

    x_row = result[result["feature"] == "x_axis"].iloc[0]
    assert abs(x_row["PC1_loading"]) == pytest.approx(1.0)
    assert result["PC1_explained_variance_ratio"].iloc[0] == pytest.approx(1.0)
    assert "PC2_loading" in result.columns
    assert "PC2_explained_variance_ratio" in result.columns


def test_build_cluster_dominance_records_noise_and_cluster_shares_sum_to_one():
    labels = pd.Series([0, 0, 0, 1, 1, 1, -1, -1], name="cluster")
    ids = pd.DataFrame(
        {
            "tester_name": [
                "alice",
                "alice",
                "bob",
                "alice",
                "bob",
                "bob",
                "alice",
                "bob",
            ],
            "project": ["wa"] * 8,
        }
    )

    result = build_cluster_dominance(
        labels, id_cols=ids, dimension="tester_name"
    )

    assert -1 in set(result["cluster_id"])
    for cluster_id, block in result.groupby("cluster_id"):
        assert block["share_in_cluster"].sum() == pytest.approx(1.0)
        assert (block["cluster_size"] == block["count"].sum()).all()
        assert block["max_dimension_share"].iloc[0] == pytest.approx(
            block["share_in_cluster"].max()
        )
