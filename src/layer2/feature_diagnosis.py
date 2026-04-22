"""Feature diagnostics for Layer 2 clustering.

These helpers quantify whether feature/cluster structure is dominated by
tester identity. They return tabular diagnostics only; notebooks handle plots.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.decomposition import PCA


EPS = 1e-9
UNSTABLE_WITHIN_VAR_THRESHOLD = 1e-6


def _ensure_columns(df: pd.DataFrame, cols: list[str], label: str) -> None:
    missing = [col for col in cols if col not in df.columns]
    if missing:
        raise ValueError(f"{label} missing required columns: {missing}")


def compute_tester_specificity(
    X: pd.DataFrame,
    id_cols: list[str],
    feature_cols: list[str],
) -> pd.DataFrame:
    """Compute tester specificity ratio for each feature.

    The ratio is a diagnostic heuristic:
    variance of per-tester feature means divided by average within-tester
    variance. It is not a formal ANOVA F statistic.
    """

    _ensure_columns(X, id_cols + feature_cols, "X")

    rows: list[dict] = []
    grouped = X.groupby(id_cols, dropna=False)

    for feature in feature_cols:
        means = grouped[feature].mean()
        within_vars = grouped[feature].var(ddof=0).fillna(0.0)

        between_var = float(means.var(ddof=0))
        within_var = float(within_vars.mean())
        specificity_ratio = between_var / (within_var + EPS)
        median = float(means.median())
        median_abs_dev = float((means - median).abs().median())
        max_gap = float(means.max() - means.min()) if len(means) else 0.0

        rows.append(
            {
                "feature": feature,
                "between_var": between_var,
                "within_var": within_var,
                "specificity_ratio": float(specificity_ratio),
                "median_abs_dev_of_tester_means": median_abs_dev,
                "max_tester_mean_gap": max_gap,
                "unstable": bool(within_var < UNSTABLE_WITHIN_VAR_THRESHOLD),
            }
        )

    result = pd.DataFrame(
        rows,
        columns=[
            "feature",
            "between_var",
            "within_var",
            "specificity_ratio",
            "median_abs_dev_of_tester_means",
            "max_tester_mean_gap",
            "unstable",
        ],
    )
    result = result.sort_values(
        ["specificity_ratio", "max_tester_mean_gap"],
        ascending=[False, False],
        kind="mergesort",
    ).reset_index(drop=True)
    result["unstable"] = result["unstable"].astype(object)
    return result


def compute_pca_loadings(
    X_scaled: pd.DataFrame,
    feature_cols: list[str],
    n_components: int = 2,
) -> pd.DataFrame:
    """Return PCA feature loadings and explained variance ratios."""

    _ensure_columns(X_scaled, feature_cols, "X_scaled")
    if n_components < 1:
        raise ValueError("n_components must be >= 1")

    matrix = X_scaled[feature_cols].to_numpy()
    pca = PCA(n_components=n_components)
    pca.fit(matrix)

    rows: list[dict] = []
    loadings = pca.components_.T
    for feature_idx, feature in enumerate(feature_cols):
        row: dict = {"feature": feature}
        for component_idx in range(n_components):
            component_name = f"PC{component_idx + 1}"
            row[f"{component_name}_loading"] = float(
                loadings[feature_idx, component_idx]
            )
            row[f"{component_name}_explained_variance_ratio"] = float(
                pca.explained_variance_ratio_[component_idx]
            )
        rows.append(row)

    columns = ["feature"]
    for component_idx in range(n_components):
        component_name = f"PC{component_idx + 1}"
        columns.extend(
            [
                f"{component_name}_loading",
                f"{component_name}_explained_variance_ratio",
            ]
        )
    return pd.DataFrame(rows, columns=columns)


def build_cluster_dominance(
    labels: pd.Series,
    id_cols: pd.DataFrame,
    dimension: str = "tester_name",
) -> pd.DataFrame:
    """Build per-cluster dominance shares for an ID dimension."""

    if dimension not in id_cols.columns:
        raise ValueError(f"id_cols must contain '{dimension}'")
    if len(labels) != len(id_cols):
        raise ValueError(
            f"length mismatch: labels={len(labels)}, id_cols={len(id_cols)}"
        )

    frame = pd.DataFrame(
        {
            "cluster_id": pd.Series(labels).reset_index(drop=True),
            "dimension_value": id_cols[dimension].reset_index(drop=True),
        }
    )

    rows: list[dict] = []
    for cluster_id in sorted(frame["cluster_id"].unique()):
        block = frame[frame["cluster_id"] == cluster_id]
        cluster_size = int(len(block))
        counts = block["dimension_value"].value_counts()
        shares = counts / cluster_size
        max_share = float(shares.max()) if len(shares) else 0.0

        for value, count in counts.items():
            rows.append(
                {
                    "cluster_id": int(cluster_id),
                    "dimension_value": str(value),
                    "count": int(count),
                    "share_in_cluster": float(count / cluster_size),
                    "cluster_size": cluster_size,
                    "max_dimension_share": max_share,
                }
            )

    return pd.DataFrame(
        rows,
        columns=[
            "cluster_id",
            "dimension_value",
            "count",
            "share_in_cluster",
            "cluster_size",
            "max_dimension_share",
        ],
    )
