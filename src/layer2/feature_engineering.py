"""Layer 2 feature engineering.

Step 4.1: build L2-only feature matrix (raw + scaled) from audio_features.csv
and windows.csv. Not used for L3 / R5 / R6.
"""

import logging
import re
from pathlib import Path

import pandas as pd
from sklearn.preprocessing import StandardScaler

FEATURE_COLS = [
    "silence_ratio",
    "narration_density",
    "words_per_minute",
    "avg_silence_duration",
    "avg_confidence",
    "unique_words_ratio",
    "avg_sentence_length",
]

ID_COLS = [
    "window_id",
    "video_id",
    "video_filename",
    "tester_name",
    "project",
    "start_time",
    "end_time",
]

NAN_THRESHOLD = 0.01  # 1%

AUDIO_FEATURE_COLS = [
    "silence_ratio",
    "narration_density",
    "words_per_minute",
    "avg_silence_duration",
    "avg_confidence",
]

TEXT_FEATURE_COLS = ["unique_words_ratio", "avg_sentence_length"]

_SENTENCE_SPLIT = re.compile(r"[.!?]")
_OVERLAP_COLS_EXACT = ["video_id", "video_filename"]
_OVERLAP_COLS_FLOAT = ["start_time", "end_time"]
_FLOAT_TOL = 1e-6

logger = logging.getLogger(__name__)


def _has_alnum(token: str) -> bool:
    return any(ch.isalnum() for ch in token)


def _tokenize(text: str) -> list[str]:
    return [token for token in text.lower().split() if _has_alnum(token)]


def _count_sentences(text: str) -> int:
    parts = [part.strip() for part in _SENTENCE_SPLIT.split(text)]
    valid_parts = [part for part in parts if part]
    return max(1, len(valid_parts))


def build_text_features(text: str) -> dict:
    if text is None:
        return {"unique_words_ratio": 0.0, "avg_sentence_length": 0.0}

    tokens = _tokenize(text)
    if not tokens:
        return {"unique_words_ratio": 0.0, "avg_sentence_length": 0.0}

    return {
        "unique_words_ratio": len(set(tokens)) / len(tokens),
        "avg_sentence_length": len(tokens) / _count_sentences(text),
    }


def validate_join(audio_df: pd.DataFrame, windows_df: pd.DataFrame) -> None:
    if audio_df["window_id"].duplicated().any():
        duplicates = audio_df.loc[audio_df["window_id"].duplicated(), "window_id"].tolist()
        raise ValueError(
            f"duplicate window_id in audio_features: {duplicates[:10]} "
            f"(total {len(duplicates)})"
        )

    if windows_df["window_id"].duplicated().any():
        duplicates = windows_df.loc[
            windows_df["window_id"].duplicated(), "window_id"
        ].tolist()
        raise ValueError(
            f"duplicate window_id in windows: {duplicates[:10]} "
            f"(total {len(duplicates)})"
        )

    missing = set(audio_df["window_id"]) - set(windows_df["window_id"])
    if missing:
        missing_list = sorted(missing)
        raise ValueError(
            f"{len(missing)} audio window_id missing from windows.csv: "
            f"{missing_list[:10]}"
        )


def impute_or_fail(
    df: pd.DataFrame,
    threshold: float = NAN_THRESHOLD,
) -> tuple[pd.DataFrame, dict]:
    total_rows = len(df)
    stats: dict = {"total_rows": total_rows, "threshold": threshold, "columns": {}}

    for col in AUDIO_FEATURE_COLS:
        nan_mask = df[col].isna()
        nan_count = int(nan_mask.sum())
        nan_rate = nan_count / total_rows if total_rows else 0.0

        by_video_id = {}
        if nan_count > 0 and "video_id" in df.columns:
            grouped = df.loc[nan_mask, "video_id"].value_counts().head(5).to_dict()
            by_video_id = {str(key): int(value) for key, value in grouped.items()}

        stats["columns"][col] = {
            "nan_count": nan_count,
            "nan_rate": nan_rate,
            "filled": 0,
            "by_video_id": by_video_id,
        }

        if nan_rate >= threshold:
            raise ValueError(
                f"NaN rate {nan_rate:.4f} >= threshold {threshold} in column '{col}'. "
                f"Concentration by video_id: {by_video_id}. "
                "Manual review required."
            )

    out = df.copy()
    for col in AUDIO_FEATURE_COLS:
        nan_count = stats["columns"][col]["nan_count"]
        if nan_count > 0:
            mean = out[col].mean()
            out[col] = out[col].fillna(mean)
            stats["columns"][col]["filled"] = nan_count

    return out, stats


