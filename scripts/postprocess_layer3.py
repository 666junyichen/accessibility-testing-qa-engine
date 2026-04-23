from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.layer3.postprocess import filter_failed_rows, unpack_level_a, unpack_level_b


def _default_input(level: str) -> Path:
    return ROOT / "outputs" / f"layer3_dev_level_{level}_results.csv"


def _default_output(level: str) -> Path:
    if level == "A":
        return ROOT / "data" / "processed" / "layer3_findings.csv"
    return ROOT / "data" / "processed" / "layer3_video_assessments.csv"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Postprocess Layer 3 raw outputs.")
    parser.add_argument("--level", choices=["A", "B"], required=True)
    parser.add_argument("--input", default=None)
    parser.add_argument(
        "--windows",
        default=str(ROOT / "data" / "processed" / "windows.csv"),
    )
    parser.add_argument("--output", default=None)
    return parser.parse_args()


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(name)s:%(message)s")
    args = parse_args()
    level = args.level

    input_path = Path(args.input) if args.input else _default_input(level)
    windows_path = Path(args.windows)
    output_path = Path(args.output) if args.output else _default_output(level)

    raw_df = pd.read_csv(input_path)
    windows_df = pd.read_csv(windows_path)
    ok_df, failed_df = filter_failed_rows(raw_df)

    if level == "A":
        flat_df = unpack_level_a(ok_df, windows_df)
    else:
        flat_df = unpack_level_b(ok_df, windows_df)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    flat_df.to_csv(output_path, index=False)
    logging.info(
        "Wrote %s rows x %s columns to %s (%s failed rows skipped)",
        flat_df.shape[0],
        flat_df.shape[1],
        output_path,
        len(failed_df),
    )


if __name__ == "__main__":
    main()
