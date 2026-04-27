"""Step 6.3 Performance Tracking
"""

from __future__ import annotations

import csv
import json
import math
from collections import Counter, defaultdict
from pathlib import Path
from typing import Iterable, Literal, Optional

from pydantic import BaseModel, Field


Tier = Literal["Foundational", "Developing", "Proficient", "Leading"]
Direction = Literal["improving", "stable", "declining"]
CrossCheckLane = Literal["with_overrides", "raw_only", "dev_only"]

_TIER_BOUNDARIES: tuple[tuple[float, Tier], ...] = (
    (85.0, "Leading"),
    (70.0, "Proficient"),
    (55.0, "Developing"),
    (0.0, "Foundational"),
)

_NARRATION_D1 = {"rich": 90.0, "adequate": 75.0, "sparse": 55.0, "none": 25.0}
_RECORDING_D3 = {"good": 90.0, "acceptable": 70.0, "poor": 40.0}


_MID_HIGH_SEVERITY = {"S1", "S2", "S3", "S4"}


_CALIBRATOR_RANK = {"L1": 1, "L2": 2, "L3": 3, "L4": 4, "L5": 5}
_CALIBRATOR_LABELS = {v: k for k, v in _CALIBRATOR_RANK.items()}


_PROJECT_LANE: dict[str, CrossCheckLane] = {

    "suncorp-insurance": "with_overrides",
    "department-of-premier-and-cabinet-wa": "with_overrides",
    "web-health-information-bupa": "with_overrides",
    "the-university-of-queensland": "raw_only",
}


def _lane_for(project: str) -> CrossCheckLane:
    return _PROJECT_LANE.get(project, "dev_only")


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------


class PerformanceRecord(BaseModel):
    """Per-submission performance score. One per video."""

    video_id: str
    tester_name: str
    project: str

    score: float = Field(..., ge=0.0, le=100.0)
    tier: Tier

    d1_narration: float = Field(..., ge=0.0, le=100.0)
    d2_friction_surfacing: float = Field(..., ge=0.0, le=100.0)
    d3_recording: float = Field(..., ge=0.0, le=100.0)
    raw_score: float = Field(..., ge=0.0, le=100.0)

    # Severity cap audit trail (§4.4) — empty means no cap applied.
    cap_applied: Optional[float] = None
    cap_reasons: list[str] = Field(default_factory=list)

    # Pass-through facets used by the per-tester layer.
    total_findings: int = 0
    total_windows: int = 0
    by_friction_type: dict[str, int] = Field(default_factory=dict)
    by_severity: dict[str, int] = Field(default_factory=dict)
    by_sentiment: dict[str, int] = Field(default_factory=dict)
    top_friction_types: list[str] = Field(default_factory=list)


    calibrator_aggregate: Optional[str] = None
    low_evidence: bool = False

    cross_check_lane: CrossCheckLane = "dev_only"

    model_config = {"extra": "forbid"}


class TesterTrajectory(BaseModel):
    """Per-tester longitudinal summary across all their submissions."""

    tester_name: str
    submission_count: int
    submission_count_scored: int  # excludes low_evidence

    score: float = Field(..., ge=0.0, le=100.0)
    tier: Tier

    direction: Optional[Direction] = None
    delta_first_to_last: Optional[float] = None

    submission_video_ids: list[str] = Field(default_factory=list)
    submission_scores: list[float] = Field(default_factory=list)
    submission_tiers: list[Tier] = Field(default_factory=list)

    persistent_friction_types: list[str] = Field(default_factory=list)
    sentiment_distribution: dict[str, int] = Field(default_factory=dict)

    projects: list[str] = Field(default_factory=list)
    cross_check_lanes: list[CrossCheckLane] = Field(default_factory=list)

    ordering_basis: Literal[
        "submission_timestamp", "filename_stable_sort"
    ] = "filename_stable_sort"

    model_config = {"extra": "forbid"}


# ---------------------------------------------------------------------------
# Per-submission scoring
# ---------------------------------------------------------------------------


def _clamp(value: float, lo: float = 0.0, hi: float = 100.0) -> float:
    return max(lo, min(hi, value))


def _tier_for(score: float) -> Tier:
    for threshold, label in _TIER_BOUNDARIES:
        if score >= threshold:
            return label
    return "Foundational"


def _d1_narration(narration_quality: str) -> float:
    return _NARRATION_D1.get(narration_quality, 50.0)


