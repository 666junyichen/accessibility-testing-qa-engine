"""
Step 8.2 Ablation Study (R4)

Re-runs fuse_video() across all 57 development videos under 4 configurations:
  - Full   : all layers as-is (baseline)
  - No-L1  : l1_flags input set to empty
  - No-L2  : l2_assignments input set to empty
  - No-L3  : l3_findings empty + neutral default l3_assessment

Outputs:
  - data/processed/ablation_summary.csv (per-video x per-config tier + counts)
  - prints comparison table to stdout
"""

import json
import sys
from collections import Counter
from pathlib import Path

import pandas as pd

# Make src importable
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.run_pipeline import (  # noqa: E402
    filter_by_video,
    filter_l1_flags,
    get_assessment_row,
    load_inputs,
    normalize_video_key,
)
from src.pipeline.fusion import fuse_video  # noqa: E402

PROCESSED_DIR = ROOT / "data" / "processed"
OUTPUT_CSV = PROCESSED_DIR / "ablation_summary.csv"

# Default neutral assessment used when L3 is ablated (No-L3).
# Reflects "system has no LLM signal at all" — neutral inputs,
# so fusion's tier logic falls through to its default branch.
NEUTRAL_ASSESSMENT = {
    "narration_quality": "rich",
    "recording_quality": "good",
    "coaching_evidence": "none",
}

CONFIGS = ["Full", "No-L1", "No-L2", "No-L3"]


def list_video_ids(data: dict[str, pd.DataFrame]) -> list[str]:
    windows = data["windows"]
    if windows.empty or "video_id" not in windows.columns:
        return []
    return sorted(windows["video_id"].astype(str).unique().tolist())


def run_one_config(
    video_id: str,
    data: dict[str, pd.DataFrame],
    config: str,
) -> dict:
    windows = filter_by_video(data["windows"], video_id)
    if windows.empty:
        return None

    l1_flags = filter_l1_flags(data["l1_flags"], data["windows"], video_id)
    l2_assignments = filter_by_video(data["l2_assignments"], video_id)
    l3_findings = filter_by_video(data["l3_findings"], video_id)

    try:
        l3_assessment = get_assessment_row(data["l3_assessments"], video_id)
    except ValueError:
        l3_assessment = dict(NEUTRAL_ASSESSMENT)

    # Apply ablation
    if config == "No-L1":
        l1_flags = pd.DataFrame()
    elif config == "No-L2":
        l2_assignments = pd.DataFrame()
    elif config == "No-L3":
        l3_findings = pd.DataFrame()
        l3_assessment = dict(NEUTRAL_ASSESSMENT)

    report = fuse_video(
        video_id=video_id,
        windows=windows,
        l1_flags=l1_flags,
        l2_assignments=l2_assignments,
        l3_findings=l3_findings,
        l3_assessment=l3_assessment,
    )

    return {
        "video_id": video_id,
        "config": config,
        "tier": report.overall.quality_tier,
        "reason": " | ".join(report.overall.reasoning),
        "l1_total": report.l1.total_flags,
        "l3_findings": report.l3_findings.total_findings,
        "top_severity": report.l3_findings.top_severity or "",
    }


def main() -> int:
    data = load_inputs(PROCESSED_DIR)
    video_ids = list_video_ids(data)
    if not video_ids:
        print("No videos found in windows.csv; abort.")
        return 1

    rows = []
    for video_id in video_ids:
        for config in CONFIGS:
            result = run_one_config(video_id, data, config)
            if result is None:
                continue
            rows.append(result)

    df = pd.DataFrame(rows)
    df.to_csv(OUTPUT_CSV, index=False)
    print(f"Wrote {OUTPUT_CSV} ({len(df)} rows = {df['video_id'].nunique()} videos x 4 configs)")
    print()

    print("=" * 68)
    print("Tier distribution per config (across 57 videos)")
    print("=" * 68)
    tier_table = (
        df.groupby(["config", "tier"]).size().unstack(fill_value=0).reindex(CONFIGS)
    )
    for col in ["good", "acceptable", "poor"]:
        if col not in tier_table.columns:
            tier_table[col] = 0
    tier_table = tier_table[["good", "acceptable", "poor"]]
    print(tier_table.to_string())
    print()

    print("=" * 68)
    print("Average L1 flags / L3 findings per video by config")
    print("=" * 68)
    metrics = df.groupby("config").agg(
        mean_l1_flags=("l1_total", "mean"),
        mean_l3_findings=("l3_findings", "mean"),
    ).reindex(CONFIGS).round(2)
    print(metrics.to_string())
    print()

    print("=" * 68)
    print("Reason distribution per config")
    print("=" * 68)
    for cfg in CONFIGS:
        sub = df[df["config"] == cfg]
        counts = Counter(sub["reason"])
        print(f"\n[{cfg}]")
        for reason, count in counts.most_common():
            print(f"  {count:>3}  {reason}")

    print()
    print("=" * 68)
    print("Tier change vs Full (per ablation)")
    print("=" * 68)
    full = df[df["config"] == "Full"][["video_id", "tier"]].rename(
        columns={"tier": "tier_full"}
    )
    for cfg in ["No-L1", "No-L2", "No-L3"]:
        sub = df[df["config"] == cfg][["video_id", "tier"]].rename(
            columns={"tier": f"tier_{cfg}"}
        )
        merged = full.merge(sub, on="video_id")
        changed = merged[merged["tier_full"] != merged[f"tier_{cfg}"]]
        print(f"\n[{cfg}] tier changed for {len(changed)} / {len(merged)} videos")
        if not changed.empty:
            print(changed.to_string(index=False))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
