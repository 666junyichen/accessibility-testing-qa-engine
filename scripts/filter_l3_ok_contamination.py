from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Drop positive-only findings from existing Layer 3-A ok rows."
    )
    parser.add_argument("--input", default="outputs/layer3_dev_level_A_results.csv")
    parser.add_argument(
        "--output",
        default="outputs/layer3_dev_level_A_results_filtered.csv",
    )
    return parser.parse_args()


def _is_positive_only_contamination(finding: dict) -> bool:
    return (
        finding.get("sentiment_e") in {"E1", "E2"}
        and finding.get("severity_s") in {"S5", "S6"}
        and finding.get("calibrator_score_l") in {"L1", "L2"}
    )


def filter_ok_contamination(df: pd.DataFrame) -> tuple[pd.DataFrame, int]:
    filtered = df.copy()
    dropped_total = 0

    for idx, row in filtered.iterrows():
        if row.get("flag") != "ok":
            continue

        output = json.loads(row["output_json"])
        findings = output.get("findings", [])
        kept = [
            finding
            for finding in findings
            if not _is_positive_only_contamination(finding)
        ]
        dropped = len(findings) - len(kept)
        if dropped:
            dropped_total += dropped
            output["findings"] = kept
            filtered.at[idx, "output_json"] = json.dumps(output, separators=(",", ":"))

    return filtered, dropped_total


def main() -> None:
    args = parse_args()
    source = pd.read_csv(args.input)
    filtered, dropped_total = filter_ok_contamination(source)

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    filtered.to_csv(output, index=False)

    print(f"input_rows={len(source)}")
    print(f"output_rows={len(filtered)}")
    print(f"findings_dropped={dropped_total}")
    print(f"output={output}")


if __name__ == "__main__":
    main()
