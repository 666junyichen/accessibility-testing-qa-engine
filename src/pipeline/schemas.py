from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel

from src.layer3.schemas_b import VideoAssessment


class L1Summary(BaseModel):
    flag_counts: dict[str, int]
    total_flags: int
    flagged_window_ids: list[str]
    duration_anomaly: bool

    model_config = {"extra": "forbid"}


class L2Summary(BaseModel):
    coverage: float
    dominant_cluster_id: Optional[int]
    dominant_cluster_pct: Optional[float]
    cluster_distribution: dict[str, int]
    caveat: str = "tester-dominated, exploratory (Step 4.2 round-2)"

    model_config = {"extra": "forbid"}


class L3FindingsSummary(BaseModel):
    total_findings: int
    by_friction_type: dict[str, int]
    by_severity: dict[str, int]
    by_sentiment: dict[str, int]
    by_calibrator_score: dict[str, int]
    signal_alignment_distribution: dict[str, int]
    top_severity: Optional[str]
    calibrator_aggregate: Optional[str]
    top_findings: list[dict]

    model_config = {"extra": "forbid"}


class OverallQuality(BaseModel):
    quality_tier: Literal["good", "acceptable", "poor"]
    reasoning: list[str]

    model_config = {"extra": "forbid"}


class QualityReport(BaseModel):
    video_id: str
    project: str
    tester_name: str
    total_windows: int
    duration_sec: float
    l1: L1Summary
    l2: L2Summary
    l3_findings: L3FindingsSummary
    l3_assessment: VideoAssessment
    overall: OverallQuality
    coaching_recommendations: list[dict]

    model_config = {"extra": "forbid"}
