from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Select known Layer 3-A schema violation windows for smoke rerun."
    )
    parser.add_argument(
        "--results",
        default="outputs/layer3_dev_level_A_results.csv",
        help="Raw Layer 3-A results CSV containing schema_violation rows.",
    )
    parser.add_argument(
        "--windows",
        default="data/processed/windows.csv",
        help="Full windows.csv source.",
    )
    parser.add_argument(
        "--output",
        default="outputs/smoke_fix_verify_input.csv",
        help="Temporary windows subset CSV to write.",
    )
    parser.add_argument(
        "--prefix",
        action="append",
        default=["marychaunguyen_wa", "ghum_wa"],
        help="Window id prefix to sample from. Can be repeated.",
    )
    parser.add_argument("--per-prefix", type=int, default=5)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    results = pd.read_csv(args.results)
    windows = pd.read_csv(args.windows)

    violations = results[results["flag"] == "schema_violation"].copy()
    selected_ids: list[str] = []
    for prefix in args.prefix:
        block = violations[
            violations["window_id"].fillna("").astype(str).str.startswith(prefix)
        ]
        selected_ids.extend(block["window_id"].head(args.per_prefix).astype(str).tolist())

    if not selected_ids:
        raise SystemExit("No matching schema_violation window_ids found.")

    selected = windows[windows["window_id"].isin(selected_ids)].copy()
    selected["_order"] = selected["window_id"].map(
        {window_id: idx for idx, window_id in enumerate(selected_ids)}
    )
    selected = selected.sort_values("_order").drop(columns=["_order"])

    missing = [window_id for window_id in selected_ids if window_id not in set(selected["window_id"])]
    if missing:
        raise SystemExit(f"Selected ids missing from windows.csv: {missing}")

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    selected.to_csv(output, index=False)
    print(f"Wrote {len(selected)} rows to {output}")
    print(selected["window_id"].to_string(index=False))


if __name__ == "__main__":
    main()
