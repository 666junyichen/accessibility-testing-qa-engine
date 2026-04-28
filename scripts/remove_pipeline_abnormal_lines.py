from __future__ import annotations

import shutil
from pathlib import Path

import pandas as pd


REPORT_DIR = Path("data/processed/reports")
EXCLUSION_CSV = REPORT_DIR / "dev_exclusion_candidates.csv"

SUMMARY_CSV = REPORT_DIR / "_summary.csv"
OFFICIAL_LIST_CSV = REPORT_DIR / "dev55_official_list.csv"
SUMMARY_DEV55_CSV = REPORT_DIR / "_summary_dev55.csv"
DEV55_DIR = REPORT_DIR / "dev55"


def main() -> None:
    if not SUMMARY_CSV.exists():
        raise FileNotFoundError(f"Missing summary file: {SUMMARY_CSV}")

    if not EXCLUSION_CSV.exists():
        raise FileNotFoundError(f"Missing exclusion file: {EXCLUSION_CSV}")

    summary_df = pd.read_csv(SUMMARY_CSV)
    exclusion_df = pd.read_csv(EXCLUSION_CSV)

    if "video_id" not in summary_df.columns:
        raise ValueError("_summary.csv must contain 'video_id' column")

    if "video_id" not in exclusion_df.columns:
        raise ValueError("dev_exclusion_candidates.csv must contain 'video_id' column")

    excluded_ids = set(
        exclusion_df["video_id"]
        .dropna()
        .astype(str)
        .str.strip()
        .tolist()
    )

    dev55_df = summary_df[
        ~summary_df["video_id"].astype(str).str.strip().isin(excluded_ids)
    ].copy()

    # official list: only keep video_id and project
    keep_cols = [col for col in ["video_id", "project"] if col in dev55_df.columns]
    official_list_df = dev55_df[keep_cols].copy()

    OFFICIAL_LIST_CSV.parent.mkdir(parents=True, exist_ok=True)
    official_list_df.to_csv(OFFICIAL_LIST_CSV, index=False)
    dev55_df.to_csv(SUMMARY_DEV55_CSV, index=False)

    # copy official JSON reports
    if DEV55_DIR.exists():
        shutil.rmtree(DEV55_DIR)
    DEV55_DIR.mkdir(parents=True, exist_ok=True)

    copied = 0
    missing_json = []

    for video_id in official_list_df["video_id"].astype(str):
        src = REPORT_DIR / f"{video_id}.json"
        dst = DEV55_DIR / f"{video_id}.json"

        if src.exists():
            shutil.copy2(src, dst)
            copied += 1
        else:
            missing_json.append(video_id)

    print("Official dev set created.")
    print(f"Original summary rows: {len(summary_df)}")
    print(f"Excluded rows: {len(excluded_ids)}")
    print(f"Official rows: {len(dev55_df)}")
    print(f"JSON reports copied: {copied}")
    print(f"Official list: {OFFICIAL_LIST_CSV}")
    print(f"Dev55 summary: {SUMMARY_DEV55_CSV}")
    print(f"Dev55 report dir: {DEV55_DIR}")

    if missing_json:
        print("Missing JSON reports:")
        for video_id in missing_json:
            print(f"  - {video_id}")


if __name__ == "__main__":
    main()