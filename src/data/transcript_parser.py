import json
import pandas as pd
from pathlib import Path


def parse_transcript(json_path):
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    transcripts = data["results"].get("transcripts", [])
    full_text = " ".join([t.get("transcript", "") for t in transcripts]).strip()
    return full_text


def parse_items(json_path):
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    items_records = []

    for i, item in enumerate(data["results"].get("items", [])):
        alternatives = item.get("alternatives", [])
        first_alt = alternatives[0] if alternatives else {}

        record = {
            "item_id": i,
            "content": first_alt.get("content"),
            "type": item.get("type")
        }

        if item.get("type") == "pronunciation":
            record["start_time"] = float(item.get("start_time", 0)) if item.get("start_time") else None
            record["end_time"] = float(item.get("end_time", 0)) if item.get("end_time") else None
            record["confidence"] = float(first_alt.get("confidence", 0)) if first_alt.get("confidence") else None
        else:
            record["start_time"] = None
            record["end_time"] = None
            record["confidence"] = None

        items_records.append(record)

    return pd.DataFrame(items_records)


def parse_segments(json_path):
    transcript = parse_transcript(json_path)

    segments = []
    sentences = transcript.split(".")

    for i, sentence in enumerate(sentences):
        sentence = sentence.strip()
        if sentence:
            segments.append({
                "segment_id": i,
                "transcript": sentence
            })

    return pd.DataFrame(segments)


def extract_metadata(file_path):
    """
    从路径和文件名提取 metadata
    例子:
    data/raw/transcribe-output/department-of-premier-and-cabinet-wa/project_xxx_ghum_video-job.json
    """
    file_path = Path(file_path)

    project = file_path.parent.name
    video_filename = file_path.stem.replace("_video-job", ".mp4")
    tester_name = file_path.stem.split("_")[-2]

    return {
        "project": project,
        "video_filename": video_filename,
        "tester_name": tester_name
    }


def build_transcript_df(json_dir):
    records = []
    json_files = list(Path(json_dir).rglob("*.json"))

    for file in json_files:
        transcript = parse_transcript(file)
        meta = extract_metadata(file)

        records.append({
            "project": meta["project"],
            "video_filename": meta["video_filename"],
            "tester_name": meta["tester_name"],
            "transcript": transcript
        })

    return pd.DataFrame(records)


def build_items_df(json_dir):
    all_items = []
    json_files = list(Path(json_dir).rglob("*.json"))

    for file in json_files:
        items_df = parse_items(file)
        meta = extract_metadata(file)

        if not items_df.empty:
            items_df["project"] = meta["project"]
            items_df["video_filename"] = meta["video_filename"]
            items_df["tester_name"] = meta["tester_name"]
            all_items.append(items_df)

    if all_items:
        return pd.concat(all_items, ignore_index=True)
    else:
        return pd.DataFrame(columns=[
            "item_id", "content", "type", "start_time", "end_time",
            "confidence", "project", "video_filename", "tester_name"
        ])


def build_segments_df(json_dir):
    all_segments = []
    json_files = list(Path(json_dir).rglob("*.json"))

    for file in json_files:
        seg_df = parse_segments(file)
        meta = extract_metadata(file)

        if not seg_df.empty:
            seg_df["project"] = meta["project"]
            seg_df["video_filename"] = meta["video_filename"]
            seg_df["tester_name"] = meta["tester_name"]
            all_segments.append(seg_df)

    if all_segments:
        return pd.concat(all_segments, ignore_index=True)
    else:
        return pd.DataFrame(columns=[
            "segment_id", "transcript", "project", "video_filename", "tester_name"
        ])


if __name__ == "__main__":
    json_dir = "data/raw/transcribe-output"
    output_dir = Path("data/processed")
    output_dir.mkdir(parents=True, exist_ok=True)

    transcripts_df = build_transcript_df(json_dir)
    items_df = build_items_df(json_dir)
    segments_df = build_segments_df(json_dir)

    transcripts_df.to_csv(output_dir / "transcripts.csv", index=False)
    items_df.to_csv(output_dir / "items.csv", index=False)
    segments_df.to_csv(output_dir / "segments.csv", index=False)

    print("transcripts.csv preview:")
    print(transcripts_df.head())
    print(f"\ntranscripts rows: {len(transcripts_df)}")

    print("\nitems.csv preview:")
    print(items_df.head())
    print(f"\nitems rows: {len(items_df)}")

    print("\nsegments.csv preview:")
    print(segments_df.head())
    print(f"\nsegments rows: {len(segments_df)}")