def _d3_recording(recording_quality: str, duration_anomaly: bool) -> float:
    base = _RECORDING_D3.get(recording_quality, 60.0)
    if duration_anomaly:
        base = min(base, 60.0)
    return base


def _d2_friction_surfacing(
    by_severity: dict[str, int],
    signal_alignment: dict[str, int],
    total_findings: int,
    total_windows: int,
    narration_quality: str,
) -> float:
    if total_findings == 0:

        if narration_quality in {"rich", "adequate"}:
            return 50.0

        return 40.0

    density = total_findings / max(total_windows, 1)
    aligned = signal_alignment.get("aligned", 0) / max(total_findings, 1)
    mid_high = sum(by_severity.get(s, 0) for s in _MID_HIGH_SEVERITY) / max(
        total_findings, 1
    )

    score = (
        60.0
        + 20.0 * _clamp(density / 0.6, 0.0, 1.0)
        + 10.0 * aligned
        + 10.0 * mid_high
    )
    return _clamp(score)


def _apply_caps(
    raw: float,
    by_severity: dict[str, int],
    narration_quality: str,
    recording_quality: str,
    total_findings: int,
) -> tuple[float, list[str]]:
    caps: list[tuple[float, str]] = []

    if by_severity.get("S1", 0) >= 1:
        caps.append((55.0, "S1 project-level blocker present"))
    if by_severity.get("S2", 0) >= 2:
        caps.append((65.0, ">=2 S2 task-blockers"))
    if narration_quality == "none" and total_findings == 0:
        caps.append((40.0, "no analyzable signal (no narration, no findings)"))
    if recording_quality == "poor":
        caps.append((70.0, "recording_quality == poor"))

    if not caps:
        return raw, []

    binding_cap, _ = min(caps, key=lambda pair: pair[0])
    if binding_cap >= raw:

        return raw, []
    reasons = [reason for cap_value, reason in caps if cap_value < raw]
    return binding_cap, reasons


def _calibrator_aggregate(by_calibrator_score: dict[str, int]) -> Optional[str]:
    if not by_calibrator_score:
        return None
    weighted = 0.0
    total = 0
    for label, count in by_calibrator_score.items():
        rank = _CALIBRATOR_RANK.get(label)
        if rank is None or count <= 0:
            continue
        weighted += rank * count
        total += count
    if total == 0:
        return None
    avg = round(weighted / total)
    avg = max(1, min(5, int(avg)))
    return _CALIBRATOR_LABELS[avg]


def _top_friction_types(by_friction_type: dict[str, int], k: int = 3) -> list[str]:
    items = [(label, count) for label, count in by_friction_type.items() if count > 0]
    items.sort(key=lambda pair: (-pair[1], pair[0]))
    return [label for label, _ in items[:k]]


def score_submission(report: dict) -> PerformanceRecord:

    video_id = report["video_id"]
    project = report.get("project", "")
    tester_name = report.get("tester_name", "")

    l3 = report.get("l3_findings", {}) or {}
    by_friction_type = dict(l3.get("by_friction_type", {}) or {})
    by_severity = dict(l3.get("by_severity", {}) or {})
    by_sentiment = dict(l3.get("by_sentiment", {}) or {})
    by_calibrator = dict(l3.get("by_calibrator_score", {}) or {})
    signal_alignment = dict(l3.get("signal_alignment_distribution", {}) or {})
    total_findings = int(l3.get("total_findings", 0) or 0)

    assessment = report.get("l3_assessment", {}) or {}
    narration_quality = assessment.get("narration_quality", "adequate") or "adequate"
    recording_quality = assessment.get("recording_quality", "acceptable") or "acceptable"

    l1 = report.get("l1", {}) or {}
    duration_anomaly = bool(l1.get("duration_anomaly", False))

    total_windows = int(report.get("total_windows", 0) or 0)

    d1 = _d1_narration(narration_quality)
    d2 = _d2_friction_surfacing(
        by_severity=by_severity,
        signal_alignment=signal_alignment,
        total_findings=total_findings,
        total_windows=total_windows,
        narration_quality=narration_quality,
    )
    d3 = _d3_recording(recording_quality, duration_anomaly)

    raw = 0.50 * d1 + 0.35 * d2 + 0.15 * d3
    capped, reasons = _apply_caps(
        raw=raw,
        by_severity=by_severity,
        narration_quality=narration_quality,
        recording_quality=recording_quality,
        total_findings=total_findings,
    )

    score = round(capped, 1)

    low_evidence = total_windows < 5

    return PerformanceRecord(
        video_id=video_id,
        tester_name=tester_name,
        project=project,
        score=score,
        tier=_tier_for(score),
        d1_narration=round(d1, 1),
        d2_friction_surfacing=round(d2, 1),
        d3_recording=round(d3, 1),
        raw_score=round(raw, 1),
        cap_applied=round(capped, 1) if reasons else None,
        cap_reasons=reasons,
        total_findings=total_findings,
        total_windows=total_windows,
        by_friction_type=by_friction_type,
        by_severity=by_severity,
        by_sentiment=by_sentiment,
        top_friction_types=_top_friction_types(by_friction_type),
        calibrator_aggregate=_calibrator_aggregate(by_calibrator),
        low_evidence=low_evidence,
        cross_check_lane=_lane_for(project),
    )


