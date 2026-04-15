"""Layer 2 clustering utilities.

Step 4.2: pure functions for fitting KMeans / DBSCAN, building per-cluster
summary + composition, and 2D PCA projection for visualization. No I/O, no
plotting; orchestrated by notebooks/04_layer2_clustering.ipynb.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.cluster import DBSCAN, KMeans
from sklearn.decomposition import PCA

RANDOM_STATE = 42
_REQUIRED_ID_COLS = ("tester_name", "project")


def fit_kmeans(
    X: np.ndarray,
    k_grid: list[int],
    random_state: int = RANDOM_STATE,
) -> dict[int, KMeans]:
    models: dict[int, KMeans] = {}
    for k in k_grid:
        model = KMeans(n_clusters=k, n_init=10, random_state=random_state)
        model.fit(X)
        models[k] = model
    return models


def fit_dbscan(X: np.ndarray, eps: float, min_samples: int) -> DBSCAN:
    model = DBSCAN(eps=eps, min_samples=min_samples)
    model.fit(X)
    return model


def pca_project(
    X: np.ndarray,
    n_components: int = 2,
    random_state: int = RANDOM_STATE,
) -> np.ndarray:
    pca = PCA(n_components=n_components, random_state=random_state)
    return pca.fit_transform(X)


def build_cluster_summary(
    X_raw: pd.DataFrame,
    labels: np.ndarray,
    id_cols: pd.DataFrame,
    feature_cols: list[str],
    algorithm_name: str,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    for required in _REQUIRED_ID_COLS:
        if required not in id_cols.columns:
            raise ValueError(
                f"id_cols must contain '{required}' (got {list(id_cols.columns)})"
            )

    if len(X_raw) != len(labels) or len(id_cols) != len(labels):
        raise ValueError(
            f"length mismatch: X_raw={len(X_raw)}, labels={len(labels)}, "
            f"id_cols={len(id_cols)}"
        )

    X_raw = X_raw.reset_index(drop=True)
    id_cols = id_cols.reset_index(drop=True)
    labels = np.asarray(labels)

    summary_rows: list[dict] = []
    composition_rows: list[dict] = []

    unique_labels = sorted(set(labels.tolist()))
    for cluster_id in unique_labels:
        mask = labels == cluster_id
        block = X_raw.loc[mask, feature_cols]
        row: dict = {
            "algorithm": algorithm_name,
            "cluster_id": int(cluster_id),
            "n_windows": int(mask.sum()),
        }
        for col in feature_cols:
            row[f"{col}_mean"] = float(block[col].mean())
            row[f"{col}_std"] = float(block[col].std(ddof=0))
        summary_rows.append(row)

        for dim in _REQUIRED_ID_COLS:
            counts = id_cols.loc[mask, dim].value_counts()
            for value, count in counts.items():
                composition_rows.append(
                    {
                        "algorithm": algorithm_name,
                        "cluster_id": int(cluster_id),
                        "dimension": dim,
                        "value": str(value),
                        "count": int(count),
                    }
                )

    summary_df = pd.DataFrame(summary_rows)
    composition_df = pd.DataFrame(
        composition_rows,
        columns=["algorithm", "cluster_id", "dimension", "value", "count"],
    )
    return summary_df, composition_df
