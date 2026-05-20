"""Regenerate the committed Step 4.2 Layer 2 clustering artifacts."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.layer2.cluster_utils import build_cluster_summary, fit_dbscan, fit_kmeans


FEATURE_COLS = [
    "silence_ratio",
    "narration_density",
    "words_per_minute",
    "avg_silence_duration",
    "avg_confidence",
    "unique_words_ratio",
    "avg_sentence_length",
]

ID_COLS = ["window_id", "video_id", "tester_name", "project"]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Regenerate Layer 2 KMeans/DBSCAN clustering outputs."
    )
    parser.add_argument(
        "--scaled",
        default="data/processed/feature_matrix_scaled.csv",
        help="Scaled feature matrix used for model fitting.",
    )
    parser.add_argument(
        "--raw",
        default="data/processed/feature_matrix_raw.csv",
        help="Raw feature matrix used for cluster summaries.",
    )
    parser.add_argument(
        "--output-dir",
        default="data/processed",
        help="Directory for layer2_cluster_*.csv outputs.",
    )
    parser.add_argument("--final-k", type=int, default=3)
    parser.add_argument("--dbscan-eps", type=float, default=0.8)
    parser.add_argument("--dbscan-min-samples", type=int, default=7)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    scaled = pd.read_csv(args.scaled)
    raw = pd.read_csv(args.raw)

    missing_scaled = sorted(set(ID_COLS + FEATURE_COLS) - set(scaled.columns))
    missing_raw = sorted(set(ID_COLS + FEATURE_COLS) - set(raw.columns))
    if missing_scaled or missing_raw:
        raise ValueError(
            f"missing columns: scaled={missing_scaled}, raw={missing_raw}"
        )

    if not scaled[ID_COLS].equals(raw[ID_COLS]):
        raise ValueError("scaled and raw feature matrices are not row-aligned")

    x_scaled = scaled[FEATURE_COLS].to_numpy()
    x_raw = raw[FEATURE_COLS]
    ids = raw[ID_COLS]

    kmeans_model = fit_kmeans(x_scaled, [args.final_k])[args.final_k]
    dbscan_model = fit_dbscan(
        x_scaled,
        eps=args.dbscan_eps,
        min_samples=args.dbscan_min_samples,
    )

    assignments = ids.copy()
    assignments["kmeans_cluster_id"] = kmeans_model.labels_.astype(int)
    assignments["dbscan_cluster_id"] = dbscan_model.labels_.astype(int)
    assignments["primary_cluster_id"] = assignments["kmeans_cluster_id"]

    kmeans_summary, kmeans_composition = build_cluster_summary(
        x_raw,
        kmeans_model.labels_,
        ids[["tester_name", "project"]],
        FEATURE_COLS,
        "kmeans",
    )
    dbscan_summary, dbscan_composition = build_cluster_summary(
        x_raw,
        dbscan_model.labels_,
        ids[["tester_name", "project"]],
        FEATURE_COLS,
        "dbscan",
    )

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    assignments.to_csv(output_dir / "layer2_cluster_assignments.csv", index=False)
    pd.concat([kmeans_summary, dbscan_summary], ignore_index=True).to_csv(
        output_dir / "layer2_cluster_summary.csv",
        index=False,
    )
    pd.concat([kmeans_composition, dbscan_composition], ignore_index=True).to_csv(
        output_dir / "layer2_cluster_composition.csv",
        index=False,
    )


if __name__ == "__main__":
    main()
