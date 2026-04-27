"""Step 6.3 analysis sketch
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

from src.tracking.performance_model import (
    PerformanceRecord,
    TesterTrajectory,
    build_per_tester_table,
    score_submissions_from_csv,
)


FINDINGS_CSV = Path("/Users/terresa/Downloads/usyd-03-2025-cs20-1-main 3/data/processed/layer3_findings_filtered.csv")
ASSESSMENTS_CSV = Path("/Users/terresa/Downloads/usyd-03-2025-cs20-1-main 3/data/processed/layer3_video_assessments.csv")
WINDOWS_CSV = Path("/Users/terresa/Downloads/usyd-03-2025-cs20-1-main 3/data/processed/windows.csv")
LAYER1_CSV = Path("/Users/terresa/Downloads/usyd-03-2025-cs20-1-main 3/data/processed/layer1_flags.csv")
OUT_DIR = Path("/Users/terresa/Downloads/usyd-03-2025-cs20-1-main 3/data/processed/performance")


PER_SUBMISSION_COLUMNS = [
    "video_id",
    "tester_name",
    "project",
    "score",
    "tier",
    "raw_score",
    "d1_narration",
    "d2_friction_surfacing",
    "d3_recording",
    "cap_applied",
    "cap_reasons",
    "total_findings",
    "total_windows",
    "top_friction_types",
    "calibrator_aggregate",
    "low_evidence",
    "cross_check_lane",
]


PER_TESTER_COLUMNS = [
    "tester_name",
    "submission_count",
    "submission_count_scored",
    "score",
    "tier",
    "direction",
    "delta_first_to_last",
    "submission_video_ids",
    "submission_scores",
    "submission_tiers",
    "persistent_friction_types",
    "sentiment_distribution",
    "projects",
    "cross_check_lanes",
    "ordering_basis",
]


def _record_row(record: PerformanceRecord) -> dict:
    return {
        "video_id": record.video_id,
        "tester_name": record.tester_name,
        "project": record.project,
        "score": record.score,
        "tier": record.tier,
        "raw_score": record.raw_score,
        "d1_narration": record.d1_narration,
        "d2_friction_surfacing": record.d2_friction_surfacing,
        "d3_recording": record.d3_recording,
        "cap_applied": "" if record.cap_applied is None else record.cap_applied,
        "cap_reasons": "; ".join(record.cap_reasons),
        "total_findings": record.total_findings,
        "total_windows": record.total_windows,
        "top_friction_types": ",".join(record.top_friction_types),
        "calibrator_aggregate": record.calibrator_aggregate or "",
        "low_evidence": record.low_evidence,
        "cross_check_lane": record.cross_check_lane,
    }


def _trajectory_row(trajectory: TesterTrajectory) -> dict:
    return {
        "tester_name": trajectory.tester_name,
        "submission_count": trajectory.submission_count,
        "submission_count_scored": trajectory.submission_count_scored,
        "score": trajectory.score,
        "tier": trajectory.tier,
        "direction": trajectory.direction or "",
        "delta_first_to_last": (
            "" if trajectory.delta_first_to_last is None
            else trajectory.delta_first_to_last
        ),
        "submission_video_ids": ",".join(trajectory.submission_video_ids),
        "submission_scores": ",".join(f"{s}" for s in trajectory.submission_scores),
        "submission_tiers": ",".join(trajectory.submission_tiers),
        "persistent_friction_types": ",".join(trajectory.persistent_friction_types),
        "sentiment_distribution": json.dumps(
            trajectory.sentiment_distribution, sort_keys=True
        ),
        "projects": ",".join(trajectory.projects),
        "cross_check_lanes": ",".join(trajectory.cross_check_lanes),
        "ordering_basis": trajectory.ordering_basis,
    }


def _write_csv(path: Path, columns: list[str], rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    records = score_submissions_from_csv(
        findings_csv=FINDINGS_CSV,
        assessments_csv=ASSESSMENTS_CSV,
        windows_csv=WINDOWS_CSV if WINDOWS_CSV.exists() else None,
        layer1_flags_csv=LAYER1_CSV if LAYER1_CSV.exists() else None,
    )
    records.sort(key=lambda r: (r.tester_name, r.project, r.video_id))

    trajectories = build_per_tester_table(records)
    trajectories.sort(key=lambda t: t.tester_name)

    _write_csv(
        OUT_DIR / "per_submission.csv",
        PER_SUBMISSION_COLUMNS,
        [_record_row(r) for r in records],
    )
    _write_csv(
        OUT_DIR / "per_tester.csv",
        PER_TESTER_COLUMNS,
        [_trajectory_row(t) for t in trajectories],
    )

    print(
        f"wrote {len(records)} submission rows and "
        f"{len(trajectories)} tester rows to {OUT_DIR}"
    )


if __name__ == "__main__":
    main()
