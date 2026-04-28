from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.pipeline.fusion import fuse_video


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run fusion pipeline and generate QualityReport JSON files."
    )
    parser.add_argument(
        "--video",
        type=str,
        help="Run pipeline for a single video_id.",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Run pipeline for all video_ids found in the processed CSV files.",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="data/processed/reports",
        help="Directory to write QualityReport JSON outputs.",
    )
    parser.add_argument(
        "--processed-dir",
        type=str,
        default="data/processed",
        help="Directory containing processed CSV inputs.",
    )
    return parser.parse_args()


def load_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        logging.warning("Missing input file: %s", path)
        return pd.DataFrame()
    return pd.read_csv(path)


def load_inputs(processed_dir: Path) -> dict[str, pd.DataFrame]:
    return {
        "windows": load_csv(processed_dir / "windows.csv"),
        "l1_flags": load_csv(processed_dir / "layer1_flags.csv"),
        "l2_assignments": load_csv(processed_dir / "layer2_cluster_assignments.csv"),
        "l3_findings": load_csv(processed_dir / "layer3_findings_filtered.csv"),
        "l3_assessments": load_csv(processed_dir / "layer3_video_assessments.csv"),
    }


def normalize_video_key(name: str) -> str:
    text = str(name).strip()
    text = Path(text).name

    if text.lower().endswith(".mp4"):
        text = text[:-4]

    if text.endswith("_video"):
        text = text[:-6]

    return text


def collect_video_ids(data: dict[str, pd.DataFrame]) -> list[str]:
    video_ids: set[str] = set()

    for df in data.values():
        if not df.empty and "video_id" in df.columns:
            ids = df["video_id"].dropna().astype(str).tolist()
            video_ids.update(ids)

    return sorted(video_ids)


def filter_by_video(df: pd.DataFrame, video_id: str) -> pd.DataFrame:
    if df.empty or "video_id" not in df.columns:
        return pd.DataFrame()
    return df[df["video_id"].astype(str) == str(video_id)].copy()


def get_video_filename_from_windows(windows: pd.DataFrame, video_id: str) -> str | None:
    if windows.empty:
        return None

    if "video_id" not in windows.columns or "video_filename" not in windows.columns:
        return None

    matched = windows[windows["video_id"].astype(str) == str(video_id)]
    if matched.empty:
        return None

    return str(matched.iloc[0]["video_filename"])


def filter_l1_flags(
    l1_df: pd.DataFrame,
    windows_df: pd.DataFrame,
    video_id: str,
) -> pd.DataFrame:
    """
    Layer 1 flags may not contain video_id.
    Current layer1_flags.csv contains video_filename instead, so we map
    video_id -> video_filename using windows.csv, then match by normalized filename.
    """
    if l1_df.empty:
        return pd.DataFrame()

    if "video_id" in l1_df.columns:
        matched = l1_df[l1_df["video_id"].astype(str) == str(video_id)].copy()
        if not matched.empty:
            return matched

    if "video_filename" not in l1_df.columns:
        return pd.DataFrame()

    video_filename = get_video_filename_from_windows(windows_df, video_id)
    if video_filename is None:
        return pd.DataFrame()

    target_key = normalize_video_key(video_filename)

    working = l1_df.copy()
    working["video_key"] = working["video_filename"].astype(str).apply(normalize_video_key)

    matched = working[working["video_key"] == target_key].copy()

    if "video_key" in matched.columns:
        matched = matched.drop(columns=["video_key"])

    return matched


def get_assessment_row(df: pd.DataFrame, video_id: str) -> dict:
    if df.empty or "video_id" not in df.columns:
        raise ValueError(f"No layer3 assessment table or missing video_id column for {video_id}")

    matched = df[df["video_id"].astype(str) == str(video_id)].copy()
    if matched.empty:
        raise ValueError(f"No l3 assessment found for video_id={video_id}")

    row = matched.iloc[0].to_dict()

    clean_row = {
        str(k): (None if pd.isna(v) else v)
        for k, v in row.items()
    }

    for extra_key in ["video_id", "project", "tester_name"]:
        clean_row.pop(extra_key, None)

    return clean_row


def save_report(report, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if hasattr(report, "model_dump"):
        payload = report.model_dump(mode="json")
    else:
        payload = json.loads(report.json())

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)


