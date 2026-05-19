from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.preprocessing.window_splitter import split_windows_from_data

PROCESSED_DIR = ROOT / "data" / "heldout" / "bupa" / "processed"
TRANSCRIPT_DIR = (
    ROOT
    / "data"
    / "heldout"
    / "bupa"
    / "raw"
    / "transcribe-output"
    / "web-health-information-bupa"
)

MANIFEST_CSV = PROCESSED_DIR / "manifest.csv"

PROJECT_KEY = "web-health-information-bupa"


def read_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def find_transcript_json(row: pd.Series, transcript_dir: Path) -> Path:
    candidate = ROOT / str(row.get("transcript_json_path", ""))
    if candidate.exists():
        return candidate

    tester_name = str(row["tester_name"]).strip()
    pattern = f"{tester_name}__{PROJECT_KEY}__transcript.json"
    path = transcript_dir / pattern

    if not path.exists():
        raise FileNotFoundError(f"Missing transcript JSON: {path}")

    return path


def parse_transcript(json_path: Path) -> str:
    data = read_json(json_path)
    transcripts = data.get("results", {}).get("transcripts", [])
    return " ".join(t.get("transcript", "") for t in transcripts).strip()


def parse_items(json_path: Path, row: pd.Series) -> pd.DataFrame:
    data = read_json(json_path)
    rows = []

    tester_name = str(row["tester_name"]).strip()
    video_filename = str(row["video_filename"]).strip()

    for i, item in enumerate(data.get("results", {}).get("items", [])):
        alternatives = item.get("alternatives", [])
        first_alt = alternatives[0] if alternatives else {}

        row = {
            "item_id": str(i),
            "content": first_alt.get("content"),
            "type": item.get("type"),
            "start_time": None,
            "end_time": None,
            "confidence": None,
            "project": PROJECT_KEY,
            "video_filename": video_filename,
            "tester_name": tester_name,
        }

        if item.get("type") == "pronunciation":
            row["start_time"] = (
                float(item.get("start_time", 0)) if item.get("start_time") else None
            )
            row["end_time"] = (
                float(item.get("end_time", 0)) if item.get("end_time") else None
            )
            confidence = first_alt.get("confidence")
            row["confidence"] = float(confidence) if confidence is not None else None

        rows.append(row)

    return pd.DataFrame(rows)


def parse_segments(json_path: Path, row: pd.Series) -> pd.DataFrame:
    data = read_json(json_path)
    rows = []

    tester_name = str(row["tester_name"]).strip()
    video_filename = str(row["video_filename"]).strip()

    for i, seg in enumerate(data.get("results", {}).get("audio_segments", [])):
        rows.append(
            {
                "segment_id": str(i),
                "transcript": seg.get("transcript", ""),
                "start_time": float(seg.get("start_time", 0)),
                "end_time": float(seg.get("end_time", 0)),
                "item_ids": ",".join(map(str, seg.get("items", [])))
                if seg.get("items")
                else "",
                "project": PROJECT_KEY,
                "video_filename": video_filename,
                "tester_name": tester_name,
            }
        )

    return pd.DataFrame(rows)


def build_windows(
    segments_df: pd.DataFrame,
    items_df: pd.DataFrame,
    manifest: pd.DataFrame,
) -> pd.DataFrame:
    windows = split_windows_from_data(
        segments_df.fillna("").astype(str).to_dict("records"),
        items_df.fillna("").astype(str).to_dict("records"),
    )
    windows_df = pd.DataFrame(windows)
    if windows_df.empty:
        return windows_df

    manifest_video_ids = {
        str(row["tester_name"]).strip(): str(row["video_id"]).strip()
        for _, row in manifest.iterrows()
    }

    def rewrite_window_id(row: pd.Series) -> str:
        tester_name = str(row["tester_name"]).strip()
        manifest_video_id = manifest_video_ids[tester_name]
        suffix = str(row["window_id"]).rsplit("_w", 1)[-1]
        return f"{manifest_video_id}_w{suffix}"

    windows_df["video_id"] = windows_df["tester_name"].map(manifest_video_ids)
    windows_df["window_id"] = windows_df.apply(rewrite_window_id, axis=1)

    return windows_df[
        [
            "window_id",
            "video_id",
            "start_time",
            "end_time",
            "duration",
            "text",
            "word_count",
            "segment_ids",
            "project",
            "video_filename",
            "tester_name",
        ]
    ]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build manifest-aware Bupa held-out processed transcript inputs."
    )
    parser.add_argument("--manifest", default=str(MANIFEST_CSV))
    parser.add_argument("--transcript-dir", default=str(TRANSCRIPT_DIR))
    parser.add_argument("--output-dir", default=str(PROCESSED_DIR))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    manifest_csv = Path(args.manifest)
    transcript_dir = Path(args.transcript_dir)
    output_dir = Path(args.output_dir)

    if not manifest_csv.exists():
        raise FileNotFoundError(f"Missing manifest: {manifest_csv}")

    manifest = pd.read_csv(manifest_csv)

    required_columns = {"tester_name", "video_id", "video_filename"}
    missing = required_columns - set(manifest.columns)
    if missing:
        raise ValueError(f"manifest.csv missing required columns: {sorted(missing)}")

    output_dir.mkdir(parents=True, exist_ok=True)

    transcript_rows = []
    all_items = []
    all_segments = []

    for _, row in manifest.iterrows():
        tester_name = str(row["tester_name"]).strip()
        video_id = str(row["video_id"]).strip()
        video_filename = str(row["video_filename"]).strip()
        json_path = find_transcript_json(row, transcript_dir)

        transcript_rows.append(
            {
                "project": PROJECT_KEY,
                "video_filename": video_filename,
                "tester_name": tester_name,
                "video_id": video_id,
                "transcript_json": str(json_path.relative_to(ROOT)),
                "transcript": parse_transcript(json_path),
            }
        )

        all_items.append(parse_items(json_path, row))
        all_segments.append(parse_segments(json_path, row))

    transcripts_df = pd.DataFrame(transcript_rows)
    items_df = pd.concat(all_items, ignore_index=True) if all_items else pd.DataFrame()
    segments_df = (
        pd.concat(all_segments, ignore_index=True) if all_segments else pd.DataFrame()
    )
    windows_df = build_windows(segments_df, items_df, manifest)

    transcripts_df.to_csv(output_dir / "transcripts.csv", index=False)
    items_df.to_csv(output_dir / "items.csv", index=False)
    segments_df.to_csv(output_dir / "segments.csv", index=False)
    windows_df.to_csv(output_dir / "windows.csv", index=False)

    print("Bupa processed inputs generated:")
    print(f"- transcripts: {len(transcripts_df)} rows")
    print(f"- items: {len(items_df)} rows")
    print(f"- segments: {len(segments_df)} rows")
    print(f"- windows: {len(windows_df)} rows")
    print(f"- output dir: {output_dir}")


if __name__ == "__main__":
    main()
