from pathlib import Path
import pandas as pd

report_dir = Path("data/processed/reports")
summary = pd.read_csv(report_dir / "_summary.csv")

# filter out potentially abnormal rows
candidates = summary[
    (summary["windows"] == 0)
    | (summary["l3_findings"] == 0)
    | (summary["narration"].isna())
    | (summary["recording"].isna())
    | (summary["tier"].isna())
].copy()

candidates.to_csv(report_dir / "dev_exclusion_candidates.csv", index=False)

print(candidates[["video_id", "windows", "l3_findings", "narration", "recording", "tier"]])
print("Candidate count:", len(candidates))