def build_summary_row(video_id: str, ok: bool, output_dir: Path) -> dict:
    if not ok:
        return {
            "video_id": video_id,
            "tester": "",
            "project": "",
            "windows": 0,
            "duration_s": 0,
            "l1_total": 0,
            "l1_duration_anomaly": False,
            "l2_coverage": 0.0,
            "l3_findings": 0,
            "top_severity": "",
            "narration": "",
            "recording": "",
            "tier": "",
            "reason": "",
            "coach_recs": 0,
        }

    report_path = output_dir / f"{video_id}.json"
    payload = json.loads(report_path.read_text(encoding="utf-8"))

    l1 = payload.get("l1", {})
    l2 = payload.get("l2", {})
    l3_findings = payload.get("l3_findings", {})
    l3_assessment = payload.get("l3_assessment", {})
    overall = payload.get("overall", {})

    reasoning = overall.get("reasoning", "")
    if isinstance(reasoning, list):
        reasoning = " | ".join(str(x) for x in reasoning)

    return {
        "video_id": payload.get("video_id", video_id),
        "tester": payload.get("tester_name", ""),
        "project": payload.get("project", ""),
        "windows": payload.get("total_windows", 0),
        "duration_s": int(round(payload.get("duration_sec", 0))),
        "l1_total": l1.get("total_flags", 0),
        "l1_duration_anomaly": l1.get("duration_anomaly", False),
        "l2_coverage": l2.get("coverage", 0.0),
        "l3_findings": l3_findings.get("total_findings", 0),
        "top_severity": l3_findings.get("top_severity", ""),
        "narration": l3_assessment.get("narration_quality", ""),
        "recording": l3_assessment.get("recording_quality", ""),
        "tier": overall.get("quality_tier", ""),
        "reason": reasoning,
        "coach_recs": len(payload.get("coaching_recommendations", [])),
    }


def run_one_video(video_id: str, data: dict[str, pd.DataFrame], output_dir: Path) -> bool:
    windows = filter_by_video(data["windows"], video_id)
    l1_flags = filter_l1_flags(
        data["l1_flags"],
        data["windows"],
        video_id,
    )
    l2_assignments = filter_by_video(data["l2_assignments"], video_id)
    l3_findings = filter_by_video(data["l3_findings"], video_id)

    if windows.empty:
        logging.warning("Skipping %s: no windows found.", video_id)
        return False

    try:
        l3_assessment = get_assessment_row(data["l3_assessments"], video_id)
    except Exception as e:
        logging.warning("Skipping %s: %s", video_id, e)
        return False

    try:
        report = fuse_video(
            video_id=video_id,
            windows=windows,
            l1_flags=l1_flags,
            l2_assignments=l2_assignments,
            l3_findings=l3_findings,
            l3_assessment=l3_assessment,
            coaching_engine=None,
        )
        save_report(report, output_dir / f"{video_id}.json")
        logging.info(
            "Generated report for %s | windows=%d l1_flags=%d l2_rows=%d l3_findings=%d",
            video_id,
            len(windows),
            len(l1_flags),
            len(l2_assignments),
            len(l3_findings),
        )
        return True
    except Exception as e:
        logging.exception("Failed to generate report for %s: %s", video_id, e)
        return False


def main() -> None:
    args = parse_args()

    if bool(args.video) == bool(args.all):
        raise SystemExit("Please provide exactly one of --video <id> or --all")

    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s: %(message)s",
    )

    processed_dir = Path(args.processed_dir)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    data = load_inputs(processed_dir)

    if args.video:
        video_ids = [args.video]
    else:
        video_ids = collect_video_ids(data)

    if not video_ids:
        raise SystemExit("No video_ids found in processed inputs.")

    success_count = 0
    fail_count = 0
    summary_rows = []

    for video_id in video_ids:
        ok = run_one_video(video_id, data, output_dir)

        if ok:
            success_count += 1
        else:
            fail_count += 1

        summary_rows.append(build_summary_row(video_id, ok, output_dir))

    logging.info("Done. success=%d failed=%d", success_count, fail_count)

    summary_df = pd.DataFrame(summary_rows)
    summary_df.to_csv(output_dir / "_summary.csv", index=False)
    logging.info("Summary CSV written to %s", output_dir / "_summary.csv")


if __name__ == "__main__":
    main()