# ---------------------------------------------------------------------------
# Per-tester aggregation
# ---------------------------------------------------------------------------


def _trajectory_direction(delta: float) -> Direction:
    if delta > 5.0:
        return "improving"
    if delta < -5.0:
        return "declining"
    return "stable"


def _persistent_friction(records: list[PerformanceRecord]) -> list[str]:
    counter: Counter[str] = Counter()
    for record in records:
        for label in record.top_friction_types:
            counter[label] += 1
    return sorted(
        [label for label, count in counter.items() if count >= 2],
        key=lambda label: (-counter[label], label),
    )


def aggregate_tester(records: list[PerformanceRecord]) -> TesterTrajectory:


    if not records:
        raise ValueError("aggregate_tester() requires at least one record")
    tester_name = records[0].tester_name
    if any(r.tester_name != tester_name for r in records):
        raise ValueError("aggregate_tester() requires single-tester input")

    ordered = sorted(records, key=lambda r: (r.project, r.video_id))
    scored = [r for r in ordered if not r.low_evidence]

    submission_video_ids = [r.video_id for r in ordered]
    submission_scores = [r.score for r in ordered]
    submission_tiers = [r.tier for r in ordered]
    projects = [r.project for r in ordered]
    lanes = [r.cross_check_lane for r in ordered]

    if scored:
        mean_score = round(sum(r.score for r in scored) / len(scored), 1)
    else:

        mean_score = round(sum(r.score for r in ordered) / len(ordered), 1)

    if len(scored) >= 2:
        delta = round(scored[-1].score - scored[0].score, 1)
        direction: Optional[Direction] = _trajectory_direction(delta)
    else:
        delta = None
        direction = None

    sentiment_total: Counter[str] = Counter()
    for r in ordered:
        for label, count in r.by_sentiment.items():
            sentiment_total[label] += count

    return TesterTrajectory(
        tester_name=tester_name,
        submission_count=len(ordered),
        submission_count_scored=len(scored),
        score=mean_score,
        tier=_tier_for(mean_score),
        direction=direction,
        delta_first_to_last=delta,
        submission_video_ids=submission_video_ids,
        submission_scores=submission_scores,
        submission_tiers=submission_tiers,
        persistent_friction_types=_persistent_friction(ordered),
        sentiment_distribution=dict(sentiment_total),
        projects=projects,
        cross_check_lanes=lanes,
        ordering_basis="filename_stable_sort",
    )


def build_per_tester_table(
    records: Iterable[PerformanceRecord],
) -> list[TesterTrajectory]:

    by_tester: dict[str, list[PerformanceRecord]] = {}
    for record in records:
        by_tester.setdefault(record.tester_name, []).append(record)
    return [aggregate_tester(rows) for rows in by_tester.values()]


# ---------------------------------------------------------------------------
# Convenience loader
# ---------------------------------------------------------------------------


def load_reports(reports_dir: str | Path) -> list[dict]:
    path = Path(reports_dir)
    if not path.is_dir():
        raise FileNotFoundError(f"reports_dir not found: {path}")

    out: list[dict] = []
    for entry in sorted(path.iterdir()):
        if entry.name.startswith("_"):
            continue
        if entry.suffix.lower() != ".json":
            continue
        with entry.open(encoding="utf-8") as handle:
            out.append(json.load(handle))
    return out


# ---------------------------------------------------------------------------
# CSV input path
# ---------------------------------------------------------------------------


def _read_csv(path: str | Path) -> list[dict]:
    with Path(path).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def _video_assessment_index(rows: list[dict]) -> dict[str, dict]:
    by_video: dict[str, dict] = {}
    for row in rows:
        video_id = row["video_id"]
        by_video[video_id] = {
            "narration_quality": (row.get("narration_quality") or "adequate").strip(),
            "recording_quality": (row.get("recording_quality") or "acceptable").strip(),
            "coaching_evidence": (row.get("coaching_evidence") or "none").strip(),
            "project": row.get("project", ""),
            "tester_name": row.get("tester_name", ""),
        }
    return by_video


