"""Step 6.3 analysis sketch - build per_submission.csv + per_tester.csv.

Reads the canonical Step 5.1 outputs (findings + video assessments) plus the
optional auxiliary CSVs (windows, layer-1 flags) and writes the two performance
tracking tables described in `docs/performance tracking.md`.

Default paths are project-relative (resolved from this file's location), so the
script is runnable on any clone:

    python scripts/build_performance_tracking.py

All five inputs/outputs can be overridden via flags for one-off / experimental
runs:

    python scripts/build_performance_tracking.py \
        --findings-csv path/to/findings.csv \
        --assessments-csv path/to/assessments.csv \
        --windows-csv path/to/windows.csv \
        --layer1-flags-csv path/to/layer1_flags.csv \
        --out-dir path/to/out
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path


# Make `src` importable when running as `python scripts/build_performance_tracking.py`.
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.tracking.performance_model import (  # noqa: E402
    PerformanceRecord,
    TesterTrajectory,
    build_per_tester_table,
    score_submissions_from_csv,
)


# Default project-relative input/output paths. Overridable via CLI flags below.
PROCESSED_DIR = ROOT / "data" / "processed"
DEFAULT_FINDINGS_CSV = PROCESSED_DIR / "layer3_findings_filtered.csv"
DEFAULT_ASSESSMENTS_CSV = PROCESSED_DIR / "layer3_video_assessments.csv"
DEFAULT_WINDOWS_CSV = PROCESSED_DIR / "windows.csv"
DEFAULT_LAYER1_CSV = PROCESSED_DIR / "layer1_flags.csv"
DEFAULT_OUT_DIR = PROCESSED_DIR / "performance"


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
    "calibrator_aggregate_mismatch_flag",
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
    "calibrator_aggregate_mismatch_count",
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
        "calibrator_aggregate_mismatch_flag": record.calibrator_aggregate_mismatch_flag,
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
        "calibrator_aggregate_mismatch_count": trajectory.calibrator_aggregate_mismatch_count,
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


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--findings-csv",
        type=Path,
        default=DEFAULT_FINDINGS_CSV,
        help=f"Path to layer3 filtered findings CSV (default: {DEFAULT_FINDINGS_CSV.relative_to(ROOT)})",
    )
    parser.add_argument(
        "--assessments-csv",
        type=Path,
        default=DEFAULT_ASSESSMENTS_CSV,
        help=f"Path to layer3 video assessments CSV (default: {DEFAULT_ASSESSMENTS_CSV.relative_to(ROOT)})",
    )
    parser.add_argument(
        "--windows-csv",
        type=Path,
        default=DEFAULT_WINDOWS_CSV,
        help=(
            "Path to windows.csv. Used to populate total_windows; if omitted/missing "
            "the loader falls back to distinct findings windows. "
            f"(default: {DEFAULT_WINDOWS_CSV.relative_to(ROOT)})"
        ),
    )
    parser.add_argument(
        "--layer1-flags-csv",
        type=Path,
        default=DEFAULT_LAYER1_CSV,
        help=(
            "Path to layer1_flags.csv. Used to surface DURATION_ANOMALY into D3. "
            f"(default: {DEFAULT_LAYER1_CSV.relative_to(ROOT)})"
        ),
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=DEFAULT_OUT_DIR,
        help=f"Directory to write per_submission.csv + per_tester.csv (default: {DEFAULT_OUT_DIR.relative_to(ROOT)})",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)

    findings_csv: Path = args.findings_csv
    assessments_csv: Path = args.assessments_csv
    windows_csv: Path = args.windows_csv
    layer1_csv: Path = args.layer1_flags_csv
    out_dir: Path = args.out_dir

    if not findings_csv.exists():
        raise FileNotFoundError(f"findings CSV not found: {findings_csv}")
    if not assessments_csv.exists():
        raise FileNotFoundError(f"assessments CSV not found: {assessments_csv}")

    records = score_submissions_from_csv(
        findings_csv=findings_csv,
        assessments_csv=assessments_csv,
        windows_csv=windows_csv if windows_csv.exists() else None,
        layer1_flags_csv=layer1_csv if layer1_csv.exists() else None,
    )
    records.sort(key=lambda r: (r.tester_name, r.project, r.video_id))

    trajectories = build_per_tester_table(records)
    trajectories.sort(key=lambda t: t.tester_name)

    _write_csv(
        out_dir / "per_submission.csv",
        PER_SUBMISSION_COLUMNS,
        [_record_row(r) for r in records],
    )
    _write_csv(
        out_dir / "per_tester.csv",
        PER_TESTER_COLUMNS,
        [_trajectory_row(t) for t in trajectories],
    )

    print(
        f"wrote {len(records)} submission rows and "
        f"{len(trajectories)} tester rows to {out_dir}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
