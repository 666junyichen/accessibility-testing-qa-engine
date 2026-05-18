from __future__ import annotations

import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]

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
WINDOW_SECONDS = 60.0


def read_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def find_transcript_json(tester_name: str) -> Path:
    pattern = f"{tester_name}__{PROJECT_KEY}__transcript.json"
    path = TRANSCRIPT_DIR / pattern

    if not path.exists():
        raise FileNotFoundError(f"Missing transcript JSON: {path}")

    return path


def parse_transcript(json_path: Path) -> str:
    data = read_json(json_path)
    transcripts = data.get("results", {}).get("transcripts", [])
    return " ".join(t.get("transcript", "") for t in transcripts).strip()


def parse_items(json_path: Path, video_id: str, tester_name: str) -> pd.DataFrame:
    data = read_json(json_path)
    rows = []

    for i, item in enumerate(data.get("results", {}).get("items", [])):
        alternatives = item.get("alternatives", [])
        first_alt = alternatives[0] if alternatives else {}

        row = {
            "video_id": video_id,
            "project": PROJECT_KEY,
            "tester_name": tester_name,
            "item_id": f"{video_id}_item_{i:05d}",
            "item_index": i,
            "content": first_alt.get("content", ""),
            "type": item.get("type", ""),
            "start_time": None,
            "end_time": None,
            "confidence": None,
        }

        if item.get("type") == "pronunciation":
            row["start_time"] = float(item.get("start_time", 0))
            row["end_time"] = float(item.get("end_time", 0))
            confidence = first_alt.get("confidence")
            row["confidence"] = float(confidence) if confidence is not None else None

        rows.append(row)

    return pd.DataFrame(rows)


def parse_segments(json_path: Path, video_id: str, tester_name: str) -> pd.DataFrame:
    data = read_json(json_path)
    rows = []

    for i, seg in enumerate(data.get("results", {}).get("audio_segments", [])):
        rows.append(
            {
                "video_id": video_id,
                "project": PROJECT_KEY,
                "tester_name": tester_name,
                "segment_id": f"{video_id}_seg_{i:05d}",
                "segment_index": i,
                "transcript": seg.get("transcript", ""),
                "start_time": float(seg.get("start_time", 0)),
                "end_time": float(seg.get("end_time", 0)),
                "item_ids": ",".join(map(str, seg.get("items", [])))
                if seg.get("items")
                else "",
            }
        )

    return pd.DataFrame(rows)


def build_windows_from_segments(segments: pd.DataFrame) -> pd.DataFrame:
    rows = []

    if segments.empty:
        return pd.DataFrame(
            columns=[
                "window_id",
                "video_id",
                "project",
                "tester_name",
                "start_time",
                "end_time",
                "text",
            ]
        )

    for video_id, block in segments.groupby("video_id", sort=False):
        block = block.sort_values("start_time").copy()

        project = str(block.iloc[0]["project"])
        tester_name = str(block.iloc[0]["tester_name"])

        max_end = float(block["end_time"].max())
        n_windows = max(1, int(max_end // WINDOW_SECONDS) + 1)

        for window_index in range(n_windows):
            start = window_index * WINDOW_SECONDS
            end = start + WINDOW_SECONDS

            sub = block[
                (block["start_time"] < end)
                & (block["end_time"] >= start)
            ]

            text = " ".join(
                sub["transcript"]
                .fillna("")
                .astype(str)
                .str.strip()
                .tolist()
            ).strip()

            rows.append(
                {
                    "window_id": f"{video_id}_w{window_index:03d}",
                    "video_id": video_id,
                    "project": project,
                    "tester_name": tester_name,
                    "start_time": start,
                    "end_time": min(end, max_end),
                    "text": text,
                }
            )

    return pd.DataFrame(rows)


def main() -> None:
    if not MANIFEST_CSV.exists():
        raise FileNotFoundError(f"Missing manifest: {MANIFEST_CSV}")

    manifest = pd.read_csv(MANIFEST_CSV)

    if "tester_name" not in manifest.columns:
        raise ValueError("manifest.csv must contain tester_name column")

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    transcript_rows = []
    all_items = []
    all_segments = []

    for _, row in manifest.iterrows():
        tester_name = str(row["tester_name"]).strip()

        # Use tester_project format for Bupa video_id
        video_id = f"{tester_name}_bupa"

        json_path = find_transcript_json(tester_name)

        transcript_rows.append(
            {
                "video_id": video_id,
                "project": PROJECT_KEY,
                "tester_name": tester_name,
                "transcript_json": str(json_path.relative_to(ROOT)),
                "transcript": parse_transcript(json_path),
            }
        )

        all_items.append(parse_items(json_path, video_id, tester_name))
        all_segments.append(parse_segments(json_path, video_id, tester_name))

    transcripts_df = pd.DataFrame(transcript_rows)
    items_df = pd.concat(all_items, ignore_index=True) if all_items else pd.DataFrame()
    segments_df = (
        pd.concat(all_segments, ignore_index=True) if all_segments else pd.DataFrame()
    )
    windows_df = build_windows_from_segments(segments_df)

    transcripts_df.to_csv(PROCESSED_DIR / "transcripts.csv", index=False)
    items_df.to_csv(PROCESSED_DIR / "items.csv", index=False)
    segments_df.to_csv(PROCESSED_DIR / "segments.csv", index=False)
    windows_df.to_csv(PROCESSED_DIR / "windows.csv", index=False)

    print("Bupa processed inputs generated:")
    print(f"- transcripts: {len(transcripts_df)} rows")
    print(f"- items: {len(items_df)} rows")
    print(f"- segments: {len(segments_df)} rows")
    print(f"- windows: {len(windows_df)} rows")
    print(f"- output dir: {PROCESSED_DIR}")


if __name__ == "__main__":
    main()