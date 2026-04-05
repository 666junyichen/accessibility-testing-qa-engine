import json
import pandas as pd
from pathlib import Path


def parse_transcript(json_path):
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    transcripts = data["results"]["transcripts"]
    full_text = " ".join([t["transcript"] for t in transcripts])
    return full_text


def parse_items(json_path):
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    items_records = []

    for i, item in enumerate(data["results"].get("items", [])):
        record = {
            "item_id": i,
            "content": item["alternatives"][0]["content"],
            "type": item.get("type")
        }

        if item.get("type") == "pronunciation":
            record["start_time"] = float(item.get("start_time", 0))
            record["end_time"] = float(item.get("end_time", 0))
            record["confidence"] = float(item["alternatives"][0].get("confidence", 0))
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


def build_transcript_df(json_dir):
    records = []
    json_files = list(Path(json_dir).glob("*.json"))

    for file in json_files:
        transcript = parse_transcript(file)

        records.append({
            "video_filename": file.stem.replace("_video-job", ".mp4"),
            "tester_name": file.stem.split("_")[-2],
            "transcript": transcript
        })

    return pd.DataFrame(records)


def build_items_df(json_dir):
    all_items = []
    json_files = list(Path(json_dir).glob("*.json"))

    for file in json_files:
        items_df = parse_items(file)
        items_df["video_filename"] = file.stem.replace("_video-job", ".mp4")
        items_df["tester_name"] = file.stem.split("_")[-2]
        all_items.append(items_df)

    return pd.concat(all_items, ignore_index=True)


def build_segments_df(json_dir):
    all_segments = []
    json_files = list(Path(json_dir).glob("*.json"))

    for file in json_files:
        seg_df = parse_segments(file)
        seg_df["video_filename"] = file.stem.replace("_video-job", ".mp4")
        seg_df["tester_name"] = file.stem.split("_")[-2]
        all_segments.append(seg_df)

    return pd.concat(all_segments, ignore_index=True)


if __name__ == "__main__":
    json_dir = "data/raw"
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

    print("\nitems.csv preview:")
    print(items_df.head())

    print("\nsegments.csv preview:")
    print(segments_df.head())