def _findings_index(rows: list[dict]) -> dict[str, list[dict]]:
    by_video: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        by_video[row["video_id"]].append(row)
    return dict(by_video)


def _windows_per_video(rows: list[dict]) -> dict[str, int]:
    """Count rows in windows.csv per video_id (one row = one 60s window)."""
    counts: Counter[str] = Counter()
    for row in rows:
        video_id = row.get("video_id")
        if video_id:
            counts[video_id] += 1
    return dict(counts)


def _layer1_anomaly_index(rows: list[dict]) -> dict[str, bool]:

    out: dict[str, bool] = {}
    for row in rows:
        if row.get("flag") == "DURATION_ANOMALY":
            video_id = row.get("video_id") or row.get("video_filename", "").rsplit(".", 1)[0]
            if video_id:
                out[video_id] = True
    return out


def _build_report_dict(
    video_id: str,
    findings: list[dict],
    assessment: dict,
    total_windows: int,
    duration_anomaly: bool,
) -> dict:

    by_friction_type: Counter[str] = Counter()
    by_severity: Counter[str] = Counter()
    by_sentiment: Counter[str] = Counter()
    by_calibrator: Counter[str] = Counter()
    alignment: Counter[str] = Counter()

    for row in findings:
        if row.get("friction_type"):
            by_friction_type[row["friction_type"]] += 1
        if row.get("severity_s"):
            by_severity[row["severity_s"]] += 1
        sentiment = row.get("sentiment_e")
        if sentiment:
            by_sentiment[sentiment] += 1
        if row.get("calibrator_score_l"):
            by_calibrator[row["calibrator_score_l"]] += 1
        if row.get("signal_alignment"):
            alignment[row["signal_alignment"]] += 1

    return {
        "video_id": video_id,
        "project": assessment.get("project", ""),
        "tester_name": assessment.get("tester_name", ""),
        "total_windows": total_windows,
        "duration_sec": 0.0,
        "l1": {"duration_anomaly": duration_anomaly, "flag_counts": {}, "total_flags": 0, "flagged_window_ids": []},
        "l2": {},
        "l3_findings": {
            "total_findings": len(findings),
            "by_friction_type": dict(by_friction_type),
            "by_severity": dict(by_severity),
            "by_sentiment": dict(by_sentiment),
            "by_calibrator_score": dict(by_calibrator),
            "signal_alignment_distribution": dict(alignment),
        },
        "l3_assessment": {
            "narration_quality": assessment["narration_quality"],
            "recording_quality": assessment["recording_quality"],
            "coaching_evidence": assessment["coaching_evidence"],
        },
        "overall": {},
    }


def score_submissions_from_csv(
    findings_csv: str | Path,
    assessments_csv: str | Path,
    windows_csv: str | Path | None = None,
    layer1_flags_csv: str | Path | None = None,
) -> list[PerformanceRecord]:

    findings_by_video = _findings_index(_read_csv(findings_csv))
    assessments_by_video = _video_assessment_index(_read_csv(assessments_csv))

    if windows_csv is not None:
        windows_per_video = _windows_per_video(_read_csv(windows_csv))
    else:
        windows_per_video = {}

    if layer1_flags_csv is not None:
        anomaly_by_video = _layer1_anomaly_index(_read_csv(layer1_flags_csv))
    else:
        anomaly_by_video = {}

    records: list[PerformanceRecord] = []
    for video_id, assessment in assessments_by_video.items():
        findings = findings_by_video.get(video_id, [])

        if video_id in windows_per_video:
            total_windows = windows_per_video[video_id]
        else:

            distinct = {row.get("window_id") for row in findings if row.get("window_id")}
            total_windows = max(len(distinct), 1)

        report = _build_report_dict(
            video_id=video_id,
            findings=findings,
            assessment=assessment,
            total_windows=total_windows,
            duration_anomaly=anomaly_by_video.get(video_id, False),
        )
        records.append(score_submission(report))

    return records


__all__ = [
    "PerformanceRecord",
    "TesterTrajectory",
    "Tier",
    "Direction",
    "CrossCheckLane",
    "score_submission",
    "score_submissions_from_csv",
    "aggregate_tester",
    "build_per_tester_table",
    "load_reports",
]
