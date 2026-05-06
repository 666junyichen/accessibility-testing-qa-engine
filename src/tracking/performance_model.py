"""Step 6.3 Performance Tracking
"""

from __future__ import annotations

import csv
import json
import math
import warnings
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

# Composite tier rank, low → high. Used for the calibrator-aggregate mismatch
# audit signal (§4.7) where we compare composite tier against the implied tier
# from the calibrator-aggregate label.
_TIER_RANK: dict[str, int] = {
    "Foundational": 1,
    "Developing": 2,
    "Proficient": 3,
    "Leading": 4,
}

# Calibrator label → implied tier rank. L1 means "minor friction reported"
# which corresponds to a Leading-tier session experience; L5 means "blocking"
# which corresponds to Foundational. Higher L = more severe friction = lower
# implied tier. (Audit-only — see §4.7 of docs/performance tracking.md.)
_CALIBRATOR_IMPLIED_TIER_RANK: dict[str, int] = {
    "L1": 4,  # Leading
    "L2": 3,  # Proficient
    "L3": 2,  # Developing
    "L4": 1,  # Foundational
    "L5": 1,  # Foundational
}

# Threshold at which composite-vs-calibrator divergence is flagged for human
# review (audit column only — does NOT trigger any R5 coaching priority bump,
# per the W9 lock-in to keep R5/R6 decoupled).
_CALIBRATOR_MISMATCH_TIER_GAP = 2


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
    # Audit-only flag (§4.7): True when composite tier and the implied tier
    # from `calibrator_aggregate` diverge by ≥ 2 tier steps (e.g. composite =
    # Leading but calibrator aggregate implies Foundational). Surfaced as a
    # column in per_submission/per_tester CSVs for human review — does NOT feed
    # R5 priority bumps (R5/R6 stay decoupled).
    calibrator_aggregate_mismatch_flag: bool = False
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
    # Audit-only roll-up of the per-submission mismatch flag (§4.7). Counts how
    # many of this tester's submissions tripped the composite-vs-calibrator
    # divergence flag; consumed downstream as a human-review hint, not as an
    # R5 coaching trigger.
    calibrator_aggregate_mismatch_count: int = 0

    projects: list[str] = Field(default_factory=list)
    cross_check_lanes: list[CrossCheckLane] = Field(default_factory=list)

    # `(project, video_id)` ordered proxy — NOT a real chronological timestamp.
    # Surfaced in the per-tester CSV so downstream readers know this is a
    # longitudinal sketch, not a true time series. See §5.1 / §7 of
    # docs/performance tracking.md.
    ordering_basis: Literal[
        "submission_timestamp", "project_video_id_proxy"
    ] = "project_video_id_proxy"

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
    # CSV input path bypasses schemas_b validation; surface unknown labels as a
    # warning so typos in narration_quality don't get silently scored at 50.
    if narration_quality not in _NARRATION_D1:
        warnings.warn(
            f"unknown narration_quality {narration_quality!r}; falling back to "
            f"50.0. expected one of {sorted(_NARRATION_D1)}",
            stacklevel=2,
        )
    return _NARRATION_D1.get(narration_quality, 50.0)


def _d3_recording(recording_quality: str, duration_anomaly: bool) -> float:
    # CSV input path bypasses schemas_b validation; surface unknown labels as a
    # warning so typos in recording_quality don't get silently scored at 60.
    if recording_quality not in _RECORDING_D3:
        warnings.warn(
            f"unknown recording_quality {recording_quality!r}; falling back to "
            f"60.0. expected one of {sorted(_RECORDING_D3)}",
            stacklevel=2,
        )
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
    # ROUND_HALF_UP rather than Python's default banker's rounding so a .5
    # mean (e.g. {L2: 1, L3: 1} → 2.5) maps to the more-severe label (L3),
    # not the less-severe one. Banker's would silently bias toward even labels
    # (round(2.5) == 2). Locked in by W10 P2#4.
    avg = int(weighted / total + 0.5)
    avg = max(1, min(5, avg))
    return _CALIBRATOR_LABELS[avg]


def _top_friction_types(by_friction_type: dict[str, int], k: int = 3) -> list[str]:
    items = [(label, count) for label, count in by_friction_type.items() if count > 0]
    items.sort(key=lambda pair: (-pair[1], pair[0]))
    return [label for label, _ in items[:k]]


def _calibrator_mismatch_flag(
    composite_tier: Tier,
    calibrator_aggregate: Optional[str],
) -> bool:
    """Audit-only check: composite tier vs implied tier from calibrator aggregate.

    Returns True only when the two tier ranks diverge by ≥ 2 steps (e.g.
    composite=Leading but calibrator aggregate implies Foundational). Returns
    False when the calibrator aggregate is None (no findings or all blanks) —
    a missing audit signal is not a mismatch, just an unavailable cross-check.

    Per W9 P1 lock-in: this flag is audit-only. It must NOT feed R5 coaching
    priority calculations. Keeps R5/R6 decoupled.
    """
    if calibrator_aggregate is None:
        return False
    implied = _CALIBRATOR_IMPLIED_TIER_RANK.get(calibrator_aggregate)
    if implied is None:
        return False
    composite_rank = _TIER_RANK[composite_tier]
    return abs(composite_rank - implied) >= _CALIBRATOR_MISMATCH_TIER_GAP


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
    composite_tier = _tier_for(score)

    low_evidence = total_windows < 5

    calibrator_aggregate = _calibrator_aggregate(by_calibrator)
    mismatch_flag = _calibrator_mismatch_flag(composite_tier, calibrator_aggregate)

    return PerformanceRecord(
        video_id=video_id,
        tester_name=tester_name,
        project=project,
        score=score,
        tier=composite_tier,
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
        calibrator_aggregate=calibrator_aggregate,
        calibrator_aggregate_mismatch_flag=mismatch_flag,
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

    mismatch_count = sum(
        1 for r in ordered if r.calibrator_aggregate_mismatch_flag
    )

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
        calibrator_aggregate_mismatch_count=mismatch_count,
        projects=projects,
        cross_check_lanes=lanes,
        ordering_basis="project_video_id_proxy",
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
