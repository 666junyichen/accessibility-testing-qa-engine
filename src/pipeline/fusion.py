"""Step 6.1 MVP fusion utilities.

The module combines per-video summaries from L1/L2/L3 and wraps the R5
coaching engine output into a single QualityReport. It intentionally performs
no file I/O and leaves caller-side filtering/joining to the orchestrator.
"""

from __future__ import annotations

from typing import Any

import pandas as pd

from src.coaching.recommendation_engine import RecommendationEngine
from src.layer3.schemas_b import VideoAssessment
from src.pipeline.schemas import (
    L1Summary,
    L2Summary,
    L3FindingsSummary,
    OverallQuality,
    QualityReport,
)

_SEVERITY_RANK = {"S1": 1, "S2": 2, "S3": 3, "S4": 4, "S5": 5, "S6": 6}
_CALIBRATOR_RANK = {"L1": 1, "L2": 2, "L3": 3, "L4": 4, "L5": 5}


def fuse_video(
    video_id: str,
    windows: pd.DataFrame,
    l1_flags: pd.DataFrame,
    l2_assignments: pd.DataFrame,
    l3_findings: pd.DataFrame,
    l3_assessment: dict,
    coaching_engine=None,
) -> QualityReport:
    assessment = VideoAssessment.model_validate(_to_plain_dict(l3_assessment))
    l1_summary = _summarize_l1(l1_flags)
    l2_summary = _summarize_l2(windows, l2_assignments)
    l3_summary = _summarize_l3_findings(l3_findings)
    overall = _compute_overall_quality(
        l3_summary,
        assessment,
        duration_anomaly=l1_summary.duration_anomaly,
    )

    engine = coaching_engine or RecommendationEngine()
    recommendations = [item.to_dict() for item in engine.generate(assessment)]

    return QualityReport(
        video_id=video_id,
        project=_first_value(windows, "project"),
        tester_name=_first_value(windows, "tester_name"),
        total_windows=int(len(windows)),
        duration_sec=float(windows["duration"].sum()) if "duration" in windows else 0.0,
        l1=l1_summary,
        l2=l2_summary,
        l3_findings=l3_summary,
        l3_assessment=assessment,
        overall=overall,
        coaching_recommendations=recommendations,
    )


def _summarize_l1(l1_flags: pd.DataFrame) -> L1Summary:
    if l1_flags.empty or "flag" not in l1_flags:
        return L1Summary(
            flag_counts={},
            total_flags=0,
            flagged_window_ids=[],
            duration_anomaly=False,
        )

    flag_counts = _value_counts(l1_flags["flag"])
    flagged_window_ids: list[str] = []
    if "window_id" in l1_flags:
        ids = l1_flags["window_id"].dropna()
        flagged_window_ids = sorted({str(value) for value in ids if str(value)})

    return L1Summary(
        flag_counts=flag_counts,
        total_flags=int(len(l1_flags)),
        flagged_window_ids=flagged_window_ids,
        duration_anomaly=bool((l1_flags["flag"] == "DURATION_ANOMALY").any()),
    )


def _summarize_l2(windows: pd.DataFrame, l2_assignments: pd.DataFrame) -> L2Summary:
    if (
        windows.empty
        or l2_assignments.empty
        or "primary_cluster_id" not in l2_assignments
    ):
        return L2Summary(
            coverage=0.0,
            dominant_cluster_id=None,
            dominant_cluster_pct=None,
            cluster_distribution={},
        )

    labels = l2_assignments["primary_cluster_id"].dropna()
    if labels.empty:
        return L2Summary(
            coverage=0.0,
            dominant_cluster_id=None,
            dominant_cluster_pct=None,
            cluster_distribution={},
        )

    distribution = _value_counts(labels)
    dominant_key, dominant_count = max(
        distribution.items(), key=lambda item: (item[1], -int(item[0]))
    )
    labelled_windows = (
        l2_assignments["window_id"].dropna().nunique()
        if "window_id" in l2_assignments
        else len(labels)
    )

    return L2Summary(
        coverage=float(labelled_windows / len(windows)),
        dominant_cluster_id=int(dominant_key),
        dominant_cluster_pct=float(dominant_count / sum(distribution.values())),
        cluster_distribution=distribution,
    )


