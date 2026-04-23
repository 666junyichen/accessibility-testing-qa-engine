"""Postprocess Layer 3 raw classifier outputs into flat CSV-shaped DataFrames."""

from __future__ import annotations

import json
import logging

import pandas as pd

logger = logging.getLogger(__name__)

LEVEL_A_COLUMNS = [
    "window_id",
    "video_id",
    "project",
    "tester_name",
    "friction_type",
    "severity_s",
    "sentiment_e",
    "calibrator_score_l",
    "signal_alignment",
    "finding",
    "observed_signal",
    "stated_signal",
    "rationale",
    "structural_amplification_note",
]

LEVEL_B_COLUMNS = [
    "video_id",
    "project",
    "tester_name",
    "narration_quality",
    "recording_quality",
    "coaching_evidence",
]

_FINDING_FIELDS = [
    "friction_type",
    "severity_s",
    "sentiment_e",
    "calibrator_score_l",
    "signal_alignment",
    "finding",
    "observed_signal",
    "stated_signal",
    "rationale",
    "structural_amplification_note",
]


def filter_failed_rows(raw_df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    if "flag" not in raw_df:
        raise ValueError("raw_df must contain a 'flag' column")

    ok_mask = raw_df["flag"] == "ok"
    ok_df = raw_df.loc[ok_mask].copy().reset_index(drop=True)
    failed_df = raw_df.loc[~ok_mask].copy().reset_index(drop=True)

    if not failed_df.empty:
        sample_ids = failed_df.get("window_id", pd.Series(dtype=object)).head(3).tolist()
        logger.warning(
            "Skipping %s failed Layer 3 rows; first ids=%s",
            len(failed_df),
            sample_ids,
        )

    return ok_df, failed_df


def unpack_level_a(raw_df: pd.DataFrame, windows_df: pd.DataFrame) -> pd.DataFrame:
    metadata = _window_metadata(windows_df)
    rows: list[dict] = []

    for _, raw_row in raw_df.iterrows():
        window_id = str(raw_row["window_id"])
        output = _parse_output_json(raw_row["output_json"])
        findings = output.get("findings", [])

        for finding in findings:
            base = {"window_id": window_id}
            base.update(metadata.get(window_id, {}))
            for field in _FINDING_FIELDS:
                base[field] = finding.get(field)
            rows.append(base)

    return pd.DataFrame(rows, columns=LEVEL_A_COLUMNS)


def unpack_level_b(raw_df: pd.DataFrame, windows_df: pd.DataFrame) -> pd.DataFrame:
    metadata = _video_metadata(windows_df)
    rows: list[dict] = []

    for _, raw_row in raw_df.iterrows():
        video_id = str(raw_row["window_id"])
        output = _parse_output_json(raw_row["output_json"])
        row = {"video_id": video_id}
        row.update(metadata.get(video_id, {}))
        row["narration_quality"] = output.get("narration_quality")
        row["recording_quality"] = output.get("recording_quality")
        row["coaching_evidence"] = output.get("coaching_evidence")
        rows.append(row)

    return pd.DataFrame(rows, columns=LEVEL_B_COLUMNS)


def _parse_output_json(value: str) -> dict:
    if isinstance(value, dict):
        return value
    if pd.isna(value):
        return {}
    return json.loads(value)


def _window_metadata(windows_df: pd.DataFrame) -> dict[str, dict]:
    required = ["window_id", "video_id", "project", "tester_name"]
    _require_columns(windows_df, required)
    indexed = windows_df.drop_duplicates("window_id").set_index("window_id")
    return indexed[["video_id", "project", "tester_name"]].to_dict(orient="index")


def _video_metadata(windows_df: pd.DataFrame) -> dict[str, dict]:
    required = ["video_id", "project", "tester_name"]
    _require_columns(windows_df, required)
    grouped = windows_df.groupby("video_id", as_index=True).first()
    return grouped[["project", "tester_name"]].to_dict(orient="index")


def _require_columns(df: pd.DataFrame, columns: list[str]) -> None:
    missing = [column for column in columns if column not in df.columns]
    if missing:
        raise ValueError(f"DataFrame missing required columns: {missing}")