def _assert_overlap_columns_consistent(
    audio_df: pd.DataFrame,
    windows_df: pd.DataFrame,
) -> None:
    merged = audio_df.merge(
        windows_df[["window_id"] + _OVERLAP_COLS_EXACT + _OVERLAP_COLS_FLOAT],
        on="window_id",
        how="left",
        suffixes=("_audio", "_win"),
    )

    for col in _OVERLAP_COLS_EXACT:
        mismatch = merged[merged[f"{col}_audio"] != merged[f"{col}_win"]]
        if not mismatch.empty:
            sample = mismatch[
                ["window_id", f"{col}_audio", f"{col}_win"]
            ].head(5).to_dict("records")
            raise ValueError(
                f"inconsistent {col} between audio_features and windows "
                f"(sample: {sample})"
            )

    for col in _OVERLAP_COLS_FLOAT:
        diff = (merged[f"{col}_audio"] - merged[f"{col}_win"]).abs()
        mismatch = merged[diff > _FLOAT_TOL]
        if not mismatch.empty:
            sample = mismatch[
                ["window_id", f"{col}_audio", f"{col}_win"]
            ].head(5).to_dict("records")
            raise ValueError(
                f"inconsistent {col} between audio_features and windows "
                f"(tol={_FLOAT_TOL}; sample: {sample})"
            )


def _write_imputation_log(stats: dict, log_path: Path) -> None:
    lines = [
        "=== Feature engineering imputation log ===",
        f"total_rows: {stats['total_rows']}",
        f"threshold: {stats['threshold']}",
        "",
    ]
    for col, col_stats in stats["columns"].items():
        lines.append(
            f"[{col}] nan_count={col_stats['nan_count']} "
            f"nan_rate={col_stats['nan_rate']:.4f} filled={col_stats['filled']}"
        )
        if col_stats["by_video_id"]:
            lines.append(
                f"    concentration by video_id (top 5): {col_stats['by_video_id']}"
            )
    log_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def build_feature_matrices(
    audio_csv,
    windows_csv,
    raw_out,
    scaled_out,
    log_out,
) -> None:
    audio_csv = Path(audio_csv)
    windows_csv = Path(windows_csv)
    raw_out = Path(raw_out)
    scaled_out = Path(scaled_out)
    log_out = Path(log_out)

    audio_df = pd.read_csv(audio_csv)
    windows_df = pd.read_csv(windows_csv)

    validate_join(audio_df, windows_df)
    _assert_overlap_columns_consistent(audio_df, windows_df)

    text_cols = windows_df[["window_id", "text", "project", "tester_name"]]
    merged = audio_df.merge(text_cols, on="window_id", how="left")

    text_features = merged["text"].fillna("").apply(build_text_features)
    merged["unique_words_ratio"] = text_features.apply(
        lambda feature: feature["unique_words_ratio"]
    )
    merged["avg_sentence_length"] = text_features.apply(
        lambda feature: feature["avg_sentence_length"]
    )

    merged, stats = impute_or_fail(merged)

    raw_frame = merged[ID_COLS + FEATURE_COLS].copy()
    scaled_frame = raw_frame.copy()
    scaled_frame[FEATURE_COLS] = StandardScaler().fit_transform(raw_frame[FEATURE_COLS])

    raw_out.parent.mkdir(parents=True, exist_ok=True)
    raw_frame.to_csv(raw_out, index=False)
    scaled_frame.to_csv(scaled_out, index=False)
    _write_imputation_log(stats, log_out)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    build_feature_matrices(
        audio_csv="data/processed/audio_features.csv",
        windows_csv="data/processed/windows.csv",
        raw_out="data/processed/feature_matrix_raw.csv",
        scaled_out="data/processed/feature_matrix_scaled.csv",
        log_out="data/processed/feature_engineering_imputation.log",
    )