def _summarize_l3_findings(l3_findings: pd.DataFrame) -> L3FindingsSummary:
    if l3_findings.empty:
        return L3FindingsSummary(
            total_findings=0,
            by_friction_type={},
            by_severity={},
            by_sentiment={},
            by_calibrator_score={},
            signal_alignment_distribution={},
            top_severity=None,
            calibrator_aggregate=None,
            top_findings=[],
        )

    top_severity = _min_rank_value(l3_findings, "severity_s", _SEVERITY_RANK)
    calibrator_aggregate = _max_rank_value(
        l3_findings, "calibrator_score_l", _CALIBRATOR_RANK
    )

    sorted_findings = l3_findings.copy()
    sorted_findings["_severity_rank"] = sorted_findings["severity_s"].map(_SEVERITY_RANK)
    sorted_findings["_calibrator_rank"] = sorted_findings["calibrator_score_l"].map(
        _CALIBRATOR_RANK
    )
    sorted_findings = sorted_findings.sort_values(
        by=["_severity_rank", "_calibrator_rank"],
        ascending=[True, False],
        na_position="last",
    )
    top_findings = sorted_findings.drop(
        columns=["_severity_rank", "_calibrator_rank"]
    ).head(5)

    return L3FindingsSummary(
        total_findings=int(len(l3_findings)),
        by_friction_type=_counts_for_column(l3_findings, "friction_type"),
        by_severity=_counts_for_column(l3_findings, "severity_s"),
        by_sentiment=_counts_for_column(l3_findings, "sentiment_e", none_key="none"),
        by_calibrator_score=_counts_for_column(l3_findings, "calibrator_score_l"),
        signal_alignment_distribution=_counts_for_column(
            l3_findings, "signal_alignment"
        ),
        top_severity=top_severity,
        calibrator_aggregate=calibrator_aggregate,
        top_findings=_records(top_findings),
    )


def _compute_overall_quality(
    l3_findings: L3FindingsSummary,
    assessment: VideoAssessment,
    duration_anomaly: bool = False,
) -> OverallQuality:
    if assessment.recording_quality == "poor":
        return OverallQuality(quality_tier="poor", reasoning=["recording unusable"])

    if {"S1", "S2"} & set(l3_findings.by_severity):
        return OverallQuality(
            quality_tier="poor",
            reasoning=["task-blocking friction: S1/S2 present"],
        )

    if l3_findings.total_findings >= 5:
        return OverallQuality(
            quality_tier="acceptable",
            reasoning=["multiple medium-severity findings"],
        )

    if assessment.coaching_evidence == "explicit":
        return OverallQuality(
            quality_tier="acceptable",
            reasoning=["explicit moderator coaching reduces session validity"],
        )

    if assessment.narration_quality in {"none", "sparse"}:
        return OverallQuality(
            quality_tier="acceptable",
            reasoning=["low narration coverage"],
        )

    if assessment.recording_quality == "acceptable" and l3_findings.total_findings > 0:
        return OverallQuality(
            quality_tier="acceptable",
            reasoning=["acceptable recording with some findings"],
        )

    overall = OverallQuality(
        quality_tier="good",
        reasoning=["no major quality concerns detected"],
    )
    if duration_anomaly:
        return OverallQuality(
            quality_tier="acceptable",
            reasoning=overall.reasoning + ["duration anomaly caps session confidence"],
        )
    return overall


def _counts_for_column(
    df: pd.DataFrame,
    column: str,
    none_key: str | None = None,
) -> dict[str, int]:
    if column not in df:
        return {}
    values = df[column]
    if none_key is not None:
        values = values.fillna(none_key)
    else:
        values = values.dropna()
    return _value_counts(values)


def _value_counts(values: pd.Series) -> dict[str, int]:
    counts = values.value_counts(dropna=False).sort_index()
    return {str(key): int(value) for key, value in counts.items()}


def _min_rank_value(
    df: pd.DataFrame,
    column: str,
    rank: dict[str, int],
) -> str | None:
    if column not in df:
        return None
    values = [value for value in df[column].dropna().astype(str) if value in rank]
    if not values:
        return None
    return min(values, key=lambda value: rank[value])


def _max_rank_value(
    df: pd.DataFrame,
    column: str,
    rank: dict[str, int],
) -> str | None:
    if column not in df:
        return None
    values = [value for value in df[column].dropna().astype(str) if value in rank]
    if not values:
        return None
    return max(values, key=lambda value: rank[value])


def _records(df: pd.DataFrame) -> list[dict]:
    records = df.where(pd.notna(df), None).to_dict(orient="records")
    return [{str(key): value for key, value in record.items()} for record in records]


def _first_value(df: pd.DataFrame, column: str) -> str:
    if df.empty or column not in df:
        return ""
    value = df[column].dropna().iloc[0]
    return str(value)


def _to_plain_dict(value: Any) -> dict:
    if isinstance(value, pd.Series):
        return value.to_dict()
    return dict(value)
